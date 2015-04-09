import os
from flask import Flask
from flask.ext.pymongo import PyMongo
import create_champ_images

app = Flask(__name__)
mongo = PyMongo(app)

from app import views
