from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import requests
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login = LoginManager()
login.init_app(app)

client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])

from app import routes, models
from app.models import User
