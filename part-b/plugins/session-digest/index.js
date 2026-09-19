// Cordis plugin entry point. Function-plugin shape (name/inject/apply, no
// default export) per DeepSeek Harness's plugin-export convention.
import { defineTool } from '@deepseek-ai/dsh-tools'
import { createDigestStore, recordToolResult, renderDigest } from './core.js'

export const name = 'session-digest'
export const inject = ['tools']

export function apply(ctx) {
  const store = createDigestStore()
  const skipTools = new Set(['session_digest'])

  // `tools/result` is an emit-mode observer event: it fires after every tool
  // call settles (success or failure) and cannot affect the outcome.
  ctx.on('tools/result', (exec, result) => {
    recordToolResult(store, exec, result, { skipTools })
  })

  ctx.tools.register(defineTool({
    name: 'session_digest',
    description: 'Summarize the tool calls made so far this session as a running changelog.',
    parameters: {
      limit: { type: 'number', description: 'Only include the last N tool calls (defaults to all)' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      return renderDigest(store, { limit: args.limit })
    },
  }))
}
