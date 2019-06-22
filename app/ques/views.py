import os, json, errno, fcntl, os, signal, time, random, pyqrcode, sys
from flask import render_template, request, Response, current_app as app, abort, redirect, url_for, flash, send_from_directory, make_response
from collections import defaultdict
from functools import wraps
from datetime import datetime
from copy import deepcopy
from flask_login import login_required, current_user
from pathlib import Path

from . import ques


@ques.route('/', methods=['GET', 'POST'])
def square():
	print(f"request {request.cookies.get('index')}")
	dir_ = _get_option('DIR')
	qs = map(lambda s: (s[:-5], _get_questionnaire_data(s[:-5])),
			 filter(lambda s: not s.startswith('_') and s.endswith('.json'),
					os.listdir(dir_)))
	return render_template('index.html', questionnaires=qs)


@ques.route('/delete/<slug>')
@login_required
def delete(slug):
	questionnaire = _get_questionnaire_data(slug)
	if questionnaire['creator'] != current_user.username:
		flash('You are not granted.')
	else:
		q_file = os.path.join(_get_option('DIR'), slug + '.json')
		qrcode_file = os.path.join(_get_option('QRCODE_DIR'), slug + '.png')
		os.remove(q_file)
		os.remove(qrcode_file)
		flash('成功删除问卷。')

	return redirect(url_for('ques.square'))


@ques.route('/<slug>', methods=['GET', 'POST'])
def questionnaire(slug):
	data = _get_questionnaire_data(slug)

	if request.method == 'GET':
		return render_template('questionnaire.html', questionnaire=data, slug=slug)

	if request.cookies.get(slug) == 'voted':
		flash('请勿重复提交喔 😯')
		return redirect(url_for('ques.square'))

	form = request.form
	print(f"form: {form}")
	result_file_path = os.path.join(_get_option('RESULTS_DIR'), slug+'.json')

	assert(Path(result_file_path).is_file())
	signal.signal(signal.SIGALRM, handler)
	signal.alarm(5)

	fd = os.open(result_file_path, os.O_RDWR) # 返回值是 int 类型的 file descriptor
	fcntl.flock(fd, fcntl.LOCK_EX)

	result_dict = defaultdict(lambda: tuple(None, None))
	result_str = os.read(fd, 100000).decode("utf-8")
	result_dict = json.loads(result_str)
	if result_dict['total'] == 0:
		result_dict['total'] = 1
		q_list = list()
		for question in data.get('questions', []): # 对问卷表里的每个问题，全部存到 q_list 然后赋给 result_dict['questions']
			q = dict()
			q['label'] = question['label']
			q['type'] = question['type']

			if q['type'] == 'text': # 文本题
				t_list = list()
				t_list.append(form[q['label']])
				q['texts'] = t_list
			else:  # 选择题
				if form[q['label']] == 'Other': # 如果选的是 Other，把文本添加到 other_options
					q['other_options'] = [form['other_option']]
				o_list = list()
				for option in question['options']:
					o = dict()
					o['option'] = option
					# count & percentage
					if option in form[q['label']]:
						o['count'] = 1
						if q['type'] == 'radio':
							o['percentage'] = 100
					else:
						o['count'] = 0
						if q['type'] == 'radio':
							o['percentage'] = 0
					o_list.append(o)
				q['result'] = o_list
			q_list.append(q)

		result_dict['questions'] = q_list
	else:
		result_dict['total'] = result_dict['total']+1
		# 加入文本，选择项的 count++，所有项的 percentage 清空
		for q in result_dict['questions']:
			if 'texts' in q: # 文本题
				if form[q['label']] != '':
					q['texts'].append(form[q['label']])
			elif 'result' in q: # 选择题
				for r in q['result']:
					if r['option'] in form[q['label']]:
						r['count'] = r['count']+1
					if 'percentage' in r:
						r['percentage'] = 0 # 全部选项的百分比先归零
				# 如果选的是 Other，要把文本添加到 other_options
				if form[q['label']] == 'Other':
					q['other_options'].append(form['other_option'])
			else:
				raise Error('No matching question type in result json.')
		# 更新单选问题的百分比（count/total）
		for q in result_dict['questions']:
			if q['type'] == 'radio':
				for r in q['result']:
					r['percentage'] = format(int(r['count']) / int(result_dict['total']) * 100, '0.2f')

	os.lseek(fd, 0, os.SEEK_SET) # 指针位置指向开头
	os.write(fd, bytes(json.dumps(result_dict, indent=4, ensure_ascii=False), 'utf8'))
	cur_pos = os.lseek(fd, 0, os.SEEK_CUR)
	os.truncate(fd, cur_pos)
	fcntl.flock(fd, fcntl.LOCK_UN)
	os.close(fd)
	signal.alarm(0)

	resp = make_response(redirect(url_for('ques.square')))
	resp.set_cookie(slug, 'voted')
	flash('谢谢参与！')
	return resp


@ques.route('/results/<slug>', methods=['GET'])
@login_required
def results(slug):
	form = _get_questionnaire_data(slug)
	if current_user.username != form.get('creator'):
		flash("You aren't the owner of this questionnaire.")
		return redirect(url_for('ques.square'))

	return render_template("results.html", questionnaire=form, results=_get_results(slug))


@ques.route('/originate', methods=['GET', 'POST'])
@login_required
def originate():
	if request.method == 'POST':
		questionnaire = defaultdict(lambda: tuple(None, None))
		questionnaire['questions'] = list()
		questionnaire['creator'] = current_user.username
		log_list = list()
		q_dict = dict()
		opt = list()
		print(f'request.form: {request.form}')
		print(f"test: {request.form.getlist('q1-option_item')}")
		for item in request.form.items():
			print(f'---\nitem: {item}')
			print(f'q_dict: {q_dict}')
			print(f'log_list: {log_list}')
			key = item[0]
			value = item[1]
			print(f'key: {key}, value: {value}')
			if key == 'title':
				questionnaire['title'] = value
			elif key == 'slug':
				questionnaire['slug'] = value
			elif key == 'comment':
				questionnaire['comment'] = value
			elif key.startswith('q'):
				id_log = key[0:].split('-')[0];
				print(f'id_log: {id_log}')
				k = key.split('-')[1]
				if id_log in log_list: # 已记录的问题
					if k == 'label' or k == 'desc':
						print(f'k: {k}')
						print(f'q_dict: {q_dict}')
						q_dict[k] = value
					elif k == 'option_item':
						c_key = id_log + '-option_item'
						for o in request.form.getlist(c_key):
							opt.append(o)
					elif k == 'allow_other':
						opt.append('Other')
						q_dict['other_options'] = ''
					elif k == 'is_mandatory':
						q_dict['required'] = True
				else: # 新的问题
					assert (k == 'type'), "The first key of a question should be qXX-type"
					log_list.append(id_log)
					if q_dict: # save and clear out q_dict
						print('save q_dict...')
						if 'type' in q_dict and q_dict['type'] != 'text':
							q_dict['options'] = opt.copy()
						questionnaire['questions'].append(q_dict.copy())
						q_dict.clear()
						opt.clear()

					q_dict[k] = value

			print('---\n')

		if q_dict['type'] == "radio" or q_dict['type'] == "checkbox":
			q_dict['options'] = opt.copy()
		questionnaire['questions'].append(q_dict.copy())

		slug = questionnaire['slug']
		q_path = os.path.join(_get_option('DIR'), slug+'.json')
		if os.path.exists(q_path):
			slug = questionnaire['slug'] + str(random.randint(100, 999))
			q_path = os.path.join(_get_option('DIR'), slug+'.json')

		# 创建并存储 qrcode
		url = _get_option('SITE_BASE') + slug
		qrcode = pyqrcode.create(url)
		qrcode_dir = os.path.join(_get_option('QRCODE_DIR'))
		if not (os.path.isdir(qrcode_dir)):
			try:
				os.mkdir(qrcode_dir)
			except OSError:
				print(f"Create qrcode directory failed.")
		qrcode.png(slug + '.png', scale=4)
		os.rename(os.getcwd() + '/' + slug + '.png', qrcode_dir + '/' + slug + '.png')

		with open(q_path, 'w', encoding='utf8') as f:
			json.dump(questionnaire, f, indent=4, ensure_ascii=False)
		init_result(slug)
		flash('成功创建问卷！扫描二维码或分发本页面 URL 即可让用户参与本问卷调查。')
		return redirect(url_for('ques.questionnaire', slug=slug))

	return render_template('originate.html')


@ques.route('/qrcode/<path:filename>')
def get_qrcode(filename):
    return send_from_directory(load_config('QUESTIONNAIRE_QRCODE_DIR'), filename, as_attachment=True)


def init_result(slug):
	r_path = os.path.join(_get_option('RESULTS_DIR'), slug+'.json')
	r_dict = {'total': 0}
	with open(r_path, 'w', encoding='utf8') as f:
		json.dump(r_dict, f, indent=4, ensure_ascii=False)
	return None


def _merge_objects(obj1, obj2):
	"""Recursive merge obj2 into obj1. Objects can be dicts and lists."""
	if type(obj1) == list:
		obj1.extend(obj2)
		return obj1
	for k2, v2 in obj2.items():
		v1 = obj1.get(k2)
		if type(v2) == type(v1) in (dict, list):
			_merge_objects(v1, v2)
		else:
			obj1[k2] = v2
	return obj1


def _get_option(opt, val=None):
	opt = 'QUESTIONNAIRE_' + opt
	try:
		val = app.config[opt]
	except KeyError:
		if val is None:
			abort(500, "%s is not configured" % opt)
	return val


def load_config(opt):
	val = None
	try:
		val = app.config[opt]
	except:
		if val is None:
			abort(400, "%s is not configured." % opt)
	return val


def _get_defaults():
	return _merge_objects(deepcopy(app.config['QUESTIONNAIRE_DEFAULTS']),
						  _get_option('DEFAULTS', {}))


def _get_questionnaire_data(slug):
	return __get_questionnaire_data(slug)


def __get_questionnaire_data(slug):
	"""Read questionnaire data from the file pointed by slug."""
	qfile = os.path.join(_get_option('DIR'), slug + '.json')
	try:
		with open(qfile) as f:
			data = json.load(f)
			if not isinstance(data, dict):
				raise ValueError('json top level structure must be object')
	except (TypeError, ValueError, OverflowError) as e:
		app.logger.exception('parse error: %s: %s', qfile, e)
		abort(500, "error in %s" % slug)
	except EnvironmentError as e:
		app.logger.info('I/O error: %s: %s', qfile, e)
		abort(404, "Questionnaire not found: %s" % slug)
	if 'extends' in data:
		data = _merge_objects(__get_questionnaire_data(data['extends']), data)
	else:
		data = _merge_objects(_get_defaults(), data) # 加载 ques.__init__ 中的参数
	return data


# deprecated
def _get_submissions(slug):
	sdir = os.path.join(_get_option('SUBMISSIONS_DIR'), slug) # 在这里已经进入了单个问卷结果目录
	submissions = {}
	try:
		dirlist = os.listdir(sdir)
	except EnvironmentError as e:
		if e.errno != errno.ENOENT:
			raise
		dirlist = []
	for subm in filter(lambda s: s.endswith('.json'), dirlist): # subm 是 .json 文件
			with open(os.path.join(sdir, subm)) as f:
				data = json.load(f)
				data = dict((
					(int(i), [tuple(v) for v in vs])
					for i, vs in data.items()
				))
				dt = datetime.strptime(subm[:-5], app.config['SUBMISSION_DATEFMT']) # dt 即是文件名
				submissions[dt] = data
	return submissions # 返回的是一个 json 文件类型的数组


# new method
def _get_results(slug):
	file_dir = os.path.join(_get_option('RESULTS_DIR'), slug+".json")
	if Path(file_dir).is_file():
		with open(file_dir) as f:
			return json.load(f)
	return None




def _write_submission(data, slug):
	sdir = os.path.join(_get_option('SUBMISSIONS_DIR'), slug)
	try:
		os.makedirs(sdir)
	except OSError:
		pass
	timestamp = datetime.now().strftime(app.config['SUBMISSION_DATEFMT'])
	sfile = os.path.join(sdir, timestamp + '.json')
	with open(sfile, 'w', encoding='utf8') as f:
		json.dump(data, f, indent=4, ensure_ascii=False)

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    raise OSError("Couldn't open device!")

# HTTP Basic Auth
# http://flask.pocoo.org/snippets/8/

def check_auth(username, password):
	"""This function is called to check if a username /
	password combination is valid.
	"""
	return _get_option('BASIC_AUTH') == (username, password)


def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})
