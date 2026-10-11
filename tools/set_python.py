# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for GitHub Copilot
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Point the plugin's MCP server at a different Python command, for Windows (or any system without `python3`).

mcp.json starts the server as `python3`. On Windows the python.org installer provides `python` and `py`, not `python3`.
Run this once in your clone, BEFORE adding it as a marketplace:

  python tools/set_python.py python        # or: py   |   python3   |   "C:/Path To/python.exe"

Then: `copilot plugin marketplace add ./spindoctor-qwerty-copilot` and
`copilot plugin install spindoctor-qwerty@spindoctor-qwerty-copilot`. Plugins from a local marketplace load live from the clone.
It edits only mcp.json, prints what it changed, and `python3` restores the original byte for byte. Standard library only.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print(__doc__); return 2
    new = sys.argv[1].strip().replace("\\", "/")
    if any(c in new for c in '"\'`$;&|<>\n'):
        print("refusing: the command must be a plain program name or path"); return 2
    p = os.path.join(ROOT, "mcp.json")
    mcp = json.load(open(p, encoding="utf-8"))
    srv = mcp["mcpServers"]["spindoctor-qwerty"]; old = srv["command"]; srv["command"] = new
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(mcp, indent=2) + "\n")
    print("mcp.json: command %r -> %r" % (old, new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
