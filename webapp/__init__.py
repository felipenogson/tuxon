from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_qrcode import QRcode
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'google.login'
login.login_message= 'Welcome back, good luck in your egg hunting'
csrf = CSRFProtect(app)
qrcode = QRcode(app)

from webapp import routes, models

