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

from flaskr.auth import login_required
from flaskr.models import Revision
from flaskr.db import get_db
from flaskr.utils import DATE_FORMAT
from datetime import datetime

bp = Blueprint("revisions", __name__, url_prefix="/revisions")


@bp.route("/")
def index():
    revisions = Revision.query.all()
    return jsonify([r.serialize() for r in revisions])


@bp.route("/api/details")
def details():
    args = request.args
    r = Revision.query.filter_by(path=args["filename"]).first()
    long = args.get("contents", False)
    return jsonify(r.serialize(long=long) if r else None)


@bp.route("/api/<int:id>")
@bp.route("/<int:id>")
def show(id):
    r = get_revision(id)
    return jsonify(r.serialize(long=True) if r else None)


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


@bp.route("/api/create", methods=["POST"])
def create():
    # To get data fields, use get_json()
    data = request.get_json()

    # ideally, we'd be able to clean the data fields!!
    # but no changeset here
    path = data.get("path", None)
    last_modified = data.get("last_modified", None)
    hash = data.get("hash", None)
    contents = data.get("contents", None)

    print("last modified:", last_modified)
    print("hash:", hash)
    if not path or not last_modified or not hash or not contents:
        return {"status": "error", "message": "Error: you must have all the fields"}

    # convert types (everything else is string)
    last_modified = datetime.strptime(last_modified, DATE_FORMAT)

    # does it exist already?
    # TODO: also, you might have to filter by user, once we make token_required
    # TODO: right now, we directly modify the row... but it might to be good to have it update
    db = get_db()

    b = Revision.query.filter(Revision.path == path).first()
    if not b:
        r = Revision(
            path=path,
            body=contents,
            last_modified=last_modified,
            content_hash=hash,
            user_id=1,
        )
        db.session.add(r)
    else:
        b.body = contents
        b.last_modified = last_modified
        b.content_hash = hash
    db.session.commit()
    return {"status": "success"}
