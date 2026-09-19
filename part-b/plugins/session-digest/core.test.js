import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createDigestStore, recordToolResult, renderDigest } from './core.js'

test('empty store renders a no-calls message', () => {
  const store = createDigestStore()
  assert.match(renderDigest(store), /No tool calls recorded/)
})

test('records successful and failed calls in order', () => {
  const store = createDigestStore()
  recordToolResult(store, { name: 'read_file', arguments: { path: 'a.txt' } }, { isError: false })
  recordToolResult(store, { name: 'bash_tool', arguments: { command: 'false' } }, { isError: true })
  const digest = renderDigest(store)
  assert.match(digest, /2 tool call/)
  assert.match(digest, /\[ok\] .* read_file/)
  assert.match(digest, /\[FAIL\] .* bash_tool/)
})

test('skips tools listed in skipTools', () => {
  const store = createDigestStore()
  recordToolResult(
    store,
    { name: 'session_digest', arguments: {} },
    { isError: false },
    { skipTools: new Set(['session_digest']) },
  )
  assert.equal(store.entries.length, 0)
})

test('limit truncates to the most recent N entries', () => {
  const store = createDigestStore()
  for (let i = 0; i < 5; i++) {
    recordToolResult(store, { name: `tool_${i}`, arguments: {} }, { isError: false })
  }
  const digest = renderDigest(store, { limit: 2 })
  assert.match(digest, /tool_3/)
  assert.match(digest, /tool_4/)
  assert.doesNotMatch(digest, /tool_0/)
})
