# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import app, db

from flask import request, session, redirect, url_for, abort,\
                  render_template, flash
                  
from flask.ext.sqlalchemy import SQLAlchemy

from models import Reference

from helpers import is_reference_unique

import markdown
                  
'''             References              '''

@app.route('/references/create')
def create_reference():
    if not session.get('logged_in'):
        abort(401)
        
    try:   
        return render_template('create_reference.html')   

    except Exception, e:
        error = 'An unexpected error occured. Try again later.'
        if app.debug:
            error = 'Error in create_reference: ' + str(e)
        flash(error, 'error')
        return redirect(url_for('show_blog'))

@app.route('/references/add', methods=['GET', 'POST'])
def add_reference():
    if not session.get('logged_in'):
        abort(401)
        
    try:     

        title = unicode(request.form['title'])
        if not is_reference_unique(title):
            flash('Title already exists. Please choose a different title' + \
                  ' for your reference.')
            # TODO: send previous data
            return redirect(url_for('create_reference'))
        text_markdown =  unicode(request.form['text'])
        text_html = markdown.markdown(text_markdown, ['codehilite'])
        
        reference = Reference(title, text_markdown, text_html, 
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
    if not session.get('logged_in'):
        abort(401)
        
    try:   

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
    if not session.get('logged_in'):
        abort(401)
        
    try:   

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
    if not session.get('logged_in'):
        abort(401)
        
    try:      

        title = unicode(request.form['title'])
        if title!=reference_title and not is_reference_unique(title):
            flash('Title already exists. Please choose a different title' + \
                  ' for your reference.')
            # TODO: send previous data
            return redirect(url_for('edit_reference', 
                                    reference_title=reference_title))    
        
        text_markdown =  unicode(request.form['text'])
        text_html = markdown.markdown(text_markdown, ['codehilite'])
        old_reference = Reference.query.filter_by(title=reference_title)\
                                 .first_or_404()
        old_reference.title = title
        old_reference.text_markdown = text_markdown
        old_reference.text_html = text_html
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
    if not session.get('logged_in'):
        abort(401)
        
    try:   

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
