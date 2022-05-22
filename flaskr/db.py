from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import click
from flask import current_app, g
from flask.cli import with_appcontext
from datetime import datetime

db = SQLAlchemy()


def get_db():
    if "db" not in g:
        g.db = db
    return g.db


def close_db(e=None):
    g.pop("db", None)
    print("SQL Alechemy will close it automatically")


def init_db():
    db = get_db()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo("Initialized the database")


def init_app(app):
    """Adds db methods to current app"""
    db.init_app(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


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
