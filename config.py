import os

class Config:
	basedir = os.path.abspath(os.path.dirname(__file__))

	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string' # 用于表单的 CSRF

	QUESTIONNAIRE_DIR = os.path.join(basedir, 'app/questionnaires')
	QUESTIONNAIRE_SUBMISSIONS_DIR = os.path.join(basedir, 'app/submissions')
	QUESTIONNAIRE_RESULTS_DIR = os.path.join(basedir, 'app/results')

	QUESTIONNAIRE_BASIC_AUTH = ('admin', 'secret')

	QUESTIONNAIRE_DEFAULTS = {
	    "submit": "Submit",
	    "messages": {
	        "error": {
	            "required": "Field is required",
	            "invalid": "Invalid value"
	        },
	        "success": "Thank you! Your form has been submitted!"
	    }
	}

	SUBMISSION_DATEFMT = '%Y%m%d%H%M%S%f'
	
	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:tbu33p6r9@localhost/letsvote'


class TestingConfig(Config):
	TESTING = True


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,

	'default': DevelopmentConfig
}
