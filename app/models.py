from time import time
import json
from app import db
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), index=True, unique=True, nullable=False)
    username = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    profile_pic = db.Column(db.String(128))
    lastCalendarID = db.Column(db.String(128))
    oauth2_tokens = db.Column(db.Text)
    # refresh_token = db.Column(db.String(200))
    division = db.Column(db.Integer, index=True)
    kurs = db.Column(db.Integer, index=True)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    auto_insert = db.Column(db.Boolean)

    def __init__(self, user_id, username, email, profile_pic, oauth2_tokens):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.profile_pic = profile_pic
        self.oauth2_tokens = oauth2_tokens

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar32px(self):
        return self.profile_pic.replace('=s96-c', '=32-c')

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idGroup = db.Column(db.Integer, index=True, nullable=False)
    subGroup = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
