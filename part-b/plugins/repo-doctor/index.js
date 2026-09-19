// Cordis plugin entry point. Function-plugin shape (name/inject/apply, no
// default export) per DeepSeek Harness's plugin-export convention.
import { defineTool } from '@deepseek-ai/dsh-tools'
import { runRepoDoctor, renderReport } from './core.js'

export const name = 'repo-doctor'
export const inject = ['tools']

export function apply(ctx) {
  ctx.tools.register(defineTool({
    name: 'repo_doctor',
    description: 'Check repository health: uncommitted changes and TODO/FIXME/XXX markers, with a 0-100 score.',
    parameters: {
      path: { type: 'string', description: 'Directory to check (defaults to the current working directory)' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args, exec) {
      const report = await runRepoDoctor({ cwd: args.path ?? '.', signal: exec.signal })
      return renderReport(report)
    },
  }))
}
