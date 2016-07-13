from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from views import api
app.register_blueprint(api, url_prefix = '/api')