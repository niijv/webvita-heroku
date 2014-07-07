# -*-coding: utf-8 -*-
#!flask/bin/python

'''        copyright by Elias Zeitfogel        '''

from __future__ import with_statement
import os
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime

'''                 Config and Initialisation               '''

app = Flask(__name__)

app.config.from_pyfile('wv.cfg')

db = SQLAlchemy(app)


'''             General Routing             '''

@app.route('/index')
def index():
    return redirect(url_for('show_blog'))

@app.route('/')
def show_blog():
    try:    

        blogposts = Blogpost.query.order_by('posted desc').all()
        '''all_tags = []        
        for blogpost in blogposts:
            tags = TagsToBlogposts.query.filter_by(blogpost=blogpost.blogpost_id).all()
            tags_per_blogpost = []
            for t in tags:
                tag = Tag.query.filter_by(tag_id=t.tag).first()
                tags_per_blogpost.append(tag.name)
            all_tags.append(tags_per_blogpost)'''
        return render_template('show_blog.html', blogposts=blogposts)#, tags=all_tags)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        abort(404)

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


'''                 Blogposts               '''

@app.route('/blog/<blogpost_title>')
def show_blogpost(blogpost_title):
    try:
        
        blogpost = Blogpost.query.filter_by(title=blogpost_title).first()
        '''tags = TagsToBlogposts.query.filter_by(blogpost=blogpost.blogpost_id).all()
        all_tags = []
        for t in tags:
            tag = Tag.query.filter_by(tag_id=t.tag).first()
            all_tags.append(tag.name)'''
        return render_template('show_blogpost.html', blogpost=blogpost)#, tags=all_tags)

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
        return render_template('create_blogpost.html')   

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/add', methods=['GET', 'POST'])
def add_blogpost():
    try:

        if not session.get('logged_in'):
            abort(401)    

        title = unicode(request.form['title'])
        if not is_title_unique(title):
            flash('Title already exists. Please choose a different title for your blogpost.')
            return redirect(url_for('create_blogpost')) #TODO: send previous data
        
        blogpost_tags = []
        tags = unicode(request.form['tags'])
        for t in tags.split(','):
            t = t.strip()
            blogpost_tags.append(t)           

        user = User.query.filter_by(username=session['user']).first()
        blogpost = Blogpost(user, title, unicode(request.form['text']), blogpost_tags, hidden=False, )
        db.session.add(blogpost)       
        db.session.commit()               

        '''tags = unicode(request.form['tags'])
        for t in tags.split(','):
            t = t.strip()            
            tag = Tag.query.filter_by(name=t).first()
            if not tag:                
                tag = Tag(t)
                db.session.add(tag)
                db.session.commit()
            #tag_to_blogpost = TagsToBlogposts(tag.tag_id, blogpost.blogpost_id)
            #db.session.add(tag_to_blogpost)
            #db.session.commit()'''

        flash('New blogpost has been added.')
        return redirect(url_for('show_blog'))

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

@app.route('/blog/edit/<blogpost_title>')
def edit_blogpost():
    try:    

        if not session.get('logged_in'):
            abort(401)        
        return render_template('edit_blogpost.html', blogpost=blogpost) 

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error += '\n' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/delete/<blogpost_title>')
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

@app.route('/blog/tag/<tag_name>')
def show_tag(tag_name):
    try:
        '''tag = Tag.query.filter_by(name=tag_name).first()
        tag_to_blogposts = TagsToBlogposts.query.filter_by(tag=tag.tag_id).all()
        blogposts = []
        for t in tag_to_blogposts:
            blogpost = Blogpost.query.filter_by(blogpost_id=t.blogpost).first()
            blogposts.append(blogpost)
        all_tags = []        
        for blogpost in blogposts:
            tags = TagsToBlogposts.query.filter_by(blogpost=blogpost.blogpost_id).all()
            tags_per_blogpost = []
            for t in tags:
                tag = Tag.query.filter_by(tag_id=t.tag).first()
                tags_per_blogpost.append(tag.name)
            all_tags.append(tags_per_blogpost)'''
        blogposts = Blogpost.query.order_by('posted desc').filter(Blogpost.tags.any(name=tag_name)).all()
        return render_template('show_tag_blogposts.html', tag_name=tag_name, blogposts=blogposts)#, tags=all_tags)
    
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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    pw_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    blogposts = db.relationship('Blogpost', backref=db.backref('user', lazy='joined'), lazy='dynamic')
    
    def __init__(self, username, pw_hash, email):
        self.username = username
        self.pw_hash = pw_hash
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

tags = db.Table('tags',
    db.Column('blogpost_id', db.Integer, db.ForeignKey('blogpost.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.Unicode, unique=True)
    text = db.Column(db.Unicode)
    posted = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    hidden = db.Column(db.Boolean)
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('tags', lazy='dynamic'))

    def __init__(self, author, title, text, tags, posted=None, edited=None, hidden=True):
        self.user_id = author.id        
        self.title = title
        self.text = text
        tag_list = []
        for t in tags:
            tag = Tag.query.filter_by(name=t).first()
            if not tag:                
                tag_list.append(Tag(t))
            else:
                tag_list.append(tag)
        self.tags = tag_list
        if posted is None:
            posted = datetime.utcnow()
        self.posted = posted
        if edited is None:
            edited = datetime.utcnow()
        self.edited = edited
        self.hidden = hidden

    def __repr__(self):
        return '<Blogpost %r>' % self.title

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % self.name

'''class TagsToBlogposts(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    tag = db.Column(db.Integer, db.ForeignKey('tag.tag_id'))
    blogpost = db.Column(db.Integer, db.ForeignKey('blogpost.blogpost_id'))

    def __init__(self, tag, blogpost):
        self.tag = tag
        self.blogpost = blogpost

    def __repr__(self):
        return '<TagToBlogpost %r to %r>' % (self.tag, self.blogpost)
'''

'''                 Helper Functions            '''

def is_title_unique(title):
    if Blogpost.query.filter_by(title=title).first():
        return False
    else:
        return True

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
    db_setup('dummy', 'dummy', 'dummy@mail.com')
