from pathlib import Path
from datetime import datetime, timedelta
import hashlib
from typing import Optional
from dataclasses import dataclass
import asyncio
import requests
import json

BUF_SIZE = 2**15
notes_path = Path("/Users/aii/02_Notes/Opal/Actual/")
SERVER_API = "http://localhost:5000/revisions"
date_format = "%Y/%m/%d %I:%M:%S %p"


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


# a map of filenames to details
_mock_server = {}


async def get_server_details(file: FileData) -> Optional[FileData]:
    """Returns the last known locations"""
    key = file.path.relative_to(notes_path)
    # return _mock_server.get(key, None)

    payload = {"filename": key}

    x = requests.get(SERVER_API + "/get", payload).json()
    if not x:
        return None

    last_modified = datetime.strptime(x["last modified"], date_format)
    return FileData(x["path"], last_modified, x["content hash"])


async def sync_file(file: FileData) -> bool:
    """Upload file to server"""
    # for now, store the details in a dict
    key = file.path.relative_to(notes_path)
    _mock_server[key] = file

    # for now, upload test contents!!
    o = {
        "path": key,
        "last_modified": file.last_modified.strftime(date_format),
        "hash": file.hash,
        "contents": "TEST contents",
    }
    json_o = json.loads(json.dumps(o, default=str))
    x = requests.post(SERVER_API + "/create", json=json_o)
    if x.status_code != 200:
        print(x.json())
    print("synced - ", key)
    return True


async def maybe_sync_file(file: FileData) -> bool:
    """We pass in a filepath. It'll know what to do

    Returns: a boolean indicating whether we synced it or not
    """
    last_sync = await get_server_details(file)
    if not last_sync:
        return await sync_file(file)

    thirty_seconds = timedelta(seconds=30)
    if last_sync.last_modified < file.last_modified - thirty_seconds:
        print("older file!", last_sync.last_modified, file.last_modified)
        return await sync_file(file)

    if last_sync.hash != file.hash:
        print("hash differ")
        return await sync_file(file)

    return False


async def main():
    for t in notes_path.glob("**/*.md"):
        stat = t.stat()
        metadata_modified_at = datetime.fromtimestamp(stat.st_ctime)
        content_hash = hash_content(t)

        filedata = FileData(t, metadata_modified_at, content_hash)

        # sync file?
        synced = await maybe_sync_file(filedata)

        _ = {
            "name": t.relative_to(notes_path),
            "last modified": metadata_modified_at,
            "hash": content_hash,
            "synced": synced,
        }


if __name__ == "__main__":
    asyncio.run(main())

for t in notes_path.glob("**/*.png"):
    print("Images:", t)
