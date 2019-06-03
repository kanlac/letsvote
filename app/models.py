from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
	__tablename__ = 'User'

	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def __repr__(self): # debug 有效
		return '<User %r>' % self.username

	def get_id(self): # flask-login 回调函数只能识别名字'id'，因此这里需要手动定义
		return (self.user_id)


# flask-login 的回调函数
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
