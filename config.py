import os

class Config:
	basedir = os.path.abspath(os.path.dirname(__file__))

	SECRET_KEY = os.environ.get('SECRET_KEY') or '?r1us6iLZ(yh' # 用于表单的 CSRF

	QUESTIONNAIRE_DIR = os.path.join(basedir, 'app/questionnaires')
	QUESTIONNAIRE_SUBMISSIONS_DIR = os.path.join(basedir, 'app/submissions')
	QUESTIONNAIRE_RESULTS_DIR = os.path.join(basedir, 'app/results')
	QUESTIONNAIRE_QRCODE_DIR = os.path.join(basedir, 'app/questionnaires/qrcode')

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
	SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/letsvote'
	QUESTIONNAIRE_SITE_BASE = '127.0.0.1:5000/'


class TestingConfig(Config):
	TESTING = True


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = 'postgres://ieoxmhcknxirqf:8dde7911fa035f8f02e66811241216535da00903a1240439fc8bdab2a275a1e6@ec2-107-22-238-217.compute-1.amazonaws.com:5432/d2o7vjbnvqgv8r'
	QUESTIONNAIRE_SITE_BASE = 'https://letsvote19.herokuapp.com/'


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}
