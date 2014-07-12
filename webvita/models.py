# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import db

from datetime import datetime

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
    short_title = db.Column(db.Unicode, unique=True)
    text_markdown = db.Column(db.Unicode)
    text_html = db.Column(db.Unicode)
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
        