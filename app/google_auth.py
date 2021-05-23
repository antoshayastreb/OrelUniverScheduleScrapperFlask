import functools
import os

import flask

from app import app, db
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from flask import render_template, request, jsonify, make_response, redirect, url_for
from authlib.integrations.requests_client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
AUTH_REDIRECT_URI = app.config['AUTH_REDIRECT_URI']
BASE_URI = app.config['BASE_URI']

AUTHORIZATION_SCOPE = 'openid email profile https://www.googleapis.com/auth/calendar'

CLIENT_ID = app.config['GOOGLE_CLIENT_ID']
CLIENT_SECRET = app.config['GOOGLE_CLIENT_SECRET']

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'


def is_logged_in():
    return True if AUTH_TOKEN_KEY in flask.session else False


def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    oauth2_tokens = flask.session[AUTH_TOKEN_KEY]

    return google.oauth2.credentials.Credentials(
        oauth2_tokens['access_token'],
        refresh_token=oauth2_tokens['refresh_token'],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI)


def build_credentials_token(oauth2_tokens, refresh_token):

    return google.oauth2.credentials.Credentials(
        oauth2_tokens,
        refresh_token=refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI)


def get_user_info():
    credentials = build_credentials()

    oauth2_client = googleapiclient.discovery.build(
        'oauth2', 'v2',
        credentials=credentials)

    return oauth2_client.userinfo().get().execute()


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)


@app.route('/login')
@no_cache
def login():
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.create_authorization_url(AUTHORIZATION_URL)

    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True

    return flask.redirect(uri, code=302)


@app.route('/login/callback')
@no_cache
def google_auth_redirect():
    req_state = flask.request.args.get('state', default=None, type=None)

    if req_state != flask.session[AUTH_STATE_KEY]:
        response = flask.make_response('Invalid state parameter', 401)
        return response

    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)

    oauth2_tokens = session.fetch_access_token(
        ACCESS_TOKEN_URI,
        authorization_response=flask.request.url)

    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens

    user_info = get_user_info()

    if user_info["verified_email"]:
        unique_id = user_info["id"]
        users_email = user_info["email"]
        picture = user_info["picture"]
        users_name = user_info["name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(user_id=unique_id, username=users_name, email=users_email, profile_pic=picture,
                oauth2_tokens=oauth2_tokens['access_token'], refresh_token=oauth2_tokens['refresh_token'])

    exists = db.session.query(
        db.session.query(User).filter_by(user_id=unique_id).exists()
    ).scalar()

    if exists:
        dbUser = User.query.filter_by(user_id=unique_id).first()
        if dbUser.profile_pic != user.profile_pic:
            dbUser.profile_pic = user.profile_pic
            db.session.commit()
        if dbUser.username != user.username:
            dbUser.username = user.username
            db.session.commit()
        if dbUser.oauth2_tokens != user.oauth2_tokens:
            dbUser.oauth2_tokens = user.oauth2_tokens
            db.session.commit()
        if dbUser.refresh_token != user.refresh_token:
            dbUser.refresh_token = user.refresh_token
            db.session.commit()
        login_user(dbUser)
        return redirect(url_for("index"))
    else:
        db.session.add(user)
        db.session.commit()
        login_user(user)

    return flask.redirect(BASE_URI, code=302)


@app.route("/logout")
@no_cache
def logout():
    logout_user()
    flask.session.pop(AUTH_TOKEN_KEY, None)
    flask.session.pop(AUTH_STATE_KEY, None)
    resp = make_response(flask.redirect(BASE_URI, code=302))
    resp.delete_cookie('group')
    resp.delete_cookie('kurs')
    resp.delete_cookie('division')
    resp.delete_cookie('subgroup')
    return resp
