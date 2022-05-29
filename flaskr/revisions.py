from flask import (
    Blueprint,
    flash,
    abort,
    redirect,
    render_template,
    url_for,
    request,
    jsonify,
)

import markdown
import frontmatter

from flaskr.auth import login_required
from flaskr.models import Revision, Checkpoint
from flaskr.db import get_db
from flaskr.utils import DATE_FORMAT
from datetime import datetime, timedelta

bp = Blueprint("revisions", __name__, url_prefix="/revisions")


@bp.route("/")
def index():
    c = Checkpoint.latest_checkpoint()
    revisions = Revision.query.all()

    ten_seconds = timedelta(seconds=10)
    current_revisions = [
        r
        for r in revisions
        if r.last_checked and r.last_checked > c.created - ten_seconds
    ]
    potentially_deleted = [
        r
        for r in revisions
        if not r.last_checked or r.last_checked <= c.created - ten_seconds
    ]

    # return jsonify([r.serialize() for r in revisions])
    return render_template(
        "revisions/index.html",
        current_revisions=current_revisions,
        potentially_deleted=potentially_deleted,
    )


@bp.route("/<int:id>")
def show(id):
    r = get_revision(id)
    data = frontmatter.loads(r.body)
    html_contents = markdown.markdown(data.content)
    return render_template(
        "revisions/show.html",
        revision=r,
        html_contents=html_contents,
        metadata=data.metadata,
    )


@bp.route("/<int:id>/update", methods=["GET", "POST"])
def update(id):
    r = get_revision(id)
    if request.method == "POST":
        path = request.form["path"]
        body = request.form["body"]
        error = None

        if not path:
            error = "Path is required!"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            if r is not None:
                r.path = path
                r.body = body
                r.last_modified = datetime.utcnow()
                r.content_hash = "<tbd>"
                db.session.add(r)
                db.session.commit()
            else:
                print("no such thing!!")
            return redirect(url_for("revisions.show", id=id))
    return render_template("revisions/update.html", post=r)


def get_revision(id, check_author=True):
    post = Revision.query.get(id)

    if post is None:
        abort(404, f"Revision id {id} doesn't exist.")

    # if check_author and post.author_id != g.user.id:
    #     abort(403)

    return post


@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    db = get_db()

    p = get_revision(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("revisions.index"))
