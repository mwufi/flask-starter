from flask import Blueprint, g, redirect, url_for, request, jsonify

from flaskr.models import Revision
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint("revisions", __name__, url_prefix="/revisions")


@bp.route("/")
def index():
    revisions = Revision.query.all()
    return jsonify([r.serialize() for r in revisions])


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
    last_modified = datetime.strptime(last_modified, "%m/%d %H:%M:%S %p")

    # does it exist already?
    # TODO: find the revisions with the same path!
    # TODO: also, you might have to filter by user, once we make token_required
        
    # create our new revision
    r = Revision(
        path=path,
        body=contents,
        last_modified=last_modified,
        content_hash=hash,
        user_id=1,
    )
    db = get_db()
    db.session.add(r)
    db.session.commit()
    return {"status": "success"}
