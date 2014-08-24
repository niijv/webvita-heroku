# -*-coding: utf-8 -*-

from webvita import app, db

from flask import request, session, redirect, url_for, abort,\
                  render_template, flash
                  
from flask.ext.sqlalchemy import SQLAlchemy

from models import Blogpost, Reference, User, Tag


@app.route('/index')
def index():
    return redirect(url_for('show_blog'))

@app.route('/')
def show_blog():
    blogposts = Blogpost.query.order_by('posted desc').all()
    return render_template('show_blog.html', blogposts=blogposts)

@app.route('/references')
def show_references():
    references = Reference.query.order_by('id desc').all()
    return render_template('show_references.html', references=references)


@app.route('/about')
def show_about():
    return render_template('show_about.html')

@app.route('/search', methods=['POST'])
def show_search():
    terms = unicode(request.form['searchterms'])
    
    #blogposts = Blogpost.query.whoosh_search(terms, or_=True)
    return render_template('search.html', terms=terms)
   

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        abort(401)   
       
    return render_template('dashboard.html') 
    
