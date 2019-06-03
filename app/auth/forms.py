from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Regexp, EqualTo

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Keep me logged in') # 「记住我」
	submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
	password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confirm password', validators=[DataRequired()])
	submit = SubmitField('Register')
