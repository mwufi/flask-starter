from flaskr.db import db
from datetime import datetime
from flaskr.utils import DATE_FORMAT


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(80), nullable=False, server_default='Your Name')
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


class Checkpoint(db.Model):
    """Represents a time when you synced all your files!

    Then, any file before here means that you probably
    deleted it.
    """

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "Checkpoint %s" % (self.created.strftime("%c"))

    @staticmethod
    def latest_checkpoint():
        return Checkpoint.query.order_by(Checkpoint.created.desc()).first()


class Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content_hash = db.Column(db.String(80), nullable=False)

    last_checked = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "%s - %s" % (self.path, self.created.strftime("%m/%d %H:%M:%s %p"))

    def serialize(self, long=False):
        value = {
            "id": self.id,
            "path": self.path,
            "content hash": self.content_hash,
            "last checked": self.last_checked.strftime(DATE_FORMAT)
            if self.last_checked
            else "na",
            "last modified": self.last_modified.strftime(DATE_FORMAT),
            "user id": self.user_id,
        }
        if long:
            value["body"] = self.body
        return value
