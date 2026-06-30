#!/usr/bin/env python3

"""
AutoCommit entry point.

It intentionally contains only platform dispatch logic. All LLM and Git
behavior now lives in autocommit_llm.py / auto_commit_mac.py /
auto_commit_windows.py so future platform additions stay minimal.
"""
from __future__ import annotations

import sys
import os
import subprocess


def main() -> None:
    platform = sys.platform
    script_dir = os.path.dirname(os.path.realpath(__file__))

    if platform.startswith("win"):
        script = os.path.join(script_dir, "auto_commit_windows.py")
    elif platform == "darwin":
        script = os.path.join(script_dir, "auto_commit_mac.py")
    else:
        # Default to the mac-style implementation on Linux
        script = os.path.join(script_dir, "auto_commit_mac.py")

    args = sys.argv[1:]
    result = subprocess.run([sys.executable, script] + args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
