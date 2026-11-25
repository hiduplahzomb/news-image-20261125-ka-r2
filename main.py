#!/usr/bin/env python3
"""news-image-20261125 entry (round 2): copy the rendered entry.png to the
output directory and verify its bytes. Standard library only.

The grader runs this twice; both runs must write identical bytes, so this
program only copies a fixed file and never generates anything.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(src, "rb") as fh:
        data = fh.read()
    if len(data) == 0 or len(data) > 1048576:
        print("entry.png has an unexpected size: %d bytes" % len(data),
              file=sys.stderr)
        return 1
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG", file=sys.stderr)
        return 1
    with open(dst, "wb") as fh:
        fh.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("entry.png: %d bytes, sha256 %s" % (len(data), digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
