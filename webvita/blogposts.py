# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import app, db

from flask import request, session, redirect, url_for, abort,\
                  render_template, flash

from flask.ext.sqlalchemy import SQLAlchemy

from models import Blogpost, Tag, User

from datetime import datetime

from helpers import is_blogpost_unique, is_blogpost_short_unique

import markdown

'''                 Blogposts               '''

@app.route('/blog/<blogpost_short_title>')
def show_blogpost(blogpost_short_title):
    try:
        
        blogpost = Blogpost.query.filter_by(short_title=blogpost_short_title)\
                           .first_or_404()
        return render_template('show_blogpost.html', blogpost=blogpost)

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in show_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/create')
def create_blogpost():
    if not session.get('logged_in'):
        abort(401)
        
    try:    
        return render_template('create_blogpost.html')   

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
           error = 'Error in create_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/add', methods=['GET', 'POST'])
def add_blogpost():
    if not session.get('logged_in'):
        abort(401)
        
    try:   
        title = unicode(request.form['title'])
        if not is_blogpost_unique(title):
            flash('Title already exists. Please choose a different title ' + \
                  'for your blogpost.')
            # TODO: send previous data
            return redirect(url_for('create_blogpost'))
        short_title = unicode(request.form['short_title']).replace(' ', '-')
        if not is_blogpost_short_unique(short_title):
            flash('Short title already exists. Please choose a different ' + \
                  'short title for your blogpost.')
            # TODO: send previous data
            return redirect(url_for('create_blogpost'))
        subtitle = unicode(request.form['subtitle'])
                
        text_markdown = unicode(request.form['text'])
        text_html = markdown.markdown(text_markdown, ['codehilite'])
        
        blogpost_tags = []
        tags = unicode(request.form['tags'])
        for t in tags.split(','):
            t = t.strip()
            if t:
                blogpost_tags.append(t)           

        user = User.query.filter_by(username=session['user']).first_or_404()
        blogpost = Blogpost(user, title, subtitle, short_title, text_markdown,
                            text_html, blogpost_tags, hidden=False)
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
    if not session.get('logged_in'):
        abort(401)
        
    try:   
        blogposts = Blogpost.query.order_by('posted desc').all()       
        return render_template('edit_blogpost_list.html', blogposts=blogposts) 

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in edit_blogpost_list: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/edit/<blogpost_short_title>')
def edit_blogpost(blogpost_short_title):
    if not session.get('logged_in'):
        abort(401)
        
    try:   

        blogpost = Blogpost.query.filter_by(short_title=blogpost_short_title).first_or_404()  
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

@app.route('/blog/update/<blogpost_short_title>', methods=['GET', 'POST'])
def update_blogpost(blogpost_short_title):
    if not session.get('logged_in'):
        abort(401)
        
    try:    
        
        old_bp = Blogpost.query.filter_by(short_title=blogpost_short_title)\
                         .first_or_404()
        blogpost_title = old_bp.title
        title = unicode(request.form['title'])
        if title!=blogpost_title and not is_blogpost_unique(title):
            flash('Title already exists. Please choose a different title' + \
                  ' for your blogpost.')
            # TODO: send previous data
            return redirect(url_for('edit_blogpost', 
                                    blogpost_title=blogpost_title))
        short_title = unicode(request.form['short_title']).replace(' ', '-')
        if short_title!=blogpost_short_title and not \
           is_blogpost_short_unique(short_title):
            flash('Short title already exists. Please choose a different ' + \
                  'short title for your blogpost.')
            # TODO: send previous data
            return redirect(url_for('edit_blogpost', 
                                    blogpost_title=blogpost_title))
        subtitle = unicode(request.form['subtitle'])
        
        
        text_markdown = unicode(request.form['text'])
        text_html = markdown.markdown(text_markdown, ['codehilite'])

        blogpost_tags = []
        tags = unicode(request.form['tags'])
        for t in tags.split(','):
            t = t.strip()
            if t:
                blogpost_tags.append(t)           
        
        
        old_bp.title = title    
        old_bp.subtitle = subtitle
        old_bp.short_title = short_title
        old_bp.text_markdown = text_markdown
        old_bp.text_html = text_html
        # TODO: remove possible unused tags        
        old_bp.update_tags(blogpost_tags)
        old_bp.edited = datetime.utcnow()
        db.session.commit()

        flash('Blogpost has been updated.')
        return redirect(url_for('show_blogpost', 
                                blogpost_short_title=short_title))          

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in update_blogpost: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/blog/delete/<blogpost_short_title>')
def delete_blogpost(blogpost_short_title):
    if not session.get('logged_in'):
        abort(401)
        
    try:   

        blogpost = Blogpost.query.filter_by(short_title=blogpost_short_title)\
                           .first_or_404()
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
        