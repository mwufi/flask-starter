from flask import Blueprint, flash, g, render_template, redirect, url_for, request
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.models import Post, User

bp = Blueprint("blog", __name__, url_prefix="/blog")


@bp.route("/")
def index():
    db = get_db()
    posts = (
        db.session.query(
            Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username
        )
        .join(User, User.id == Post.author_id)
        .order_by(Post.created)
    )
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            p = Post(title=title, body=body, author_id=g.user.id)
            db.session.add(p)
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_post(id, check_author=True):
    post = Post.query.get(id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            p = Post.query.get(id)
            if p is not None:
                p.title = title
                p.body = body
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    db = get_db()

    p = get_post(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("blog.index"))
