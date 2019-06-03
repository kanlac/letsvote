from flask import render_template, flash, url_for, session, redirect, request, jsonify
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user
from .. import db

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit(): # 针对 POST 请求，即点击 Submit 后
		user = User.query.filter_by(username=form.username.data).first() # 查看数据库中是否有这个用户名
		if user is None: # 没有，提示错误，请注册
			flash("User doesn't exist.")
		elif user.verify_password(form.password.data): # 有则判断输入密码是否正确
			login_user(user, form.remember_me.data) # 传入 BooleanField 实例表示是否要记住该用户
			return redirect(url_for('ques.square'))
		else:
			flash("Password is wrong.")
	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('ques.square'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You can now login.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)
