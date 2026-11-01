"""Build the webOS package for the Living Room launcher."""

import io
import os
import shutil
import tarfile

ROOT = os.path.dirname(os.path.abspath(__file__))
STAGE = os.path.join(ROOT, "tv-app")
DIST = os.path.join(ROOT, "dist")
APP_ID = "tv.livingroom.shell"
VERSION = "2.2.0"

APPINFO = """{
  "id": "tv.livingroom.shell",
  "version": "2.2.0",
  "vendor": "Living Room",
  "type": "web",
  "main": "index.html",
  "title": "Living Room",
  "icon": "icon.png",
  "largeIcon": "largeIcon.png",
  "bgColor": "#000000",
  "iconColor": "#f4f0e6",
  "disableBackHistoryAPI": true,
  "handlesRelaunch": true
}
"""

CONTROL = """Package: tv.livingroom.shell
Version: 2.2.0
Section: misc
Priority: optional
Architecture: all
Maintainer: Living Room <livingroom@localhost>
Description: Living Room launcher
"""


def make_icons():
    from PIL import Image, ImageDraw

    def draw(size):
        image = Image.new("RGB", (size, size), "#0c0c0b")
        pen = ImageDraw.Draw(image)
        margin = int(size * 0.16)
        pen.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=int(size * 0.16),
            fill="#f4f0e6",
        )
        left = int(size * 0.34)
        right = int(size * 0.66)
        top = int(size * 0.30)
        mid = int(size * 0.56)
        bottom = int(size * 0.76)
        pen.pieslice([left, top, right, top + (right - left)], 180, 360, fill="#0c0c0b")
        pen.rectangle([left, mid, right, bottom], fill="#0c0c0b")
        return image

    os.makedirs(STAGE, exist_ok=True)
    draw(80).save(os.path.join(STAGE, "icon.png"))
    draw(130).save(os.path.join(STAGE, "largeIcon.png"))


def tar_bytes(entries):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz", format=tarfile.USTAR_FORMAT) as archive:
        for name, data, mode in entries:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = mode
            info.mtime = 1707436800  # webOS 5 rejects zero-timestamp members
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def ar_member(name, data):
    header = (
        name.encode("ascii").ljust(16)
        + b"1707436800".ljust(12)
        + b"0".ljust(6)
        + b"0".ljust(6)
        + b"100644".ljust(8)
        + str(len(data)).encode("ascii").ljust(10)
        + b"`\n"
    )
    pad = b"\n" if len(data) % 2 else b""
    return header + data + pad


def main():
    make_icons()
    html_src = os.path.join(ROOT, "launcher", "index.html")
    html_dst = os.path.join(STAGE, "index.html")
    shutil.copyfile(html_src, html_dst)
    for extra in ("spelunkr.html", "spelunkr-channels.js"):
        shutil.copyfile(os.path.join(ROOT, "launcher", extra), os.path.join(STAGE, extra))
    logo_src = os.path.join(ROOT, "launcher", "logos")
    logo_dst = os.path.join(STAGE, "logos")
    if os.path.isdir(logo_dst):
        shutil.rmtree(logo_dst)
    shutil.copytree(logo_src, logo_dst)
    with open(os.path.join(STAGE, "appinfo.json"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(APPINFO)

    prefix = "usr/palm/applications/%s/" % APP_ID
    data_entries = [(prefix, b"", 0o755), (prefix + "logos/", b"", 0o755)]
    names = ["appinfo.json", "index.html", "spelunkr.html", "spelunkr-channels.js", "icon.png", "largeIcon.png"]
    logo_dir = os.path.join(STAGE, "logos")
    for filename in sorted(os.listdir(logo_dir)):
        if filename.endswith(".svg"):
            names.append("logos/" + filename)
    for filename in names:
        path = os.path.join(STAGE, filename.replace("/", os.sep))
        with open(path, "rb") as handle:
            data_entries.append((prefix + filename, handle.read(), 0o644))

    control_entries = [
        ("control", CONTROL.encode("utf-8"), 0o644),
    ]
    debian = b"2.0\n"
    package = b"!<arch>\n" + ar_member("debian-binary", debian)
    package += ar_member("control.tar.gz", tar_bytes(control_entries))
    package += ar_member("data.tar.gz", tar_bytes(data_entries))

    os.makedirs(DIST, exist_ok=True)
    ipk_path = os.path.join(DIST, "%s_%s_all.ipk" % (APP_ID, VERSION))
    with open(ipk_path, "wb") as handle:
        handle.write(package)
    print(ipk_path)


if __name__ == "__main__":
    main()
