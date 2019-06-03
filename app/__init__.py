from flask import Flask
from flask_bootstrap import Bootstrap
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


# Factory Function
def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])

	bootstrap.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)
	from .main.errors import page_not_found, internal_server_error
	app.register_error_handler(404, page_not_found)
	app.register_error_handler(500, internal_server_error)
	from .ques import ques as ques_blueprint
	app.register_blueprint(ques_blueprint)

	return app
