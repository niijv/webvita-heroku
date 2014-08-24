# -*-coding: utf-8 -*-

from webvita import app, db

from flask import request, session, redirect, url_for, abort,\
                  render_template, flash

from flask.ext.sqlalchemy import SQLAlchemy

from models import Blogpost, Tag, User

from datetime import datetime

from helpers import is_blogpost_unique, is_blogpost_short_unique,\
                    delete_unused_tags

import markdown


@app.route('/blog/<blogpost_short_title>')
def show_blogpost(blogpost_short_title):

    blogpost = Blogpost.query.filter_by(short_title=blogpost_short_title)\
                       .first_or_404()
    return render_template('show_blogpost.html', blogpost=blogpost)

@app.route('/blog/create')
def create_blogpost():
    if not session.get('logged_in'):
        abort(401)
         
    return render_template('create_blogpost.html')   

@app.route('/blog/add', methods=['GET', 'POST'])
def add_blogpost():
    if not session.get('logged_in'):
        abort(401)
        
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

@app.route('/blog/edit')
def edit_blogpost_list():
    if not session.get('logged_in'):
        abort(401)

    blogposts = Blogpost.query.order_by('posted desc').all()       
    return render_template('edit_blogpost_list.html', blogposts=blogposts) 

@app.route('/blog/edit/<blogpost_short_title>')
def edit_blogpost(blogpost_short_title):
    if not session.get('logged_in'):
        abort(401)
        
    blogpost = Blogpost.query.filter_by(short_title=blogpost_short_title).first_or_404()  
    tags = ', '.join([tag.name for tag in blogpost.tags])     
    return render_template('edit_blogpost.html', 
                           blogpost=blogpost, 
                           tags=tags)

@app.route('/blog/update/<blogpost_short_title>', methods=['GET', 'POST'])
def update_blogpost(blogpost_short_title):
    if not session.get('logged_in'):
        abort(401)
        
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
    
    old_tags = list(old_bp.tags)
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
    old_bp.update_tags(blogpost_tags)
    old_bp.edited = datetime.utcnow()
    db.session.commit()
    delete_unused_tags(old_tags)

    flash('Blogpost has been updated.')
    return redirect(url_for('show_blogpost', 
                            blogpost_short_title=short_title))          

@app.route('/blog/delete/<blogpost_short_title>')
def delete_blogpost(blogpost_short_title):
    if not session.get('logged_in'):
        abort(401)
        
    blogpost = Blogpost.query.filter_by(short_title=blogpost_short_title)\
                       .first_or_404()
    old_tags = list(blogpost.tags)
    db.session.delete(blogpost)
    db.session.commit()
    delete_unused_tags(old_tags)
    
    flash('Blogpost has been deleted.')
    return render_template('dashboard.html') 

@app.route('/blog/tag/<tag_name>')
def show_tag(tag_name):

    blogposts = Blogpost.query.order_by('posted desc')\
                        .filter(Blogpost.tags.any(name=tag_name)).all()
    return render_template('show_tag_blogposts.html', 
                           tag_name=tag_name, 
                           blogposts=blogposts)
    
        