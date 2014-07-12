# -*-coding: utf-8 -*-
#!flask/bin/python

from models import Blogpost, Reference

'''                 Helper Functions            '''

def is_blogpost_unique(title):
    if Blogpost.query.filter_by(title=title).first():
        return False
    else:
        return True
        
def is_blogpost_short_unique(short_title):
    if Blogpost.query.filter_by(short_title=short_title).first():
        return False
    else:
        return True

def is_reference_unique(title):
    if Reference.query.filter_by(title=title).first():
        return False
    else:
        return True
