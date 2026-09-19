// Pure logic for the session-digest plugin, kept free of @deepseek-ai/dsh-tools
// imports so it can be unit-tested without a running DSH profile.

export function createDigestStore() {
  return { entries: [] }
}

function summarizeArguments(args) {
  if (args == null) return ''
  try {
    const str = JSON.stringify(args)
    return str.length > 160 ? `${str.slice(0, 157)}...` : str
  } catch {
    return '[unserializable arguments]'
  }
}

/**
 * Record one settled tool call. Intended to be called from a `tools/result`
 * listener with the exec/result pair Cordis hands that event.
 */
export function recordToolResult(store, exec, result, { skipTools = new Set() } = {}) {
  if (skipTools.has(exec.name)) return
  store.entries.push({
    time: new Date().toISOString(),
    tool: exec.name,
    ok: !result.isError,
    summary: summarizeArguments(exec.arguments),
  })
}

export function renderDigest(store, { limit } = {}) {
  const entries = typeof limit === 'number' ? store.entries.slice(-limit) : store.entries
  if (entries.length === 0) return 'No tool calls recorded yet this session.'
  const lines = [`Session digest — ${entries.length} tool call(s):`]
  for (const e of entries) {
    lines.push(`- [${e.ok ? 'ok' : 'FAIL'}] ${e.time} ${e.tool} ${e.summary}`)
  }
  return lines.join('\n')
}
