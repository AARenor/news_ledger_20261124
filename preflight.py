#!/usr/bin/env python3
"""Check this repository against the news image bounty rules before submitting."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 1024 * 1024
SIZE = (1024, 1024)


def check(label: str, condition: bool, detail: str = "") -> bool:
    print(("PASS " if condition else "FAIL ") + label + (": " + detail if detail else ""))
    return condition


def main() -> int:
    ok = True
    program = ROOT / "main.py"
    ok &= check("program at main.py", program.is_file())

    image = ROOT / "entry.png"
    raw = image.read_bytes() if image.is_file() else b""
    ok &= check("image under 1 MiB", 0 < len(raw) <= MAX_BYTES, f"{len(raw)} bytes")
    try:
        with Image.open(image) as opened:
            opened.verify()
        with Image.open(image) as opened:
            fmt, dimensions = opened.format, opened.size
        ok &= check("image format PNG or JPEG", fmt in {"PNG", "JPEG"}, str(fmt))
        ok &= check("image is 1024 by 1024", dimensions == SIZE, str(dimensions))
    except Exception as exc:
        ok &= check("image decodes", False, type(exc).__name__)

    license_text = (ROOT / "LICENSE").read_text(errors="replace")
    ok &= check("OSI license line", "SPDX-License-Identifier: MIT" in license_text)

    owner = ROOT / ".makefun" / "owner.json"
    try:
        wallet = json.loads(owner.read_text()).get("wallet", "")
        ok &= check("payout wallet recorded", bool(wallet), str(len(wallet)) + " chars")
    except Exception:
        ok &= check("payout wallet recorded", False)

    with tempfile.TemporaryDirectory() as directory:
        environment = dict(os.environ, MAKEFUN_OUTPUT_DIR=directory)
        result = subprocess.run([sys.executable, str(program)], env=environment, check=True)
        first = hashlib.sha256(Path(directory, "entry.png").read_bytes()).hexdigest()
        subprocess.run([sys.executable, str(program)], env=environment, check=True)
        second = hashlib.sha256(Path(directory, "entry.png").read_bytes()).hexdigest()
        ok &= check("two runs write identical bytes", first == second, first[:12])
        ok &= check("output matches repository image", first == hashlib.sha256(raw).hexdigest())

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
