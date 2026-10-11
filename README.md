# SpinDoctor Qwerty for GitHub Copilot

**GitHub Copilot CLI plugin for the SpinDoctor 3.1.2 quantum-circuit simulator.** It adds a skill, four slash commands, a custom
agent and a local MCP server with six tools to [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/copilot-cli/about-cli-plugins):
build and run `q.*` circuits (1-298 logical qubits), run the 241 built-in presets, process folders of command files with
`q.folder`, test theories from files, pasted text or the conversation itself, and get TXT, PDF, JSON and CSV reports. Everything
runs locally in a bundled, standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages).

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.

## What's in the plugin

The repo root is an [Agent Plugins](https://agent-plugins.org) **1.1.0** plugin (the newest version Copilot CLI recognizes) and a
one-plugin Copilot marketplace.

| Part | File | What it does |
|---|---|---|
| Manifest | `plugin.json` | Agent Plugins 1.1.0: name, version, author, license, keywords |
| MCP server | `mcp.json` | Starts `python3 ${PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py`; reports go to `${PLUGIN_DATA}/workspace` |
| Skill | `skills/spindoctor-qwerty/` | Instructions, honesty rules, the engine and its CLI |
| Slash commands | `com.github.copilot/commands/*.md` | `/qwerty-run`, `/qwerty-preset`, `/qwerty-functions`, `/qwerty-theory` (Copilot lists them as skills) |
| Custom agent | `com.github.copilot/agents/spindoctor-qwerty-helper.agent.md` | `spindoctor-qwerty:spindoctor-qwerty-helper`, limited to the SpinDoctor tools plus read/shell |
| Marketplace | `.github/plugin/marketplace.json` | Makes this repo the marketplace `spindoctor-qwerty-copilot` |
| Windows helper | `tools/set_python.py` | Switches `python3` to `python`, `py` or a full path |

No hooks, no LSP server, no network access, no telemetry. Nothing runs until you use a command or the model calls a tool.

## Install (GitHub Copilot CLI)

You need Copilot CLI and Python 3.8+ (as `python3` on macOS/Linux; see Windows below).

```sh
copilot plugin marketplace add LKVexa/spindoctor-qwerty-copilot
copilot plugin install spindoctor-qwerty@spindoctor-qwerty-copilot
```

Start a new session and ask *"show the SpinDoctor functions"*. Check the install with `copilot plugin list`, `copilot mcp get
spindoctor-qwerty` and `copilot skill list`; in a session, `/mcp` and `/plugin` show it. Run the agent with
`copilot --agent spindoctor-qwerty:spindoctor-qwerty-helper` (or pick it with `/agent`).

Manage it with `copilot plugin disable|enable|update|uninstall spindoctor-qwerty`. (Copilot CLI still accepts
`copilot plugin install LKVexa/spindoctor-qwerty-copilot`, but direct installs are deprecated: use the marketplace.)

**From a local clone:** `copilot plugin marketplace add ./spindoctor-qwerty-copilot`, then the same `install` line. Plugins from a
local marketplace load live from the clone, so edits take effect in the next session.

**Windows:** the python.org installer provides `python` and `py`, not `python3`. Clone the repo, run
`python tools/set_python.py python` (or `py`, or a full path to `python.exe`), then add the marketplace from that clone.
`python tools/set_python.py python3` restores the original file.

**VS Code / other Copilot surfaces:** VS Code's agent plugins and other Agent Plugins hosts read the same `plugin.json`, `skills/`
and `mcp.json`; the `com.github.copilot/` agent and commands are Copilot CLI extras. Only Copilot CLI was tested.

## Commands

| Command | What it does |
|---|---|
| `/qwerty-run <q.* commands>` | Runs q.* commands and summarises probabilities, counts and report paths |
| `/qwerty-preset <qc-NNN> [name=value ...]` | Runs one of the 241 presets |
| `/qwerty-functions [section] [filter]` | Shows the function table |
| `/qwerty-theory <file \| text \| "we discussed">` | Tests a theory and writes a theory test report |

Each command uses the `spindoctor_*` MCP tools (Copilot names them `spindoctor-qwerty-spindoctor_*`). If the server is disabled,
it falls back to the skill's CLI, `skills/spindoctor-qwerty/scripts/spindoctor_cli.py`.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" or `/qwerty-functions` |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Copilot CLI, @-mention the file or give its path on your computer.
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `skills/spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 skills/spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check with the **real Copilot CLI** | `COPILOT=$(command -v copilot) python3 tests/copilot_host_check.py` | 19/19 checks, end-to-end 12/12 |
| Same without Copilot CLI | `python3 tests/copilot_host_check.py` | 9/9 checks, end-to-end 12/12 |

**Real host, scripted model:** GitHub Copilot CLI 1.0.95 was installed from npm (`@github/copilot`) on a Linux test machine and
used **without a GitHub account or sign-in**. It added the marketplace, installed the plugin (Agent Plugins 1.1.0 accepted), listed
it enabled at 1.1.0, showed the plugin MCP server and the skill + 4 commands, disabled, re-enabled and uninstalled it. For the
session tests the check uses Copilot CLI's documented BYOK mode (`COPILOT_PROVIDER_BASE_URL`, which needs no GitHub authentication)
pointed at `tests/stub_llm.py`, a local scripted OpenAI-compatible endpoint (not an LLM, no API key). Through it, `copilot -p`
offered the six plugin tools and **executed** the function table, a Bell script, preset qc-001 and a chat-history theory test via
the plugin's MCP server, and `--agent spindoctor-qwerty:spindoctor-qwerty-helper` ran the custom agent. No real model was called,
so how well a given model uses the tools isn't tested. Details in [E2E_RESULTS.md](E2E_RESULTS.md).

On headless Linux each Copilot CLI run can leave a D-Bus session daemon behind; the check sets
`DBUS_SESSION_BUS_ADDRESS=disabled:` for every run. Do the same if you script Copilot CLI on a server.

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). `plugin.json` and `marketplace.json` carry the license and author.
GitHub and GitHub Copilot are trademarks of GitHub, Inc.; this project is not affiliated with GitHub.
