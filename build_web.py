"""Assemble the deployable web build (web/) from the TV app in launcher/.

The TV app (launcher/) stays the single source of truth. This copies the
guide/player and its assets into web/ as app.html plus fonts, logos, and the
channel data. The landing page (web/index.html) and install guide
(web/install.html) are hand-authored and are NOT touched here.

Run: python build_web.py
"""

import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(ROOT, "launcher")
WEB = os.path.join(ROOT, "web")


def copy_tree(name):
    src = os.path.join(LAUNCHER, name)
    dst = os.path.join(WEB, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    os.makedirs(WEB, exist_ok=True)

    # The guide/player. On the web its "Back exits to Home" lands on web/index.html.
    shutil.copyfile(os.path.join(LAUNCHER, "spelunkr.html"), os.path.join(WEB, "app.html"))

    # Channel database (generated; see nost4lgia-src/build_channels.js).
    channels = os.path.join(LAUNCHER, "spelunkr-channels.js")
    if not os.path.exists(channels):
        raise SystemExit("Missing launcher/spelunkr-channels.js — run: node nost4lgia-src/build_channels.js")
    shutil.copyfile(channels, os.path.join(WEB, "spelunkr-channels.js"))

    copy_tree("fonts")
    copy_tree("logos")

    print("Wrote", WEB)
    for f in ("index.html", "install.html"):
        if not os.path.exists(os.path.join(WEB, f)):
            print("  note: web/%s not found (hand-authored page)" % f)


if __name__ == "__main__":
    main()
