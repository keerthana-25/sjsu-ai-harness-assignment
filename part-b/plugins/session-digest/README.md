# dsh-plugin-session-digest

Adds a `session_digest` tool that summarizes the tool calls made so far in the
current session as a running changelog.

## How it works

- `index.js` listens on the Cordis `tools/result` event (`emit` mode, fires
  after every tool call settles) and appends `{ time, tool, ok, summary }` to
  an in-memory list, skipping calls to `session_digest` itself.
- The `session_digest` tool renders that list as markdown-ish text, optionally
  limited to the last N calls via the `limit` parameter.
- `core.js` holds the pure logic (`createDigestStore`, `recordToolResult`,
  `renderDigest`) with no dependency on `@deepseek-ai/dsh-tools`, so it can be
  unit tested (`core.test.js`) without booting a DSH profile.

## Test

```sh
node --test
```
