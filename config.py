import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    # GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    # GOOGLE_DISCOVERY_URL = (
    #     "https://accounts.google.com/.well-known/openid-configuration"
    # )
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    API_SERVICE_NAME = 'calendar'
    API_VERSION = 'v3'
    SSL_CONTEXT = 'adhoc'
    DEBUG = True
    CELERY_BROKER_URL = 'redis://'
    CELERY_RESULT_BACKEND = 'redis://'
