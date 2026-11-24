#!/usr/bin/env python3
"""Write the bundled news image to the grader output path, byte for byte."""

import os
import shutil
from pathlib import Path


SOURCE = Path(__file__).resolve().parent / "entry.png"
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
# The grader reads entry.png by name, even though the bytes are a real PNG.
DESTINATION = OUTPUT_DIR / "entry.png"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, DESTINATION)


if __name__ == "__main__":
    main()
