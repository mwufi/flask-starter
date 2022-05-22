from flaskr.auth import login_required
from flask import Blueprint, g, render_template, redirect, url_for, request
from flaskr.models import Token
from flaskr.db import db
import secrets


def gen_secret():
    return secrets.token_hex()


bp = Blueprint("tokens", __name__, url_prefix="/tokens")


@bp.route("/")
@login_required
def index():
    tokens = Token.query.filter(Token.user_id == g.user.id).all()
    return render_template("tokens/index.html", tokens=tokens)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        name = request.form["name"] or "Untitled"

        t = Token(user_id=g.user.id, name=name, value=gen_secret())
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("tokens.index"))

    return render_template("tokens/create.html")


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    p = Token.query.filter(Token.id == id and Token.user_id == g.user.id)
    p.delete()
    db.session.commit()
    return redirect(url_for("tokens.index"))
