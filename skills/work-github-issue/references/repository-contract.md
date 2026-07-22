# Consumer repository initialization

Read this reference only when a consuming repository lacks an execution,
publication, or tracker-label setup, or the user asks to inspect or initialize
the standard `work-github-issue` repository contract.

The initialization has two independently verified parts:

- a managed `AGENTS.md` contract that grants standing authority for agent-owned
  pull requests, local verification, independent review, autonomous merge,
  evidence-backed issue closure, and safe session-worktree cleanup while
  prohibiting GitHub Actions;
- the seven Korean state and category labels defined by the bundled
  [tracker contract](tracker-contract.md).

Read the exact [managed contract template](consumer-agents-contract.md) before
previewing or installing it. `check` operations are read-only. Installing the
contract or creating labels are distinct durable mutations; initialize only
when the user explicitly authorizes the corresponding repository-policy or
remote-label mutation. Permission for one does not imply the other, and full
initialization requires both.

Choose the branch from the granted authority:

- **Read-only inspection:** run both checks when access permits and report each
  component independently; acquire no lease.
- **Policy-only setup:** preview, snapshot, lease, install, and read back only the
  managed `AGENTS.md` contract. Missing label authority or catalog access does
  not block this previously supported branch; report tracker initialization as
  incomplete.
- **Label-only setup:** snapshot, lease, create, and read back only the bundled
  labels. Do not edit `AGENTS.md`; report policy initialization as incomplete.
- **Full initialization:** require both mutation authorities, preflight both
  components before any write, and follow the labels-first sequence below.

For initialization outside an active implementation lease, use the planning
lease flow in the main skill: key it to the source issue, or to repository-wide
key `0` when no source issue exists. A repository bootstrap normally uses key
`0`. Check that lease before every mutation batch and release only after every
authorized component is current and no result is unknown. Full initialization
therefore requires both components to be current; a component-only branch does
not wait for unauthorized setup.

Before writing, read the existing target and the full applicable instruction
chain, preview the exact managed block, and compare its merge, Actions, review,
closure, and cleanup authority with every existing rule. Also resolve the
canonical GitHub remote and inspect the complete label catalog. Stop before all
mutations when the managed policy conflicts, a required label name has a
different description, authentication or repository identity is ambiguous, or
the repository selects a tracker contract other than the bundled fallback.
This combined stop gate applies to full initialization; in a component-only
branch, evaluate only the selected component and its prerequisites.
Preview the policy with:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  render --integration-target main --merge-method squash
```

Check both initialization parts before acquiring a lease:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  check /absolute/path/to/repository/AGENTS.md \
  --integration-target main --merge-method squash

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  check /absolute/path/to/repository --remote origin
```

Keep the exact opaque `snapshot` from each check. After explicit authorization,
acquire the repository-wide planning lease and initialize labels first so a
failed remote setup does not install a local policy that depends on unavailable
tracker state:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim 0 --purpose planning --ttl-minutes 10 --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  install /absolute/path/to/repository --remote origin \
  --lease-session SESSION_FROM_CLAIM \
  --expected-snapshot LABEL_SNAPSHOT_FROM_CHECK

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  check 0 --session SESSION_FROM_CLAIM --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  install /absolute/path/to/repository/AGENTS.md \
  --expected-snapshot POLICY_SNAPSHOT_FROM_CHECK \
  --integration-target main --merge-method squash
```

Run both `check` commands again and release only when each returns `current`.
The label installer creates only missing bundled labels, checks the planning
lease immediately before each create, and reads the complete catalog after each
attempt. It treats colors as presentation suggestions but requires an existing
label's name and description to express the bundled meaning exactly. It never
renames, edits, or deletes an existing label. A changed label snapshot or
meaning conflict fails before remote writes.

The policy `check` is the read-only exact-state and snapshot-identity test.
Inspect its rendered `contract` and target content, then pass its opaque
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
The policy installer refuses to replace a different managed block automatically; resolve
that policy explicitly first. It also fails closed on duplicate or unmatched
markers, unsafe Git branch names, any symlinked path component, a
missing/non-repository parent, or a target other than the selected Git root
`AGENTS.md`. After installation, reread the complete applicable instruction
chain. A conflicting higher-authority or more-specific instruction remains
unresolved; the managed block never silently overrides it.

If a label-create result is unknown, keep the lease, preserve the reported list
of confirmed labels, and reconcile the catalog before retrying. If labels become
current but policy installation fails, leave them in place and rerun the
snapshot-gated policy step; labels are harmless prerequisites, not rollback
targets. Never delete successful initialization state automatically.

Initialization is complete only when both checks return `status=current`, the
full instruction chain has no conflict, GitHub Actions and required hosted
checks are disabled in repository settings, target-branch rules require no
external human approval or other restriction the lease owner cannot satisfy, a
provider-side rule or operation can atomically reject both a stale PR head and
an out-of-date integration base without GitHub Actions, and the named
integration target and merge method match the repository's actual publication
design. Treat GitHub settings other than the bundled labels as a read-only
preflight unless the user separately authorizes changing them.
