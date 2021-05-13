from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_pyfile('application.cfg', silent=True)
app.secret_key = app.config['SECRET_KEY']


db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager()
login.init_app(app)

from app import routes, models, google_auth, google_calendar, oreluniverAPI
from app.models import User, Group
