from flask import render_template
from . import main

@main.errorhandler(404)
def page_not_found(e):
	return render_template('error/404.html'), 404 # set the 404 status explicitly

@main.errorhandler(500)
def internal_server_error(e):
	return render_template('error/500.html'), 500