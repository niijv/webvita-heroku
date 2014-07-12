# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import db, models

from passlib.apps import custom_app_context as pwd_context

def db_setup(name, realname, pw, email):
    #currently for development#
    db.drop_all()
    db.create_all()
    admin = models.User(name, realname, pwd_context.encrypt(pw), email)
    db.session.add(admin)
    db.session.commit()
    
db_setup('dummy', 'Mr. Dummy', 'dummy', 'dummy@mail.com')