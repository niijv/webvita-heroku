# -*-coding: utf-8 -*-
#!flask/bin/python

'''        copyright by Elias Zeitfogel        '''

from __future__ import with_statement
import os
from datetime import datetime

from flask import Flask, request, session, redirect, url_for, abort,\
                  render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy

from passlib.apps import custom_app_context as pwd_context


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
    try:    
        
        if not session.get('logged_in'):
            abort(401)        
        return render_template('dashboard.html') 
    
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in dashboard: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))


'''                 Blogposts               '''

@app.route('/blog/<blogpost_title>')
def show_blogpost(blogpost_title):
    try:
        
        blogpost = Blogpost.query.filter_by(title=blogpost_title).first_or_404()
        return render_template('show_blogpost.html', blogpost=blogpost)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in show_blogpost: ' + str(e)
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
           error = 'Error in create_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/add', methods=['GET', 'POST'])
def add_blogpost():
    try:

        if not session.get('logged_in'):
            abort(401)    

        title = unicode(request.form['title'])
        if not is_blogpost_unique(title):
            flash('Title already exists. Please choose a different title ' + \
                  'for your blogpost.')
            # TODO: send previous data
            return redirect(url_for('create_blogpost'))

        subtitle = unicode(request.form['subtitle'])
        short_title = unicode(request.form['short_title'])
        
        blogpost_tags = []
        tags = unicode(request.form['tags'])
        for t in tags.split(','):
            t = t.strip()
            if t:
                blogpost_tags.append(t)           

        user = User.query.filter_by(username=session['user']).first_or_404()
        blogpost = Blogpost(user, title, subtitle, short_title, unicode(request.form['text']), 
                            blogpost_tags, hidden=False)
        db.session.add(blogpost)       
        db.session.commit()

        flash('New blogpost has been added.')
        return redirect(url_for('show_blog'))

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in add_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/edit')
def edit_blogpost_list():
    try:    

        if not session.get('logged_in'):
            abort(401)

        blogposts = Blogpost.query.order_by('posted desc').all()       
        return render_template('edit_blogpost_list.html', blogposts=blogposts) 

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in edit_blogpost_list: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/edit/<blogpost_title>')
def edit_blogpost(blogpost_title):
    try:    

        if not session.get('logged_in'):
            abort(401)

        blogpost = Blogpost.query.filter_by(title=blogpost_title).first_or_404()  
        tags = ', '.join([tag.name for tag in blogpost.tags])     
        return render_template('edit_blogpost.html', 
                               blogpost=blogpost, 
                               tags=tags)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in edit_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/update/<blogpost_title>', methods=['GET', 'POST'])
def update_blogpost(blogpost_title):
    try:

        if not session.get('logged_in'):
            abort(401)    

        title = unicode(request.form['title'])
        if title!=blogpost_title and not is_blogpost_unique(title):
            flash('Title already exists. Please choose a different title' + \
                  ' for your blogpost.')
            # TODO: send previous data
            return redirect(url_for('edit_blogpost', 
                                    blogpost_title=blogpost_title))
        
        subtitle = unicode(request.form['subtitle'])
        short_title = unicode(request.form['short_title'])

        blogpost_tags = []
        tags = unicode(request.form['tags'])
        for t in tags.split(','):
            t = t.strip()
            if t:
                blogpost_tags.append(t)           
        
        old_bp = Blogpost.query.filter_by(title=blogpost_title).first_or_404()
        old_bp.title = title    
        old_bp.subtitle = subtitle
        old_bp.short_title = short_title
        old_bp.text = unicode(request.form['text'])
        # TODO: remove possible unused tags        
        old_bp.update_tags(blogpost_tags)
        old_bp.edited = datetime.utcnow()
        db.session.commit()

        flash('Blogpost has been updated.')
        return redirect(url_for('show_blogpost', blogpost_title=title))          

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in update_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/delete/<blogpost_title>')
def delete_blogpost(blogpost_title):
    try:    

        if not session.get('logged_in'):
            abort(401)

        blogpost = Blogpost.query.filter_by(title=blogpost_title).first_or_404()
        db.session.delete(blogpost) #TODO: remove possible unused tags
        db.session.commit()

        flash('Blogpost has been deleted.')
        return render_template('dashboard.html') 

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in delete_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/tag/<tag_name>')
def show_tag(tag_name):
    try:

        blogposts = Blogpost.query.order_by('posted desc')\
                            .filter(Blogpost.tags.any(name=tag_name)).all()
        return render_template('show_tag_blogposts.html', 
                               tag_name=tag_name, 
                               blogposts=blogposts)
    
    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in show_tag: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))


'''             References              '''

@app.route('/references/create')
def create_reference():
    try:    

        if not session.get('logged_in'):
            abort(401)
        return render_template('create_reference.html')   

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in create_reference: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/references/add', methods=['GET', 'POST'])
def add_reference():
    try:

        if not session.get('logged_in'):
            abort(401)    

        title = unicode(request.form['title'])
        if not is_blogpost_unique(title):
            flash('Title already exists. Please choose a different title' + \
                  ' for your reference.')
            # TODO: send previous data
            return redirect(url_for('create_reference'))
        
        reference = Reference(title, 
                              unicode(request.form['text']), 
                              unicode(request.form['timespan']))
        db.session.add(reference)       
        db.session.commit()

        flash('New reference has been added.')
        return redirect(url_for('show_references'))

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in add_reference: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/references/edit')
def edit_reference_list():
    try:    

        if not session.get('logged_in'):
            abort(401)

        references = Reference.query.order_by('id desc').all()       
        return render_template('edit_reference_list.html', 
                               references=references) 

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in edit_reference_list: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/references/edit/<reference_title>')
def edit_reference(reference_title):
    try:    

        if not session.get('logged_in'):
            abort(401)

        reference = Reference.query.filter_by(title=reference_title)\
                             .first_or_404()    
        return render_template('edit_reference.html', reference=reference)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in edit_reference: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/references/update/<reference_title>', methods=['GET', 'POST'])
def update_reference(reference_title):
    try:

        if not session.get('logged_in'):
            abort(401)    

        title = unicode(request.form['title'])
        if title!=reference_title and not is_reference_unique(title):
            flash('Title already exists. Please choose a different title' + \
                  ' for your reference.')
            # TODO: send previous data
            return redirect(url_for('edit_reference', 
                                    reference_title=reference_title))    
        
        old_reference = Reference.query.filter_by(title=reference_title)\
                                 .first_or_404()
        old_reference.title = title
        old_reference.text = unicode(request.form['text'])
        old_reference.timespan = unicode(request.form['timespan'])
        db.session.commit()

        flash('Reference has been updated.')
        return redirect(url_for('show_references'))          

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in update_reference: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/references/delete/<reference_title>')
def delete_reference(reference_title):
    try:    

        if not session.get('logged_in'):
            abort(401)

        reference = Reference.query.filter_by(title=reference_title)\
                             .first_or_404()
        db.session.delete(reference)
        db.session.commit()

        flash('Reference has been deleted.')
        return render_template('dashboard.html') 

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in delete_reference: ' + str(e)
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
            error = 'Error in login: ' + str(e)
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
    realname = db.Column(db.String(120))
    pw_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    blogposts = db.relationship('Blogpost', 
                                backref=db.backref('user', lazy='joined'), 
                                lazy='dynamic')
    
    def __init__(self, username, realname, pw_hash, email):
        self.username = username
        self.realname = realname
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
    subtitle = db.Column(db.Unicode)
    short_title = db.Column(db.Unicode)
    text = db.Column(db.Unicode)
    posted = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    hidden = db.Column(db.Boolean)
    tags = db.relationship('Tag', 
                           secondary=tags, 
                           backref=db.backref('tags', lazy='dynamic'))

    def update_tags(self, tags):
        #TODO: remove unused tags
        tag_list = []
        for t in tags:
            tag = Tag.query.filter_by(name=t).first()
            if not tag:                
                tag_list.append(Tag(t))
            else:
                tag_list.append(tag)
        self.tags = tag_list

    def __init__(self, author, title, subtitle, short_title, text, tags, 
                 posted=None, edited=None, hidden=True):
        self.user_id = author.id        
        self.title = title
        self.subtitle = subtitle
        self.short_title = short_title
        self.text = text
        self.update_tags(tags)
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


class Reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    title = db.Column(db.Unicode, unique=True)
    text = db.Column(db.Unicode)
    timespan = db.Column(db.Unicode)

    def __init__(self, title, text, timespan):
        self.title = title
        self.text = text
        self.timespan = timespan

    def __repr__(self):
        return '<Reference %r>' % self.title

'''                 Helper Functions            '''

def is_blogpost_unique(title):
    if Blogpost.query.filter_by(title=title).first():
        return False
    else:
        return True

def is_reference_unique(title):
    if Reference.query.filter_by(title=title).first():
        return False
    else:
        return True

'''                 Database Setup             '''

def db_setup(name, realname, pw, email):
    #currently for development
    db.drop_all()
    db.create_all()
    admin = User(name, realname, pwd_context.encrypt(pw), email)
    db.session.add(admin)
    db.session.commit()
    app.run()


if __name__ == '__main__':
    db_setup('dummy', 'Mr. Dummy', 'dummy', 'dummy@mail.com')
