# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import app, db

from flask import request, session, redirect, url_for, abort,\
                  render_template, flash
                  
from flask.ext.sqlalchemy import SQLAlchemy

from models import Blogpost, Reference, User, Tag

'''             General Routing             '''

@app.route('/index')
def index():
    return redirect(url_for('show_blog'))

@app.route('/')
def show_blog():
    try:    

        blogposts = Blogpost.query.order_by('posted desc').all()
        return render_template('show_blog.html', blogposts=blogposts)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in show_blog: ' + str(e)
        flash(error, 'error')
        abort(404)

@app.route('/references')
def show_references():
    try:    

        references = Reference.query.order_by('id desc').all()
        return render_template('show_references.html', references=references)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in show_references: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/about')
def show_about():
    return render_template('show_about.html')

@app.route('/search', methods=['POST'])
def search():
    terms = unicode(request.form['searchterms'])
    return render_template('search.html', terms=terms)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
            abort(401)   
    
    try:    
        return render_template('dashboard.html') 
    
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in dashboard: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))
