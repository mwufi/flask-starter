from pathlib import Path
from datetime import datetime, timedelta
import hashlib
from typing import Optional
from dataclasses import dataclass
import asyncio
import requests
import json
import pytz

BUF_SIZE = 2**15
notes_path = Path("/Users/aii/02_Notes/Opal/Actual/")
SERVER_API = "http://localhost:5000/revisions/api"
DATE_FORMAT = "%c"


def hash_content(file):
    md5 = hashlib.md5()
    with open(file, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


@dataclass
class FileData:
    # a class that stores information about a local file
    path: Path
    last_modified: datetime
    hash: str
    contents: str = None


# a map of filenames to details
_mock_server = {}


async def get_server_details(file: FileData, with_contents=False) -> Optional[FileData]:
    """Returns the last known locations"""
    key = file.path.relative_to(notes_path)
    # return _mock_server.get(key, None)

    payload = {"filename": key, "contents": with_contents}

    x = requests.get(SERVER_API + "/details", payload).json()
    if not x:
        return None

    path = x["path"]
    last_modified = datetime.strptime(x["last modified"], DATE_FORMAT).replace(
        tzinfo=pytz.UTC
    )
    content_hash = x["content hash"]
    contents = x.get("body") if with_contents else None
    return FileData(path, last_modified, content_hash, contents)


async def sync_file(file: FileData) -> bool:
    """Upload file to server"""
    # for now, store the details in a dict
    key = file.path.relative_to(notes_path)
    _mock_server[key] = file

    # load the file contents?
    with open(file.path) as f:
        contents = f.read()
        print(contents)

    # for now, upload test contents!!
    o = {
        "path": key,
        "last_modified": file.last_modified.strftime(DATE_FORMAT),
        "hash": file.hash,
        "contents": contents,
    }
    json_o = json.loads(json.dumps(o, default=str))
    x = requests.post(SERVER_API + "/create", json=json_o)
    if x.status_code != 200:
        print(x.json())
    print("synced - ", key)
    return True


def overwrite_local(local: FileData, full_file: FileData) -> bool:
    """Update local contents & hash

    Actually, one bad thing about this is that if you update it,
    the metadata becomes newer. so then next time, it'll sync to the server!
    """
    # TODO: how do we know if it successfully wrote the file?
    with open(local.path, "w") as f:
        f.write(full_file.contents)

    key = local.path.relative_to(notes_path)
    print("downloaded - ", key)
    return True


async def maybe_sync_file(file: FileData, force=False) -> bool:
    """We pass in a filepath. It'll know what to do

    Returns: a boolean indicating whether we synced it or not
    """
    last_sync = await get_server_details(file)
    if not last_sync or force:
        return await sync_file(file)

    one_second = timedelta(seconds=1)
    if last_sync.last_modified < file.last_modified - one_second:
        print("local update!")
        return await sync_file(file)

    if file.last_modified < last_sync.last_modified - one_second:
        print(
            "remote update!",
            file.last_modified.strftime(DATE_FORMAT),
            last_sync.last_modified.strftime(DATE_FORMAT),
        )
        full_file = await get_server_details(file, with_contents=True)
        overwrite_local(file, full_file)

    if last_sync.hash != file.hash:
        print("hash differ")
        return await sync_file(file)

    return False


def current_sync():
    """Creates a "checkpoint", which is the timestamp of the current sync

    If there are revisions on the server which are older than the checkpoint,
    this must be bc 1) we failed to sync it (unlikely), or 2) they should be
    deleted!

    This makes it easier to recognize, on the server, which files have been
    deleted locally!
    """

    # Step 1: local --> remote
    o = {
        "time": datetime.utcnow(),
    }
    json_o = json.loads(json.dumps(o, default=str))
    x = requests.post(SERVER_API + "/checkpoint", json=json_o)
    if x.status_code != 200:
        print(x.json())
    else:
        print("[File tree] local --> remote!")


async def main():
    for t in notes_path.glob("**/*.md"):
        stat = t.stat()
        metadata_modified_at = datetime.fromtimestamp(stat.st_ctime).astimezone(
            pytz.UTC
        )
        content_hash = hash_content(t)

        filedata = FileData(t, metadata_modified_at, content_hash)

        # sync file?
        await maybe_sync_file(filedata)

    current_sync()


if __name__ == "__main__":
    asyncio.run(main())
