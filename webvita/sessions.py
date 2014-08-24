# -*-coding: utf-8 -*-

from webvita import app, db

from flask import request, session, redirect, url_for, abort,\
                  render_template, flash

from flask.ext.sqlalchemy import SQLAlchemy

from models import User
                  
from passlib.apps import custom_app_context as pwd_context


@app.route('/login', methods=['GET', 'POST'])
def login():
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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('Logged out.', 'info')
    return redirect(url_for('show_blog'))
    