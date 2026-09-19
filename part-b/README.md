# Part B: DeepSeek Harness + Plugins

**Status**: Harness installed, Creator Mode confirmed, 2 custom plugins built
and verified end-to-end. Live agent run pending a `DEEPSEEK_API_KEY`.

## What DeepSeek Harness (DSH) actually is

DSH (`@deepseek-ai/dsh`, [github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness))
is DeepSeek's open-source coding-agent harness, built on **Cordis**, a
plugin/service framework (vendored in-repo): every capability — models,
tools, sessions, sandboxing, the UI — is a plugin row in a `cordis.yml`. A
**profile** (`web`, `headless`, `acp`, `sdk`) is a named, composed stack of
those plugin layers under `$DSH_HOME/profiles/<name>/`; you extend a profile
by adding plugin packages, which is exactly the "5-7 plugins, 2 from
scratch" assignment shape.

This isn't a toy repo — it's a real ~12k-file TypeScript monorepo with native
addons, a desktop app, and an i18n'd doc set. Verified directly (not taken on
faith): cloned `deepseek-ai/deepseek-harness`, confirmed `@deepseek-ai/dsh` is
published on npm (22 versions), and used the local source tree only to read
the authoritative docs (`docs/cordis-primer.md`, `docs/cookbook/adding-a-tool.md`,
`packages/core/tools/src/index.ts`) — it is **not** committed here
(`part-b/harness/` is gitignored; ~150MB of upstream source has no business
in this repo).

## Creator Mode

Creator Mode is not a separate install — it's a shipped **agent preset**
(`packages/preset/agent-presets/presets/cordis`), selectable in the `web`
profile's mode dropdown alongside `standard`/`minimal`/`ptc`. Read straight
from its persona config: "Creator adds persistent plugin management, runtime
inspection, composition-authoring skills... It exists so a person can ask an
agent to author another agent." It's what lets you ask the running agent
itself to scaffold and install a new plugin without leaving chat (the
`plugin_manager` tool + `cordis_inspect_list`/`cordis_inspect_query`).

## Setup performed

```sh
# pnpm wasn't on PATH and global npm/corepack writes were permission-denied,
# so pnpm was installed locally instead of touching global dirs:
npm install pnpm   # into a scratch dir; invoked by its full ./node_modules/.bin/pnpm path

# Created a dedicated profile from the shipped `web` template:
npx @deepseek-ai/dsh --profile ai-harness --from-default-profile web --dump-config

# Installed both custom plugins into it (see below):
npx @deepseek-ai/dsh plugin --profile ai-harness add link:./plugins/session-digest
npx @deepseek-ai/dsh plugin --profile ai-harness add link:./plugins/repo-doctor
```

`$DSH_HOME` (`~/.dsh`) is a per-user directory outside this repo, so the
profile itself isn't committed — the patch files under `plugins/*/cordis.patch.yml`
are what's portable and reviewable.

## The 2 custom plugins (built from scratch, tested, verified in the real runtime)

| Plugin | Tool it adds | What it does |
|---|---|---|
| [`plugins/session-digest`](plugins/session-digest/) | `session_digest` | Listens on the Cordis `tools/result` event and keeps a running changelog of every tool call in the session; returns it as text, optionally limited to the last N calls. |
| [`plugins/repo-doctor`](plugins/repo-doctor/) | `repo_doctor` | Checks `git status` and scans for `FIXME`/`TODO`/`XXX` markers, rolled into a 0-100 health score. |

Both follow the documented `defineTool` shape from `docs/cookbook/adding-a-tool.md`
and the function-plugin export convention (`name`/`inject`/`apply`, no
default export) from the repo's own `AGENTS.md`. Each package splits pure,
dependency-free logic (`core.js`) from the thin Cordis wiring (`index.js`),
so the logic is unit-tested directly:

```sh
cd plugins/session-digest && node --test   # 4/4 passing
cd plugins/repo-doctor && node --test      # 4/4 passing
```

**Real integration, not just unit tests.** Installing both into a live
`headless` profile and booting it surfaced and fixed a genuine bug: the
plugins first declared `@deepseek-ai/dsh-tools` as a `peerDependency`, which
`pnpm link:` never resolves into the plugin's own `node_modules` (Node's ESM
resolver walks up from the plugin's real path and never finds it). Fixed by
making it a real `dependency` and installing it directly in each plugin
directory. After the fix:

```
$ npx @deepseek-ai/dsh --profile <profile-with-both-plugins> "say hi"
dsh: MISSING_CREDENTIAL: llm-deepseek: no API key for provider route
"deepseek-official"; store DEEPSEEK_API_KEY through the credentials service
...or export DEEPSEEK_API_KEY in the launching environment
```

That's the harness successfully loading the entire plugin tree — including
both custom plugins — and stopping at exactly the expected point (no model
credential yet), confirmed via `--dump-config` showing both `session-digest`
and `repo-doctor` rows in the composed profile.

## The 5 plugins picked from the course's plugin list

Deliberately **not** auto-installed: they're unreviewed third-party code
(some flagged in their own docs as needing "explicit user approval for build
scripts"), so installing all five sight-unseen isn't something to do without
you in the loop. Picked for category breadth rather than overlap, with the
exact install command for when you're ready:

| Plugin | Category | Install |
|---|---|---|
| `ccch1mneyyy/dsh-TUI` | Full-screen TUI frontend | `dsh plugin --profile <name> add github:ccch1mneyyy/dsh-TUI` |
| `AKS1st/dock` | VS Code-style workbench + editor | `dsh plugin --profile <name> add github:AKS1st/dock` |
| `omdsh-dev/DSH-better-sidebar` | Sidebar host (files/terminal/git/subagents) | `dsh plugin --profile <name> add github:omdsh-dev/DSH-better-sidebar` |
| `aa2246740/dsh-creator-mode-plus` | Fail-closed Creator Mode tooling (scaffold/check/activate/remove) | see its own install script — `git clone` into `tools/`, then `pnpm dsh plugin --profile <name> add link:./tools/dsh-creator-mode-plus` |
| `icetomoyo/dsh_workflow` | Saveable/governable multi-agent workflows | `dsh plugin --profile <name> add github:icetomoyo/dsh_workflow` |

## Showcase prompt

Once `DEEPSEEK_API_KEY` is set, this exercises both custom plugins together:

> Run `repo_doctor` on this project. If the score is below 100, explain
> what's dragging it down. Then call `session_digest` to show me everything
> you just did.

Run it with:

```sh
export DEEPSEEK_API_KEY="sk-..."
npx @deepseek-ai/dsh --profile ai-harness web   # opens the browser UI, select "Creator" mode from the dropdown to also see Creator Mode
# or, for a one-shot non-interactive run:
npx @deepseek-ai/dsh --profile ai-harness-headless "Run repo_doctor on this project..."
```

## What's left

- [ ] Get a `DEEPSEEK_API_KEY` and run the showcase prompt end-to-end
- [ ] Install and smoke-test the 5 external plugins above (with your
      approval, since they run third-party install scripts)
- [ ] Record the demo
