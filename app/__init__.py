from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from celery import Celery

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_pyfile('application.cfg', silent=True)
app.secret_key = app.config['SECRET_KEY']


db = SQLAlchemy(app)
migrate = Migrate(app, db)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
login = LoginManager()
login.init_app(app)

from app import routes, models, google_auth, google_calendar
from app.models import User, Group
