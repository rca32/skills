# Consumer repository contract

Read this reference only when a consuming repository lacks an execution and
publication contract, or the user asks to install the standard
`work-github-issue` policy in an `AGENTS.md` file.

The bundled contract grants standing authority for agent-owned pull requests,
local verification, independent review, autonomous merge, evidence-backed issue
closure, and safe session-worktree cleanup. It also prohibits GitHub Actions.
Read the exact [managed contract template](consumer-agents-contract.md) before
previewing or installing it.
Installing or updating it is a durable repository-policy mutation: do so only
when the user explicitly authorizes that mutation. An issue-backed or shared
policy change additionally requires the applicable planning or implementation
lease.

For a policy mutation outside an active implementation lease, use the planning
lease flow in the main skill: key it to the source issue, or to repository-wide
key `0` when no source issue exists. Check that lease immediately before
`install`, read back the file with this script's `check`, reconcile any unknown
write before retrying, and release only after the managed block and all
authorized policy writes are confirmed.

Before writing, read the existing target and the full applicable instruction
chain, preview the exact managed block, and compare its merge, Actions, review,
closure, and cleanup authority with every existing rule. Stop and resolve any
conflict before `install`; do not write a contradictory block and diagnose it
afterward. Preview with:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  render --integration-target main --merge-method squash
```

Install it into an explicitly selected consuming repository:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  check /absolute/path/to/repository/AGENTS.md \
  --integration-target main --merge-method squash

# Pass the exact opaque `snapshot` value returned above.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  install /absolute/path/to/repository/AGENTS.md \
  --expected-snapshot SNAPSHOT_FROM_CHECK \
  --integration-target main --merge-method squash
```

`check` is the read-only exact-state and snapshot-identity test. Inspect its
exact rendered `contract` and target content, then pass the returned opaque
`snapshot` to `install`. The token binds the rendered contract, repository-root
identity, target-file identity or absence, and content hash; a changed template,
repository, or file fails before writing. On first
installation the script creates a missing root file exclusively or appends one
versioned block without replacing existing bytes. A repository-local atomic
installer lock serializes cooperating runs, and append-only installation
preserves unrelated edits made by other tools, then reports a reconciliation
error instead of claiming success when concurrent content appears. Repository
and target files are opened through pinned directory identity plus stable
descriptors with no-follow and inode checks so repository or symlink replacement
cannot redirect the write. Platforms without those secure primitives fail closed
and may use `render` for a manual installation.
The script refuses to replace a different managed block automatically; resolve
that policy explicitly first. It also fails closed on duplicate or unmatched
markers, unsafe Git branch names, any symlinked path component, a
missing/non-repository parent, or a target other than the selected Git root
`AGENTS.md`. After installation, reread the complete applicable instruction
chain. A conflicting higher-authority or more-specific instruction remains
unresolved; the managed block never silently overrides it.

Installation is complete only when `check` returns `status=current`, the full
instruction chain has no conflict, GitHub Actions and required hosted checks are
disabled in repository settings, target-branch rules require no external human
approval or other restriction the lease owner cannot satisfy, a provider-side
rule or operation can atomically reject both a stale PR head and an out-of-date
integration base without GitHub Actions, and the named integration target and
merge method match the repository's actual publication design. Treat those
GitHub settings as a read-only preflight unless the user
separately authorizes changing them; installing the local managed block alone
does not authorize remote repository-setting mutations.
