from flaskr.db import db
from datetime import datetime
import secrets


def gen_secret():
    return secrets.token_hex()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self) -> str:
        return "User %s" % self.username


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "Post %s" % self.title


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80), nullable=False, default=gen_secret())
    name = db.Column(db.String(80), nullable=True, default='New Token')

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "Token %s..." % (self.value[:10])
