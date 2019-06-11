from flask import render_template, flash, url_for, session, redirect, request, send_from_directory, abort, current_app as app
from . import main

@main.route('/about', methods=['GET'])
def about():
	return render_template('about.html')