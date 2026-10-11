# Changelog

## 1.1.0 - 2026-10-10

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics (.qasm2/.circuit, skipped-file listing, compact status, 128 files /
  4 MiB / 128 commands / 4096 characters), CSV report copies and measurement-CSV fitting equations. All 241 presets replayed.
- New tools `spindoctor_functions` (in-chat function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or
  the chat history, with TXT+JSON+PDF theory reports).
- Manifests move to Agent Plugins **1.1.0** (`plugin.json` and `mcp.json`), the newest version Copilot CLI 1.0.95 recognizes.
- The repo root is now the plugin and a one-plugin marketplace (`.github/plugin/marketplace.json`), because Copilot CLI deprecates
  direct installs: `copilot plugin marketplace add LKVexa/spindoctor-qwerty-copilot`.
- The 1.0 skill had no slash commands: four commands (`com.github.copilot/commands/`) are added; Copilot lists them as skills.
- The custom agent is renamed `spindoctor-qwerty-helper.agent.md` and updated for 3.1.2.
- The empty `com.github.copilot/hooks/hooks.json` is removed: the plugin has no hooks.
- `mcp.json` keeps reports in `${PLUGIN_DATA}/workspace` and sets UTF-8 and no-bytecode.
- Skill and agent updated for 3.1.2 (298-qubit limit, q.folder, theory testing with user confirmation).
- New `tools/set_python.py` for Windows (`python` / `py` / full path) with a byte-for-byte restore.
- Tests: real Copilot CLI marketplace/install/list/mcp get/skill list/disable/enable/uninstall, BYOK sessions against a local
  scripted stub (tool execution + custom agent) and the full end-to-end suite.
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` folder with an Agent Plugins 1.0 manifest, skill, `mcp.json`, agent and an empty hooks file.
