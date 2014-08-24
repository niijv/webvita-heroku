# -*-coding: utf-8 -*-
#!flask/bin/python

from webvita import db, models

from passlib.apps import custom_app_context as pwd_context

def db_setup_dev(name, realname, pw, email):
    db.drop_all()
    db.create_all()
    admin = models.User(name, realname, pwd_context.encrypt(pw), email)
    db.session.add(admin)
    db.session.commit()
    
def db_reset():
    db.drop_all()
    db.create_all()
    
                           
#db_setup_dev('dummy', 'Mr. Dummy', 'dummy', 'dummy@mail.com')
#db_reset()

