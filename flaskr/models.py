from flaskr.db import db
from datetime import datetime


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
    value = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=True, default="New Token")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "Token %s..." % (self.value[:10])


class Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content_hash = db.Column(db.String(80), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "%s - %s" % (self.path, self.created.strftime("%m/%d %H:%m %p"))

    def serialize(self):
        return {
            'path': self.path,
            'content hash': self.content_hash,
            'last modified': self.last_modified.strftime("%m/%d %H:%m %p"),
            'user id': self.user_id
        }