from flask import render_template, flash, url_for, session, redirect, request
from . import main

@main.route('/about', methods=['GET'])
def about():
	return render_template('about.html')