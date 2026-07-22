# Workspace cleanup

Use this reference only after implementation and publication are settled and
before posting final evidence, closing the issue, and releasing the
implementation lease. Cleanup is housekeeping under the same session, not part
of the lease mutation. Keep the issue open until cleanup succeeds or every
preserved artifact has a safe disposition that the repository completion
contract accepts.

## Contents

- [Default disposition](#default-disposition)
- [Remove a linked worktree](#remove-a-linked-worktree)
- [Delete a local ticket branch](#delete-a-local-ticket-branch)
- [Delete an authorized remote branch](#delete-an-authorized-remote-branch)
- [Evidence and release](#evidence-and-release)

## Default disposition

Repository instructions and explicit user direction override this table. The
bundled default applies only to artifacts recorded as absent before claim and
created by the current session.

| Artifact | `completed` default | `blocked` or `handoff` default |
| --- | --- | --- |
| Session-created linked worktree | Remove when every safety check passes | Retain for continuation |
| Session-created local ticket branch | Delete after worktree removal when every branch check passes | Retain for continuation |
| Session-created remote ticket branch | Retain | Retain |
| Pre-existing, primary, current, or shared workspace | Retain | Retain |

Never broaden the default from a familiar branch name or directory pattern.
Remote branch deletion and cleanup of a pre-existing local artifact require
explicit repository or user authority. A repository rule to auto-delete a merged
pull-request branch counts only for that named remote publication flow.

## Remove a linked worktree

Operate from a different retained control worktree while the issue lease remains
owned. Immediately before removal, verify all of the following:

- the target canonical path is the exact linked worktree recorded as created by
  this session, not the control worktree, primary checkout, or another actor's
  path;
- `git worktree list --porcelain` still maps that path to the expected branch and
  final commit;
- no user task or other active session shares the target;
- tracked, staged, unstaged, and untracked state is empty; inspect ignored files
  too, and remove them only when the repository identifies them as disposable
  generated output;
- submodules and nested repositories contain no state that removal would lose;
- the final commit remains reachable through the local branch that will be
  retained, a live remote ref read back from the canonical remote, or the
  verified integration ref. Do not treat a stale remote-tracking ref as durable
  recovery evidence. After squash or rebase merge, the integration commit does
  not by itself make the original ticket-head commit recoverable; retain and
  verify a live remote ticket ref or another durable ref for that exact OID.

Recheck lease ownership, then run ordinary `git worktree remove` against the
explicit canonical path from the control worktree. Never use `--force`, broad
globs, recursive file deletion, or `git worktree prune` as a substitute. Read
back `git worktree list --porcelain`; success means the exact target entry is
absent and the control worktree is unchanged.

If any observation is unknown or changes between inspection and removal, stop
cleanup and preserve the target. Record the path, expected branch and commit,
the failed check, and the command or decision needed to make removal safe.

## Delete a local ticket branch

Consider the local branch only after its linked worktree is confirmed absent.
Delete it under the bundled default only when all of these are true:

- the branch was recorded as created by this session and no worktree checks it
  out;
- its tip is the expected final commit and that exact commit is reachable from a
  retained remote ref or verified integration ref;
- no unresolved publication result or continuation depends on it;
- ordinary `git branch -d -- <branch>` accepts the deletion.

Never use `git branch -D`. Read back the exact `refs/heads/<branch>`; success
means it is absent while the retained recovery ref still resolves as expected.
If safe deletion refuses, retain the branch and report why.

## Delete an authorized remote branch

Delete a remote ticket branch only when a repository rule or explicit user
instruction authorizes that exact remote and branch. First verify its exact tip,
the pull request's terminal state, the integration result, and that the commit
remains durably recoverable after deletion. Recheck the lease, then delete with
an atomic expected-old-OID guard equivalent to:

```bash
git push \
  --force-with-lease=refs/heads/<branch>:<expected-old-oid> \
  <remote> :refs/heads/<branch>
```

If the compare-and-swap loses, preserve the new tip and reassess authorization;
never replace the expected OID with the newly observed value automatically.
Read back the exact live remote ref after the push. Deletion succeeds only when
that readback reports the ref absent. If it exists regardless of the push result,
treat it as advanced or recreated: preserve the observed tip, report the race,
and require new explicit authority before another deletion attempt. An unknown
result must be reconciled before retrying.

## Evidence and release

Put the cleanup result in the session evidence: removed worktree paths, deleted
refs, retained recovery refs, and every preserved artifact with its reason and
next safe action. Read back that evidence, apply the tracker outcome, ensure the
issue is closed for a completed outcome without reopening a provider-closed
issue, and release the lease. Do not begin a new automatic cleanup attempt after
release because a successor session may already own or be inspecting the work.
