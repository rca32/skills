# Default GitHub issue contract

Use this contract when the consuming repository does not define its own tracker
document. Repository instructions override it.

## Readiness and frontier

- Treat `ready-for-agent` as specified work, not an active claim.
- Use GitHub native blocking dependencies; use a `Blocked by:` body line only
  when native dependencies are unavailable.
- Define the frontier as open `ready-for-agent` issues with no open blocker, no
  other-account assignee, and no active issue/session lease pair.
- Permit a missing readiness label only after an explicit user override.
- Treat a same-account assignee without a lease as ambiguous legacy work. Read
  comments, branches, commits, and PRs; require an explicit handoff before
  `--allow-shared-assignee`.

## Tracker states

Use exactly one state label where the repository provides this vocabulary:
`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix`.
Keep category labels separate from state.

## Publication and completion

This fallback does not choose a base branch, pull-request target, integration
target, merge method, or merge authority for the consuming repository. Before an
implementation claim, resolve the fields required by the requested outcome from
explicit user and repository instructions as described in the main skill. A
remote default branch is discovery evidence, not publication authority.

If a required publication field or completion point is missing or conflicting,
do not claim for an outcome that requires it. A local-only implementation may
proceed only when that scope is explicit; it ends in `handoff` unless the
repository separately defines local work as complete. If the ambiguity is found
after claim, stop consequential writes, preserve the workspace, publish the
blocker or handoff evidence, and release with the matching non-complete outcome.

## Session outcomes

A real claim authorizes assignment, lease projection, renewal, evidence, and
release writes on that issue. If tracker writes are prohibited, remain
read-only and do not claim. Code publication requires separate authorization.

- **Complete:** reach the resolved repository completion point, post reproducible
  evidence, close only when every acceptance criterion holds, update the parent
  pointer, then release as `completed`. A pushed branch or open pull request is
  complete only when the repository contract explicitly says so.
- **Blocked:** post the blocker and next action, add a native dependency or an
  exclusive `needs-info|ready-for-human` state, keep the issue open, then
  release as `blocked`. Use `ready-for-human` when required approval, access, or
  merge authority belongs to a person.
- **Handoff:** keep the issue open and post branch, HEAD, fixed point, tests,
  local state, publication state, and next action before releasing as `handoff`.
  Use this when another agent or separately authorized workflow can continue.

Every release uses an evidence comment on the leased issue with this shell.
Fill every section; add `## Next action` for `blocked` or `handoff`.

```markdown
<!-- rca-issue-evidence:v1 session=<session> outcome=<completed|blocked|handoff> -->
## Outcome
## Changes
## Verification
## Limitations
## Safety
## Next action
```

Omit `## Next action` only for `completed`.
