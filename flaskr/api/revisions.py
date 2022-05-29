from datetime import datetime

from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required

from flaskr.db import get_db
from flaskr.models import Revision, Checkpoint


bp = Blueprint("revisions-api", __name__, url_prefix="/revisions/api")
DATE_FORMAT = "%c"


@bp.route("/checkpoint", methods=["POST"])
@jwt_required()
def checkpoint():
    c = Checkpoint(user_id=current_user.id)
    db = get_db()
    db.session.add(c)
    db.session.commit()

    return jsonify(status="Success")


@bp.route("/sync", methods=["POST"])
@jwt_required()
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
        return jsonify(status="Error", message="you must have all the fields"), 500

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
            user_id=current_user.id,
        )
        db.session.add(r)
    else:
        b.body = contents
        b.last_modified = last_modified
        b.content_hash = hash
    db.session.commit()

    return {"status": "success"}


@bp.route("/fetch")
def details():
    args = request.args
    r = Revision.query.filter_by(path=args["filename"]).first()

    if r is None:
        return {"status": "error", "message": "Stuff does not exist!"}, 404

    # If we call this endpoint, it's likely that it still exists
    # on client!! so we refresh it
    r.last_checked = datetime.utcnow()
    db = get_db()
    db.session.add(r)
    db.session.commit()

    long = args.get("contents", False)
    return jsonify(r.serialize(long=long) if r else None)


def get_revision(id, check_author=True):
    post = Revision.query.get(id)

    if post is None:
        abort(404, f"Revision id {id} doesn't exist.")

    # if check_author and post.author_id != g.user.id:
    #     abort(403)

    return post


@bp.route("/api/<int:id>")
def show_json(id):
    r = get_revision(id)
    return jsonify(r.serialize(long=True) if r else None)
