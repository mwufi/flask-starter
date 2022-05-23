from flask import Blueprint, g, redirect, url_for, request, jsonify

from flaskr.models import Revision
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint("revisions", __name__, url_prefix="/revisions")


@bp.route("/")
def index():
    revisions = Revision.query.all()
    return jsonify([r.serialize() for r in revisions])


@bp.route("/get")
def details():
    args = request.args
    r = Revision.query.filter_by(path=args['filename']).first()
    return jsonify(r.serialize() if r else None) 


@bp.route("/create", methods=["POST"])
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
    last_modified = datetime.strptime(last_modified, "%Y/%m/%d %H:%M:%S %p")

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
