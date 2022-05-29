from flaskr.auth import login_required
from flask import Blueprint, g, render_template, redirect, url_for, request
from flaskr.models import User

bp = Blueprint("users", __name__, template_folder="templates")


@bp.route("/community")
@login_required
def index():
    users = User.query.all()
    return render_template("users/index.html", users=users)
