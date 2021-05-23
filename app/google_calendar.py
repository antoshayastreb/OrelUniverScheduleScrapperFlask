import io
import tempfile

import flask

import googleapiclient.discovery
from app.google_auth import build_credentials, build_credentials_token, get_user_info


def build_calendar_api():
    credentials = build_credentials()
    return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)


def build_calendar_api_token(oauth2_tokens, refresh_token):
    credentials = build_credentials_token(oauth2_tokens, refresh_token)
    return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
