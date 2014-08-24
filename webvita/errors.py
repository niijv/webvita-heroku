# -*-coding: utf-8 -*-

from webvita import app

from flask import render_template


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

