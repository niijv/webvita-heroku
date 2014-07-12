# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import app

from flask import render_template

'''             Error Handling              '''

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

