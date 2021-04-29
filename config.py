import os
from dotenv import load_dotenv
load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or 'this is the default secret key, change it now!'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'default.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_ID = os.getenv('GOOGLE_ID')
    GOOGLE_SECRET = os.getenv('GOOGLE_SECRET')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    UPLOAD_FOLDER = os.path.join(basedir, 'photos')
    USE_SESSION_FOR_NEXT = True
