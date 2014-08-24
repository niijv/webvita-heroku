# -*-coding: utf-8 -*-
#!flask/bin/python
import os

SECRET_KEY = "very secret"
DEBUG = True
SQLALCHEMY_ECHO = False

if os.environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/webvita-heroku'

#Openshift: 'OPENSHIFT_POSTGRESQL_DB_URL'
#Heroku: 'DATABASE_URL'


