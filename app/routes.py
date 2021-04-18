import flask

from app import app, db
from flask import render_template, request, jsonify, make_response, redirect, url_for
import ast
import requests
from app import datetimecalc as dtc
import json
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

base_request = 'http://oreluniver.ru/schedule/'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', divisions=get_divisionlist())


@app.route('/login', methods=['GET', 'POST'])
def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.config['CLIENT_SECRETS_FILE'], scopes=app.config['SCOPES'])
    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline')
    # Enable incremental authorization. Recommended as a best practice.
    # include_granted_scopes='true')
    flask.session['state'] = state

    return flask.redirect(authorization_url)

    # google_provider_cfg = get_google_provider_cfg()
    # authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # request_uri = client.prepare_request_uri(
    #     authorization_endpoint,
    #     redirect_uri=request.base_url + "/callback",
    #     scope=["openid", "email", "profile"],
    # )
    # return redirect(request_uri)


@app.route("/login/callback")
def callback():
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.config['CLIENT_SECRETS_FILE'], scopes=app.config['SCOPES'], state=state)
    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for('index'))
    # code = request.args.get("code")
    # google_provider_cfg = get_google_provider_cfg()
    # token_endpoint = google_provider_cfg["token_endpoint"]
    #
    # token_url, headers, body = client.prepare_token_request(
    #     token_endpoint,
    #     authorization_response=request.url,
    #     redirect_url=request.base_url,
    #     code=code
    # )
    # token_response = requests.post(
    #     token_url,
    #     headers=headers,
    #     data=body,
    #     auth=(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET']),
    # )
    #
    # client.parse_request_body_response(json.dumps(token_response.json()))
    #
    # userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    # uri, headers, body = client.add_token(userinfo_endpoint)
    # userinfo_response = requests.get(uri, headers=headers, data=body)
    #
    # if userinfo_response.json().get("email_verified"):
    #     unique_id = userinfo_response.json()["sub"]
    #     users_email = userinfo_response.json()["email"]
    #     picture = userinfo_response.json()["picture"]
    #     users_name = userinfo_response.json()["name"]
    # else:
    #     return "User email not available or not verified by Google.", 400
    #
    # user = User(unique_id, users_name, users_email, picture)
    #
    # exists = db.session.query(
    #     db.session.query(User).filter_by(id=unique_id).exists()
    # ).scalar()
    #
    # if exists:
    #     dbUser = User.query.filter_by(id=unique_id).first()
    #     if dbUser.profile_pic != picture:
    #         dbUser.profile_pic = picture
    #         db.session.commit()
    #     if dbUser.username != users_name:
    #         dbUser.username = users_name
    #         db.session.commit()
    #     login_user(user)
    #     return redirect(url_for("index"))
    # else:
    #     db.session.add(user)
    #     db.session.commit()
    #     login_user(user)
    #     return redirect(url_for("index"))


@app.route('/get_kurslist', methods=['POST'])
def get_kourselist():
    division_id = request.form['division_id']
    kurslist_request = base_request + str(division_id) + '/' + 'kurslist'
    kurslist_response = ast.literal_eval(requests.get(kurslist_request).text)
    res = make_response(jsonify({'data': render_template('kurslist.html', kurs_list=kurslist_response)}))
    res.delete_cookie('division_id')
    res.delete_cookie('kurs')
    res.delete_cookie('group')
    res.set_cookie('division_id', division_id)
    return res


@app.route('/get_grouplist', methods=['POST'])
def get_grouplist():
    division_id = request.cookies.get('division_id')
    kurs = request.form['kurs']
    grouplist_request = base_request + str(division_id) + '/' + str(kurs) + '/' + 'grouplist'
    grouplist_response = ast.literal_eval(requests.get(grouplist_request).text)
    res = make_response(jsonify({'data': render_template('grouplist.html', group_list=grouplist_response)}))
    res.set_cookie('kurs', kurs)
    return res


@app.route('/print_student_schedule', methods=['POST'])
def print_student_schedule():
    group = request.form['group']
    weekstart = dtc.current_week_start_ms()
    schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
    schedule_response = requests.get(schedule_request).json()
    res = make_response(jsonify({'data': render_template('table.html', schedule=schedule_response)}))
    res.set_cookie('group', group)
    return res


@app.route("/logout")
@login_required
def logout():
    logout_user()
    if 'credentials' in flask.session:
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])
        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                               params={'token': credentials.token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})

    return redirect(url_for("index"))


def get_divisionlist():
    divisions_request = base_request + 'divisionlistforstuds'

    divisions_response = ast.literal_eval(requests.get(divisions_request).text)

    return divisions_response


def get_google_provider_cfg():
    return requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
