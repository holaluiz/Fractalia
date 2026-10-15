"""Download every file of a public Google Drive folder (Quaternius legacy packs) into a new directory.

Usage: python drive_download.py <folder_id> <out_dir>
"""
import html
import os
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def list_folder(folder_id):
    page = get(f"https://drive.google.com/embeddedfolderview?id={folder_id}").decode("utf-8", "replace")
    ids = re.findall(r'id="entry-([\w-]+)"', page)
    titles = [html.unescape(t) for t in re.findall(r'class="flip-entry-title">([^<]+)<', page)]
    return list(zip(ids, titles))


def main():
    folder_id, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    entries = list_folder(folder_id)
    total = 0
    for fid, name in entries:
        if not name.lower().endswith(".fbx"):
            continue
        dest = os.path.join(out, os.path.basename(name))
        if os.path.exists(dest):
            continue
        data = None
        for attempt in range(5):  # Drive throttles bursts with an HTML page: back off and retry
            data = get(f"https://drive.usercontent.google.com/download?id={fid}&export=download")
            if not (data[:15].lower().startswith(b"<!doctype html") or data[:5] == b"<html"):
                break
            data = None
            time.sleep(3 * (attempt + 1))
        time.sleep(0.8)
        if data is None:
            print("  still throttled:", name)
            continue
        with open(dest, "wb") as f:
            f.write(data)
        total += len(data)
    files = [f for f in os.listdir(out) if f.lower().endswith(".fbx")]
    print(f"{out}: {len(files)} fbx, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
