from webapp import db, login
from datetime import datetime
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    postscoins = db.relationship('Postcoin', backref="user", lazy='dynamic')
    tuxcoins = db.relationship('Tuxcoin', backref="user", lazy='dynamic')
    # tuxcoins = db.relationship('Tuxcoin', )

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)

class Postcoin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(1024))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    url = db.Column(db.String(256), unique=True)
    token = db.Column(db.String(256), index=True, unique=True)
    img = db.Column(db.String(256))
    posted = db.Column(db.Boolean, default=False)
    void = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tuxcoins = db.relationship('Tuxcoin', backref="post", lazy='dynamic')

    def __repr__(self):
        return f'<Postcoin: {self.title}>'

class Tuxcoin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    void = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    postcoin_id = db.Column(db.Integer, db.ForeignKey('postcoin.id'))



