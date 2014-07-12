# -*-coding: utf-8 -*-
#!flask/bin/python

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

'''                 Config and Initialisation               '''

app = Flask(__name__)

app.config.from_pyfile('wv.cfg')

db = SQLAlchemy(app)

from webvita import views, blogposts, references, sessions, errors, helpers, models

