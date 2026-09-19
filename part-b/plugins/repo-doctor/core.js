// Pure logic for the repo-doctor plugin, kept free of @deepseek-ai/dsh-tools
// imports so it can be unit-tested without a running DSH profile.
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'

const execFileAsync = promisify(execFile)

const TODO_TAGS = ['FIXME', 'TODO', 'XXX']
const IGNORE_DIRS = new Set(['.git', 'node_modules', 'dist', 'build', '.dsh'])
const SCANNABLE_EXT = /\.(js|mjs|cjs|ts|tsx|jsx|py|md|json|yml|yaml)$/

export async function gitStatus(cwd, signal) {
  try {
    const { stdout } = await execFileAsync('git', ['status', '--porcelain'], { cwd, signal })
    const lines = stdout.split('\n').filter(Boolean)
    return { isGitRepo: true, changedFiles: lines.length, entries: lines.slice(0, 20) }
  } catch {
    return { isGitRepo: false, changedFiles: 0, entries: [] }
  }
}

export async function scanTodos(cwd, signal, maxFiles = 500) {
  const counts = Object.fromEntries(TODO_TAGS.map((tag) => [tag, 0]))
  const samples = []
  let filesScanned = 0

  async function walk(dir) {
    if (filesScanned >= maxFiles || signal?.aborted) return
    let entries
    try {
      entries = await readdir(dir, { withFileTypes: true })
    } catch {
      return
    }
    for (const entry of entries) {
      if (signal?.aborted || filesScanned >= maxFiles) return
      if (IGNORE_DIRS.has(entry.name)) continue
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) {
        await walk(full)
      } else if (entry.isFile() && SCANNABLE_EXT.test(entry.name)) {
        filesScanned++
        let text
        try {
          text = await readFile(full, 'utf8')
        } catch {
          continue
        }
        for (const tag of TODO_TAGS) {
          const matches = text.match(new RegExp(`\\b${tag}\\b`, 'g'))
          if (matches) {
            counts[tag] += matches.length
            if (samples.length < 10) samples.push(`${full}: ${tag}`)
          }
        }
      }
    }
  }

  await walk(cwd)
  return { counts, samples, filesScanned }
}

export function scoreReport({ git, todos }) {
  let score = 100
  score -= Math.min(git.changedFiles * 2, 30)
  score -= Math.min(todos.counts.FIXME * 5, 30)
  score -= Math.min(todos.counts.TODO * 1, 20)
  return Math.max(0, Math.round(score))
}

export async function runRepoDoctor({ cwd = '.', signal } = {}) {
  const resolvedCwd = path.resolve(cwd)
  const [git, todos] = await Promise.all([
    gitStatus(resolvedCwd, signal),
    scanTodos(resolvedCwd, signal),
  ])
  return { cwd: resolvedCwd, git, todos, score: scoreReport({ git, todos }), checkedAt: new Date().toISOString() }
}

export function renderReport(report) {
  const lines = [
    `Repo Doctor report for ${report.cwd}`,
    `Health score: ${report.score}/100`,
    report.git.isGitRepo
      ? `Git: ${report.git.changedFiles} changed file(s)`
      : 'Git: not a git repository',
    `TODO markers — FIXME: ${report.todos.counts.FIXME}, TODO: ${report.todos.counts.TODO}, XXX: ${report.todos.counts.XXX} (scanned ${report.todos.filesScanned} files)`,
  ]
  if (report.todos.samples.length) {
    lines.push('Samples:')
    for (const s of report.todos.samples) lines.push(`  - ${s}`)
  }
  return lines.join('\n')
}
