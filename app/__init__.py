import os
from flask import Flask
from flask.ext.pymongo import PyMongo
import create_champ_images

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.config["MONGO_DBNAME"] = "app"
mongo = PyMongo(app)

from app import views