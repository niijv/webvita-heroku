# -*-coding: utf-8 -*-

from webvita import db
from models import Blogpost, Reference, Tag


def is_blogpost_unique(title):
    return Blogpost.query.filter_by(title=title).first() is not None
        
def is_blogpost_short_unique(short_title):
    return Blogpost.query.filter_by(short_title=short_title).first() is not None

def is_reference_unique(title):
    return Reference.query.filter_by(title=title).first() is not None

        
def delete_unused_tags(tag_list):
    for tag in tag_list:
        if tag.blogposts.all():
            continue
        else:
            db.session.delete(tag)
    db.session.commit()
