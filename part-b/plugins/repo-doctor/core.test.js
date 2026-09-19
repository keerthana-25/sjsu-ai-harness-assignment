import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { runRepoDoctor, renderReport } from './core.js'

const execFileAsync = promisify(execFile)

async function withTempRepo(fn) {
  const dir = await mkdtemp(path.join(tmpdir(), 'repo-doctor-test-'))
  try {
    await execFileAsync('git', ['init', '-q'], { cwd: dir })
    await execFileAsync('git', ['config', 'user.email', 'test@example.com'], { cwd: dir })
    await execFileAsync('git', ['config', 'user.name', 'Test'], { cwd: dir })
    await fn(dir)
  } finally {
    await rm(dir, { recursive: true, force: true })
  }
}

test('reports a clean committed repo with no TODOs', async () => {
  await withTempRepo(async (dir) => {
    await writeFile(path.join(dir, 'a.js'), 'console.log(1)\n')
    await execFileAsync('git', ['add', '.'], { cwd: dir })
    await execFileAsync('git', ['commit', '-q', '-m', 'init'], { cwd: dir })
    const report = await runRepoDoctor({ cwd: dir })
    assert.equal(report.git.isGitRepo, true)
    assert.equal(report.git.changedFiles, 0)
    assert.equal(report.todos.counts.FIXME, 0)
    assert.equal(report.score, 100)
  })
})

test('counts uncommitted changes and TODO markers, lowering the score', async () => {
  await withTempRepo(async (dir) => {
    await writeFile(path.join(dir, 'a.js'), '// FIXME: broken\n// TODO: cleanup\n')
    const report = await runRepoDoctor({ cwd: dir })
    assert.equal(report.git.changedFiles, 1)
    assert.equal(report.todos.counts.FIXME, 1)
    assert.equal(report.todos.counts.TODO, 1)
    assert.ok(report.score < 100)
  })
})

test('non-git directory is reported without crashing', async () => {
  const dir = await mkdtemp(path.join(tmpdir(), 'repo-doctor-nogit-'))
  try {
    await writeFile(path.join(dir, 'a.md'), 'no todos here\n')
    const report = await runRepoDoctor({ cwd: dir })
    assert.equal(report.git.isGitRepo, false)
    assert.equal(report.score, 100)
  } finally {
    await rm(dir, { recursive: true, force: true })
  }
})

test('renderReport produces human-readable text', async () => {
  await withTempRepo(async (dir) => {
    await writeFile(path.join(dir, 'a.js'), '// XXX: someday\n')
    const report = await runRepoDoctor({ cwd: dir })
    const text = renderReport(report)
    assert.match(text, /Health score/)
    assert.match(text, /XXX: 1/)
  })
})
