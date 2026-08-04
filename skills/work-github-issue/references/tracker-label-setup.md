# Bundled tracker-label setup

Read this reference only when the user asks to inspect or initialize the bundled
GitHub tracker labels in a consuming repository. Label setup is optional: the
fallback tracker contract uses issue-body markers when matching labels are
absent, so missing labels never block issue work.

The setup owns only the seven Korean state and category labels defined by the
bundled [tracker contract](tracker-contract.md). It does not edit `AGENTS.md`,
install publication policy, change repository settings, or grant code
publication authority.

Choose the branch from the granted authority:

- **Read-only inspection:** check the complete label catalog and report
  `current`, `missing`, or `conflict`; acquire no lease.
- **Authorized initialization:** require explicit repository-wide label creation
  authority, acquire a planning lease on the source or parent issue (or key `0`
  only when no source issue exists), create only missing labels, read back the
  catalog, and release after the result is known.

Before either branch, resolve the repository root, canonical GitHub remote,
authenticated account, and selected tracker contract. Stop before mutation when
repository identity is ambiguous, the repository selects another tracker
contract, or an existing bundled label name has a conflicting description.

Inspect the catalog before acquiring a lease:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  check /absolute/path/to/repository --remote origin
```

Keep the returned opaque `snapshot`. For authorized initialization, claim the
planning key selected above and pass its key, session, and snapshot to the
installer:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim LEASE_KEY --purpose planning --ttl-minutes 10 --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  install /absolute/path/to/repository --remote origin \
  --lease-key LEASE_KEY \
  --lease-session SESSION_FROM_CLAIM \
  --expected-snapshot SNAPSHOT_FROM_CHECK
```

The installer fails before writes if the snapshot changed or a description
conflicts. It checks the planning lease immediately before each create, creates
only absent labels, and reads the catalog after each attempt. Existing label
colors may differ; names and descriptions carry the contract. Never rename,
edit, or delete existing labels during setup.

Run both checks again after installation. A successful initialization must read
back as `current`. If installation fails before any create and a complete catalog
read classifies the result as `missing` or `conflict`, that known non-complete
result is also safe to release and report. Never release while any create result
is unknown.

If a later lease check fails after earlier labels were created and read back,
the installer returns `status=error` with the confirmed `created` list. Re-read
the complete catalog, report that known partial outcome, and release only when
the catalog and lease state are both exact.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  check LEASE_KEY --session SESSION_FROM_CLAIM --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  check /absolute/path/to/repository --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  release LEASE_KEY --session SESSION_FROM_CLAIM --remote origin
```

If the installer reports `status=unknown`, preserve confirmed labels. The caller,
not the installer, then reconciles with at most three complete catalog reads over
no more than 60 seconds. Retry one absent label create once only when the final
two reads agree it is absent. If the retry remains unknown, stop writes and lease
renewal so a successor can reconcile after expiry. Never delete successfully
created labels as rollback.

Completion is observable: inspection reports the exact catalog state without a
write; authorized initialization reports `current`; or a known pre-write failure
reports its exact non-complete state. Every create has an exact readback, and the
selected planning key is unclaimed after release.
