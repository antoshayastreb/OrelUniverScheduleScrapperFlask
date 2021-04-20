import io
import tempfile

import flask

import googleapiclient.discovery
from app.google_auth import build_credentials, get_user_info


def build_calendar_api():
    credentials = build_credentials()
    return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
