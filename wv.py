# -*-coding: utf-8 -*-
#!flask/bin/python

'''        copyright by Elias Zeitfogel        '''

from __future__ import with_statement
import os
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

#config
app.config.from_pyfile('wv.cfg')

#db = SQLAlchemy(app)

@app.route('/index')
def index():
    return redirect(url_for('show_blog'))

@app.route('/')
def show_blog():
    return render_template('show_blog.html')

@app.route('/projects')
def show_projects():
    return render_template('show_projects.html')

@app.route('/cv')
def show_cv():
    return render_template('show_cv.html')

@app.route('/about')
def show_about():
    return render_template('show_about.html')

@app.route('/search', methods=['POST'])
def search():
    terms = unicode(request.form['searchterms'])
    print terms
    return render_template('search.html', terms=terms)

@app.route('/dashboard')
def dashboard():
    try:    
        if not session.get('logged_in'):
            abort(401)        
        return render_template('dashboard.html') 
    
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/create')
def create_blogpost():
    try:    
        if not session.get('logged_in'):
            abort(401)        
        if request.method == 'POST':
            print 'post created'
            return render_template('dashboard.html')

        return render_template('create_blogpost.html') 
         
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/edit')
def edit_blogpost_list():
    try:    
        if not session.get('logged_in'):
            abort(401)        
        return render_template('edit_blogpost_list.html') 
    
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/delete/<title>')
def delete_blogpost():
    try:    
        if not session.get('logged_in'):
            abort(401)        
        return render_template('dashboard.html') 
    
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

















@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        error = None
        if request.method == 'POST':
            username = unicode(request.form['username'])
            #check user in DB
            '''
            user = User.query.filter_by(username=userame).first()
            if not user:
                error = 'Invalid username or password.'
            elif pwd_context.verify(request.form['password'], user.pw_hash):
            ''' 
            session['logged_in'] = True
            session['user'] = request.form['username']
            session.permanent = False
            flash('Logged in.', 'info')
            return redirect(url_for('dashboard'))
        return render_template('login.html', error=error)
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('Logged out.', 'info')
    return redirect(url_for('show_blog'))

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
