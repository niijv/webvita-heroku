# -*-coding: utf-8 -*-

from webvita import app, db

#import flask.ext.whooshalchemy as whooshalchemy

from datetime import datetime


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
    #__searchable__ = ['title', 'text_html', 'subtitle', 'short_title']
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.Unicode, unique=True)
    subtitle = db.Column(db.Unicode)
    short_title = db.Column(db.Unicode, unique=True)
    text_markdown = db.Column(db.Unicode)
    text_html = db.Column(db.Unicode)
    posted = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    hidden = db.Column(db.Boolean)
    tags = db.relationship('Tag', 
                           secondary=tags, 
                           backref=db.backref('blogposts', lazy='dynamic'))

    def update_tags(self, tags):
        to_add = set(tags)
        for old_tag in list(self.tags):
            if old_tag.name not in tags:
                self.tags.remove(old_tag)
            to_add.discard(old_tag.name)
        for new_tag in to_add:
            tag = Tag.query.filter_by(name=new_tag).first()
            if tag is None:
                tag = Tag(new_tag)
            self.tags.append(tag)

    def __init__(self, author, title, subtitle, short_title, text_markdown,
                 text_html, tags, posted=None, edited=None, hidden=True):
        self.user_id = author.id        
        self.title = title
        self.subtitle = subtitle
        self.short_title = short_title
        self.text_markdown = text_markdown
        self.text_html = text_html
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
    text_markdown = db.Column(db.Unicode)
    text_html = db.Column(db.Unicode)
    timespan = db.Column(db.Unicode)

    def __init__(self, title, text_markdown, text_html, timespan):
        self.title = title
        self.text_markdown = text_markdown
        self.text_html = text_html
        self.timespan = timespan
        
    def __repr__(self):
        return '<Reference %r>' % self.title

#whooshalchemy.whoosh_index(app, Blogpost)
