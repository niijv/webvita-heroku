# -*-coding: utf-8 -*-
#!flask/bin/python

'''        copyright by Elias Zeitfogel        '''

from __future__ import with_statement
import os
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

'''                 Config and Initialisation               '''

app = Flask(__name__)

app.config.from_pyfile('wv.cfg')

db = SQLAlchemy(app)


'''             Routing             '''

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


'''             Login and Session Logic             '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        error = None
        if request.method == 'POST':
            username = unicode(request.form['username'])
            user = User.query.filter_by(username=username).first()
            
            if not user:
                error = 'Invalid username or password'
            elif pwd_context.verify(request.form['password'], user.pw_hash):
                session['logged_in'] = True
                session['user'] = user.username
                session.permanent = False
                flash('Logged in.', 'info')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password'
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


'''                 Database Models                 '''

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    pw_hash = db.Column(db.String(400))
    email = db.Column(db.String(120), unique=True)
    
    def __init__(self, username, pw_hash, email):
        self.username = username
        self.pw_hash = pw_hash
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


'''                 Database Setup             '''

def db_setup(name, pw, email):

    #currently for development
    db.drop_all()
    db.create_all()
    admin = User(name, pwd_context.encrypt(pw), email)
    db.session.add(admin)
    db.session.commit()
    app.run()


if __name__ == '__main__':
    db_setup('Dummy', 'dummy', 'dummy@mail.com')
