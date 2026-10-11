# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for GitHub Copilot
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""GitHub Copilot CLI host check. Standard library only (Python 3.8+); no GitHub account, no sign-in, no API key, no model.

1. Static: plugin.json and mcp.json against the Agent Plugins 1.1.0 rules (closed field sets, $schema, name constraints,
   stdio server under ${PLUGIN_ROOT}, workspace under ${PLUGIN_DATA}), .github/plugin/marketplace.json (name, owner, one
   entry with source "./"), the custom agent and 4 slash commands under com.github.copilot/, the skill, no hooks, text only,
   tools/set_python.py round trip.
2. With the REAL Copilot CLI (COPILOT=/path/to/copilot, or `copilot` on PATH) in a throw-away HOME: `copilot plugin
   marketplace add <repo>`, `plugin install spindoctor-qwerty@spindoctor-qwerty-copilot`, `plugin list --json`, `mcp get`,
   `skill list`, `plugin disable/enable`. Then BYOK mode (documented: no GitHub authentication needed) pointed at
   tests/stub_llm.py, a local scripted OpenAI-compatible endpoint (not an LLM, no key): `copilot -p --allow-all-tools`
   offers the 6 plugin MCP tools and EXECUTES scripted calls (function table, Bell script, preset qc-001, chat-history theory
   test) through the plugin's server; `--agent spindoctor-qwerty:spindoctor-qwerty-helper` runs the custom agent with its
   prompt and the MCP tools. Finally `plugin uninstall` and `marketplace remove`. Every CLI run gets
   DBUS_SESSION_BUS_ADDRESS=disabled: so no session-bus daemon is started (on headless Linux each run otherwise leaves one).
3. End-to-end: tests/e2e_mcp.py through the server as mcp.json declares it (${PLUGIN_ROOT}/${PLUGIN_DATA} expanded).

usage: python3 tests/copilot_host_check.py [REPO_DIR]"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
S11 = "https://agent-plugins.org/schemas/1.1.0/"
PLUGIN_ID = "spindoctor-qwerty@spindoctor-qwerty-copilot"
TOOLS = ["spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_functions", "spindoctor_test_theory"]
TEXT = (".py", ".md", ".json", ".txt", ".csv", ".html", ".q", "")


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", open(path, encoding="utf-8").read(), re.S)
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.+)$", m.group(1), re.M)) if m else None


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def snapshot(root):
    return {os.path.relpath(os.path.join(r, f), root): open(os.path.join(r, f), "rb").read() for r, ds, fs in os.walk(root) if "__pycache__" not in r for f in fs}


def main():
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True; mode = "host-simulated"

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    load = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
    pj = load(repo, "plugin.json"); mj = load(repo, "mcp.json"); mk = load(repo, ".github", "plugin", "marketplace.json")
    allowed = {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}
    n = pj.get("name", "")
    T("plugin.json: Agent Plugins 1.1.0 $schema, closed field set, name constraints, author, GPL-3.0-or-later, version 1.1.0",
      pj.get("$schema") == S11 + "plugin.schema.json" and set(pj) <= allowed and re.match(r"^[a-z0-9]([a-z0-9.-]{0,62}[a-z0-9])?$", n) and "--" not in n and ".." not in n
      and set(pj["author"]) <= {"name", "email", "url"} and pj["author"]["name"] == "RUSSELL PHILIP SMITHSON" and pj["license"] == "GPL-3.0-or-later" and pj["version"] == "1.1.0"
      and all(isinstance(k, str) for k in pj["keywords"]), pj)
    s = mj["mcpServers"]["spindoctor-qwerty"]
    T("mcp.json: same Agent Plugins version, closed envelope, stdio server under ${PLUGIN_ROOT}, workspace under ${PLUGIN_DATA}",
      mj.get("$schema") == S11 + "mcp.schema.json" and set(mj) == {"$schema", "mcpServers"} and s["type"] == "stdio" and s["command"] == "python3"
      and s["args"] == ["${PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py"] and os.path.isfile(s["args"][0].replace("${PLUGIN_ROOT}", repo))
      and s["env"]["SPINDOCTOR_WORKSPACE"] == "${PLUGIN_DATA}/workspace" and all(isinstance(v, str) for v in s["env"].values()), mj)
    e = (mk.get("plugins") or [{}])[0]
    T(".github/plugin/marketplace.json: kebab-case name, owner.name, one entry (source \"./\") matching the plugin",
      re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", mk.get("name", "")) and mk["owner"].get("name") and len(mk["plugins"]) == 1 and e["name"] == n and e["source"] == "./"
      and e["version"] == pj["version"] and e["license"] == pj["license"], mk)
    ag = frontmatter(os.path.join(repo, "com.github.copilot", "agents", "spindoctor-qwerty-helper.agent.md"))
    cd = os.path.join(repo, "com.github.copilot", "commands"); cmds = sorted(os.listdir(cd)); cfm = {f: frontmatter(os.path.join(cd, f)) for f in cmds}
    sk = frontmatter(os.path.join(repo, "skills", "spindoctor-qwerty", "SKILL.md"))
    T("com.github.copilot: agent (name, description, tools incl. spindoctor-qwerty/*), 4 commands with descriptions; skill name = folder",
      ag and ag.get("name") == "spindoctor-qwerty-helper" and ag.get("description") and "spindoctor-qwerty/*" in ag.get("tools", "")
      and cmds == ["qwerty-functions.md", "qwerty-preset.md", "qwerty-run.md", "qwerty-theory.md"] and all(m and m.get("description") for m in cfm.values())
      and sk and sk.get("name") == "spindoctor-qwerty", (ag, cfm, sk))
    allmd = "".join(open(os.path.join(cd, f), encoding="utf-8").read() for f in cmds) + open(os.path.join(repo, "skills", "spindoctor-qwerty", "SKILL.md"), encoding="utf-8").read()
    T("no other host's variables in commands/skill; honest limits (not a quantum computer, 298, 59); chat-theory confirmation",
      not re.search(r"CLAUDE_|CODEBUDDY|CURSOR_", allmd) and "not a quantum computer" in allmd.replace("\n", " ") and "298" in allmd and "59" in allmd and "confirm" in allmd)
    T("no hooks, no LSP, no legacy manifests competing with the root Agent Plugins manifest",
      not os.path.exists(os.path.join(repo, "com.github.copilot", "hooks")) and not os.path.exists(os.path.join(repo, "com.github.copilot", "lsp.json"))
      and not any(os.path.exists(os.path.join(repo, d, "plugin.json")) for d in (".plugin", ".claude-plugin", os.path.join(".github", "plugin"))))
    bad = [os.path.relpath(os.path.join(r, f), repo) for r, ds, fs in os.walk(repo) if ".git" not in r.split(os.sep) and "__pycache__" not in r
           for f in fs if os.path.splitext(f)[1].lower() not in TEXT and not (f.endswith(".pdf") and r.endswith(os.path.join("examples", "theory")))]
    T("only text files (sample PDFs are generated by make_sample_pdfs.py and git-ignored)", not bad, bad)
    tmp = tempfile.mkdtemp(prefix="sdq_cop_"); cp = os.path.join(tmp, "r"); shutil.copytree(repo, cp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    before = snapshot(cp); sp = os.path.join(cp, "tools", "set_python.py")
    r1 = subprocess.run([sys.executable, sp, "python"], stdout=subprocess.PIPE, text=True); mid = load(cp, "mcp.json")["mcpServers"]["spindoctor-qwerty"]["command"]
    r2 = subprocess.run([sys.executable, sp, "python3"], stdout=subprocess.PIPE, text=True); r3 = subprocess.run([sys.executable, sp, "py; rm -rf /"], stdout=subprocess.PIPE, text=True)
    T("tools/set_python.py: 'python' rewrites mcp.json, 'python3' restores byte-for-byte, shell metacharacters refused",
      r1.returncode == 0 and mid == "python" and r2.returncode == 0 and snapshot(cp) == before and r3.returncode == 2, (r1.stdout, r3.stdout))

    root = repo; data = os.path.join(tmp, "plugin_data")
    cop = os.environ.get("COPILOT") or shutil.which("copilot")
    if cop:
        mode = "real GitHub Copilot CLI (BYOK, model = local scripted stub)"
        home = os.path.join(tmp, "home"); os.makedirs(home); proj = os.path.join(tmp, "project"); os.makedirs(proj)
        env = dict(os.environ, HOME=home, DBUS_SESSION_BUS_ADDRESS="disabled:", COPILOT_AUTO_UPDATE="false")
        for k in [k for k in env if k.startswith(("COPILOT_PROVIDER", "GITHUB_TOKEN", "GH_TOKEN", "COPILOT_GITHUB_TOKEN", "COPILOT_HOME"))]: env.pop(k)

        def run(*a, **k):
            return subprocess.run([cop] + list(a), env=k.pop("env", env), cwd=k.pop("cwd", home), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
        v = run("--version").stdout.strip().splitlines()[0]
        r = run("plugin", "marketplace", "add", repo)
        T("%s: copilot plugin marketplace add <repo>" % v, r.returncode == 0 and "spindoctor-qwerty-copilot" in r.stdout and "added" in r.stdout, r.stdout)
        r = run("plugin", "install", PLUGIN_ID)
        T("copilot plugin install %s (Agent Plugins 1.1.0 accepted)" % PLUGIN_ID, r.returncode == 0 and "installed successfully" in r.stdout, r.stdout)
        r = run("plugin", "list", "--json")
        try: it = next(x for x in json.loads(r.stdout[r.stdout.index("["):]) if x.get("name") == "spindoctor-qwerty")
        except Exception: it = {}
        T("copilot plugin list --json: 1.1.0, enabled, from the spindoctor-qwerty-copilot marketplace", it.get("version") == "1.1.0" and it.get("enabled") is True and it.get("marketplace") == "spindoctor-qwerty-copilot", r.stdout)
        if it.get("installedFrom") and os.path.isdir(it["installedFrom"]): root = it["installedFrom"]
        r = run("mcp", "get", "spindoctor-qwerty")
        T("copilot mcp get: plugin server (local stdio, spindoctor_mcp.py, PLUGIN_ROOT/PLUGIN_DATA exported)",
          "Source plugin: spindoctor-qwerty (1.1.0)" in r.stdout and "spindoctor_mcp.py" in r.stdout and "PLUGIN_DATA" in r.stdout and "Type: local" in r.stdout, r.stdout)
        r = run("skill", "list")
        T("copilot skill list: the skill + the 4 slash commands", all(x in r.stdout for x in ("spindoctor-qwerty -", "qwerty-functions -", "qwerty-preset -", "qwerty-run -", "qwerty-theory -")), r.stdout[:600])
        rd = run("plugin", "disable", "spindoctor-qwerty"); l1 = run("plugin", "list", "--json").stdout
        re_ = run("plugin", "enable", "spindoctor-qwerty"); l2 = run("plugin", "list", "--json").stdout
        T("copilot plugin disable / enable", rd.returncode == 0 and re_.returncode == 0 and '"enabled": false' in l1 and '"enabled": true' in l2, (rd.stdout, re_.stdout, l1))
        port = free_port(); log = os.path.join(tmp, "stub.jsonl"); script = os.path.join(tmp, "script.json")
        P = "spindoctor-qwerty-"
        steps = [{"tool": P + "spindoctor_functions", "args": {"section": "commands"}},
                 {"tool": P + "spindoctor_run_script", "args": {"script": "q.circuit new bell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z"}},
                 {"tool": P + "spindoctor_run_preset", "args": {"preset_id": "qc-001"}},
                 {"tool": P + "spindoctor_test_theory", "args": {"action": "run", "source": "chat", "text": "Claim: H then CX gives a Bell state; P(00)=P(11)=0.5.",
                  "excerpts": ["User: so H then CX should split 00 and 11 evenly?", "Assistant: yes, about half each"],
                  "hypothesis": "H on qubit 0 then CX(0,1) prepares a Bell state.", "prediction": "P(11) = 0.5 within shot noise.",
                  "script": "q.circuit new t 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 2000 basis z",
                  "checks": [{"kind": "probability", "outcome": "11", "expected": 0.5, "tolerance": 0.05}]}},
                 {"text": "FINAL-DONE"}]
        json.dump(steps, open(script, "w"))
        benv = dict(env, COPILOT_PROVIDER_BASE_URL="http://127.0.0.1:%d/v1" % port, COPILOT_MODEL="stub")
        stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(port), log, script])
        flat = lambda x: x if isinstance(x, str) else json.dumps(x)
        try:
            time.sleep(1.0)
            r = run("-p", "show the SpinDoctor functions, run a Bell pair, preset qc-001 and test our theory", "--allow-all-tools", env=benv, cwd=proj)
            recs = [json.loads(l) for l in open(log) if l.strip()] if os.path.isfile(log) else []; ag_ = [x for x in recs if x["tools"]]
            T("copilot -p (BYOK, no GitHub sign-in): the model is offered the 6 plugin MCP tools (spindoctor-qwerty-*) and the skill tool",
              r.returncode == 0 and "FINAL-DONE" in r.stdout and ag_ and all(P + t in ag_[0]["tools"] for t in TOOLS) and "skill" in ag_[0]["tools"], (r.stdout[-400:], ag_[0]["tools"] if ag_ else None))
            res = ag_[-1]["tool_results"] if ag_ else []
            pdfs = [p for p in re.findall(r"[^\"\s\\]+?\.pdf", " ".join(flat(x) for x in res)) if os.path.isabs(p)]
            T("Copilot CLI executed 4 MCP tool calls through the plugin's server: table, Bell, qc-001, chat-history theory (supported); PDFs on disk",
              len(res) == 4 and "| Function | What it does | Command to type |" in flat(res[0]) and "q.circuit" in flat(res[1]) and "qc-001" in flat(res[2])
              and "supported" in flat(res[3]) and len(pdfs) >= 6 and any("theory" in p.lower() for p in pdfs) and all(os.path.isfile(p) for p in pdfs),
              {"n": len(res), "res": [flat(x)[:200] for x in res], "pdfs": pdfs[:4]})
            stub.kill(); stub.wait(); open(log, "w").close(); json.dump([{"text": "FINAL-DONE"}], open(script, "w"))
            stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(port), log, script]); time.sleep(1.0)
            r = run("-p", "hi", "--agent", "spindoctor-qwerty:spindoctor-qwerty-helper", "--allow-all-tools", env=benv, cwd=proj)
            recs = [json.loads(l) for l in open(log) if l.strip()]; ag_ = [x for x in recs if x["tools"]]
            T("copilot --agent spindoctor-qwerty:spindoctor-qwerty-helper: the agent's prompt is the system prompt and it gets the 6 MCP tools",
              r.returncode == 0 and ag_ and "You are the SpinDoctor Qwerty helper" in (ag_[0]["system"] or "") and all(P + t in ag_[0]["tools"] for t in TOOLS), (r.stdout[-300:], ag_[0]["tools"] if ag_ else None))
        finally:
            stub.kill()
        r = run("plugin", "uninstall", "spindoctor-qwerty"); r2 = run("plugin", "marketplace", "remove", "spindoctor-qwerty-copilot")
        T("copilot plugin uninstall + marketplace remove", r.returncode == 0 and r2.returncode == 0 and "spindoctor-qwerty" not in run("plugin", "list").stdout.replace("spindoctor-qwerty-copilot", ""), (r.stdout, r2.stdout))
    else:
        print("SKIP real Copilot CLI not found (set COPILOT=/path/to/copilot)")
    sub = lambda x: x.replace("${PLUGIN_ROOT}", root).replace("${PLUGIN_DATA}", data)
    cmd = [os.environ.get("SPINDOCTOR_PYTHON") or s["command"]] + [sub(a) for a in s["args"]]
    env2 = dict(os.environ, **{k: sub(v) for k, v in s.get("env", {}).items()}); env2.update(PLUGIN_ROOT=root, PLUGIN_DATA=data)
    ex = os.path.join(root, "skills", "spindoctor-qwerty", "examples", "theory")
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server"] + cmd + ["--examples", ex, "--out", os.path.join(tmp, "e2e_results.json")], env=env2)
    T("end-to-end through the server declared in mcp.json", r.returncode == 0)
    print("HOST-CHECK (%s)" % mode, "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
