from app import db
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text, index=True, unique=True, nullable=False)
    username = db.Column(db.Text)
    email = db.Column(db.Text, index=True, unique=True, nullable=False)
    profile_pic = db.Column(db.Text)

    def __init__(self, user_id, username, email, profile_pic):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.profile_pic = profile_pic

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar32px(self):
        return self.profile_pic.replace('=s96-c', '=32-c')


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idGroup = db.Column(db.Integer, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.idGroup)
