from flaskr.auth import login_required
from flask import Blueprint, g, render_template, redirect, url_for, request
from flaskr.models import Token

bp = Blueprint("tokens", __name__, url_prefix="/tokens")


@bp.route("/")
@login_required
def index():
    tokens = Token.query.filter(Token.user_id == g.user.id).all()
    return render_template("tokens/index.html", tokens=tokens)
