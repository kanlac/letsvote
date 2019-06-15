import os

def init_data(db):
	from app.models import User

	db.drop_all()
	db.create_all()

	jack = User(username='Jack', password='123456')
	jane = User(username='Jane', password='123456')
	jacob = User(username='Jacob', password='123456')
	jerry = User(username='Jerry', password='123456')
	jesse = User(username='Jesse', password='123456')
	josef = User(username='Josef', password='123456')
	jude = User(username='Jude', password='123456')
	jackson = User(username='Jackson', password='123456')
	jupiter = User(username='Jupiter', password='123456')

	db.session.add_all([jack, jane, jacob, jerry, jesse, josef, jude, jackson, jupiter])
	db.session.commit()


if __name__ == '__main__':
	from app import db, create_app

	app = create_app(os.getenv('FLASK_CONFIG') or 'production')
	app.app_context().push()
	db.init_app(app)
	init_data(db)
