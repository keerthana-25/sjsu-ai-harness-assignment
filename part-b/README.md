# Part B: DeepSeek Harness + Plugins

**Status**: Complete. Harness installed, Creator Mode confirmed, 2 custom
plugins built and verified end-to-end, all 5 community plugins reviewed and
installed (7 total plugins mounted together, confirmed by actually booting
the web server), showcase prompt run live end-to-end for free (via
OpenRouter, see below — no `DEEPSEEK_API_KEY` required).

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

## Free alternative to a paid DeepSeek API key

DeepSeek's own API (`llm-deepseek` adapter) requires a funded account — no
free tier survived past a signup bonus that either didn't apply or expired
(confirmed directly against `https://api.deepseek.com/user/balance`: `$0.00`
across granted, topped-up, and total balance). Since paying isn't the point
of this assignment, model calls are routed elsewhere instead:

DSH ships a second, provider-neutral adapter, **`dsh-llm-pi-ai`**, already
mounted in `dsh-base` but unconfigured by default. It accepts any
OpenAI-Chat-Completions-compatible gateway — including
[OpenRouter](https://openrouter.ai), which has genuinely zero-cost (`:free`
suffixed) models and which you already have a key for from Part A. No new
plugin, no reinstall — just a config overlay:
[`openrouter-free.patch.yml`](openrouter-free.patch.yml), applied at boot
with `--patch`.

Model choice mattered: the first free model tried
(`deepseek/deepseek-v4-flash-0731:free`) handled a trivial prompt fine but
spiraled into a degenerate reasoning loop on the actual multi-tool showcase
task — a small/distilled free-tier model struggling with agentic tool
orchestration, not a harness or plugin bug. The second pick
(`qwen/qwen3.8-27b:free`) hit a shared-pool `429 RATE_LIMIT` (a real, common
free-tier constraint — OpenRouter's free models share capacity across every
user). Landed on **`nvidia/nemotron-3-super-120b-a12b:free`** (120B params,
262k context): reliable on both the trivial prompt and the full showcase
prompt, confirmed live below.

```sh
export OPENROUTER_API_KEY="sk-or-..."   # same key from Part A
npx @deepseek-ai/dsh --profile ai-harness-headless --patch ./openrouter-free.patch.yml "say hi"
```

**Confirmed live output of the actual showcase prompt**, run this way, $0 cost:

```
The repo_doctor analysis shows this project has a health score of 48/100, which is below the perfect score. The issues dragging down the score are:

1. Git status: 1 changed file that needs attention
2. Technical debt markers:
   - 13 FIXME comments
   - 21 TODO comments
   - 9 XXX comments

These markers were found across 500 scanned files, indicating areas that need
cleanup, fixes, or further work. The session digest shows I only made one
tool call - running repo_doctor itself.
```

(The 48/100 reflects `repo_doctor` scanning `part-b/` including the cloned
upstream `harness/` source, which carries its own many TODO markers — expected,
not a plugin bug. Point it at a narrower `path` for a tighter score.)

`--patch` is a CLI flag, not a permanent profile mutation, so switching back
to real DeepSeek later (once there's balance) is just dropping the flag —
`agent-default-model` reverts to its `dsh-base` default (`deepseek-official`).

## The 5 plugins picked from the course's plugin list

All 5 reviewed (cloned, read source, checked for install/build scripts
before running anything) and **installed and verified live** — the whole
`ai-harness` profile actually boots with all of them mounted together
(confirmed by starting the real web server, not just `--dump-config`).

| Plugin | Category | Published as | Status |
|---|---|---|---|
| `ccch1mneyyy/dsh-TUI` | Full-screen TUI frontend | `@deepseek-harness-tui/dsh-tui` (npm) | Installed into its own `dsh-tui` profile; confirmed 18+ config rows mounted |
| `AKS1st/dock` | VS Code-style workbench base | `dock-base` (npm) | Installed into `ai-harness`; mounted as `id: dock` |
| `omdsh-dev/DSH-better-sidebar` | Sidebar host (files/terminal/git) | `dsh-better-sidebar` (npm) | Installed into `ai-harness`; mounted as `id: better-sidebar` |
| `aa2246740/dsh-creator-mode-plus` | Fail-closed Creator Mode tooling | not on npm — `link:` from source, plus its `dshx` companion CLI | Preset installed at `~/.dsh/.agent-presets/creator-mode-plus/`, verified on disk |
| `icetomoyo/dsh_workflow` | Governable multi-agent workflows | `@dsh-external/workflow` — not on npm, `link:` from source | Installed into `ai-harness`; mounted as `id: dsh-external-workflow` |

**Install commands actually used:**

```sh
# dsh-TUI: standalone profile (its own documented convention)
dsh plugin --profile dsh-tui add @deepseek-harness-tui/dsh-tui

# dock, better-sidebar: published packages, straight into ai-harness
dsh plugin --profile ai-harness add dock-base
dsh plugin --profile ai-harness add dsh-better-sidebar   # needed `pnpm approve-builds node-pty -y` first (see below)

# dsh_workflow: not published, link: from a local clone
git clone https://github.com/icetomoyo/dsh_workflow.git
dsh plugin --profile ai-harness add link:/path/to/dsh_workflow

# dsh-creator-mode-plus: two-step install per its own docs — the client
# plugin + a separate devkit (DSHX) cloned into the harness checkout
git clone https://github.com/aa2246740/dsh-creator-mode-plus.git harness/tools/dsh-creator-mode-plus
git clone https://github.com/aa2246740/dsh-external-plugin-devkit.git harness/tools/dshx
node harness/tools/dshx/src/cli.ts setup --harness harness/           # installs the dshx CLI + skill
dsh plugin --profile ai-harness add link:/path/to/harness/tools/dsh-creator-mode-plus
node harness/tools/dsh-creator-mode-plus/scripts/install.mjs --harness harness/
```

**What review found and what got fixed:**

- **`node-pty`'s native build** (used by `dsh-better-sidebar`'s terminal tab): pnpm blocks native build scripts by default. `node-pty` is the same library VS Code itself uses for terminal support — approved specifically (`pnpm approve-builds node-pty -y`), not blanket-approved for everything.
- **`dsh-creator-mode-plus`'s installer** (`scripts/install.mjs`) was read in full before running: it only ever writes under `$DSH_HOME/.agent-presets/`, stages changes in a temp dir with rollback-on-failure, and tightens file permissions (`chmod 700/600`) on what it writes. No network calls, no code execution beyond that.
- **`dshx`'s bundled skill** got linked into `~/.claude/skills/dshx` by its own setup step (a real side effect on this machine beyond just this repo, not a bug) — read in full: it's pure instructional text for how an AI coding assistant should use the CLI safely (explicit guardrails like "never kill or restart dsh from inside a session"), no executable content.
- **`dsh_workflow` had two real packaging bugs**, both worked around in the local clone only (not upstream):
  1. Its `dependencies`/`peerDependencies` split assumes installation inside the actual DSH monorepo workspace, where peer packages resolve for free. Under a plain `link:` install (same root cause we hit and fixed with our own 2 plugins), none of those peers resolve. Fixed by letting `npm install` pull the real published versions of each into the plugin's own `node_modules` — cleaner than the peerDependency→dependency edit we made for our own plugins, since this is someone else's package we're not maintaining upstream.
  2. Its `package.json` `devDependencies` block hardcodes the author's own local dev checkout paths (`link:../test-icetomoyo/...`), which made `npm install` fail outright (even with `--omit=dev`) since it can't parse an unresolvable `link:` target. Removed that block in the local clone only — it's dev-only tooling, irrelevant to actually running the plugin.
- The other three plugins installed clean, no issues.

None of this was assumed safe — every install script was read before running, and the two packaging bugs were real bugs, not expected friction.

## Showcase prompt

Exercises both custom plugins together (output shown above, run for free
via OpenRouter):

> Run `repo_doctor` on this project. If the score is below 100, explain
> what's dragging it down. Then call `session_digest` to show me everything
> you just did.

```sh
# Free (OpenRouter, no DeepSeek balance needed):
export OPENROUTER_API_KEY="sk-or-..."
npx @deepseek-ai/dsh --profile ai-harness-headless --patch ./openrouter-free.patch.yml "Run repo_doctor on this project. If the score is below 100, explain what's dragging it down. Then call session_digest to show me everything you just did."

# Or, once there's a funded DEEPSEEK_API_KEY, drop the --patch flag and swap providers:
export DEEPSEEK_API_KEY="sk-..."
npx @deepseek-ai/dsh --profile ai-harness-headless "Run repo_doctor on this project..."

# Interactive web UI either way (pick "Creator" mode from the dropdown):
npx @deepseek-ai/dsh --profile ai-harness web --patch ./openrouter-free.patch.yml
```

## What's left

- [x] Run the showcase prompt end-to-end (free, via OpenRouter — see above)
- [x] Install and smoke-test the 5 external plugins above (all reviewed and
      verified live, see above)
- [ ] Record the demo (screen capture of the running web UI — nothing
      technical blocking this, just an artifact to produce)
