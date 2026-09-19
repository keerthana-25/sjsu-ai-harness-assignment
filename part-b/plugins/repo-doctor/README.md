# dsh-plugin-repo-doctor

Adds a `repo_doctor` tool that checks repository health: uncommitted `git`
changes and `FIXME`/`TODO`/`XXX` markers (the same three tags DeepSeek
Harness's own contributor guide uses), rolled into a 0-100 score.

## How it works

- `core.js` (`gitStatus`, `scanTodos`, `scoreReport`, `runRepoDoctor`,
  `renderReport`) does the real work with plain `node:child_process` /
  `node:fs` calls — no dependency on `@deepseek-ai/dsh-tools`, so it's unit
  tested (`core.test.js`) directly against real temp git repos, no DSH profile
  needed.
- `index.js` wraps that logic in a `defineTool` registration exposing
  `repo_doctor({ path? })`, forwarding the tool call's `AbortSignal` so a
  cancelled call stops the directory walk / git subprocess.

## Test

```sh
node --test
```
