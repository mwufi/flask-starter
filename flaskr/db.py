from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import click
from flask import current_app, g
from flask.cli import with_appcontext
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

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
    migrate.init_app(app, db)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
