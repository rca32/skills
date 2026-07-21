# Default GitHub issue contract

Use this contract when the consuming repository does not define its own tracker
document. Repository instructions override it.

## Readiness and frontier

- Treat the `ready-for-agent` role (`상태: 에이전트 작업 가능`) as specified
  work, not an active claim.
- Use GitHub native blocking dependencies; use a `먼저 끝나야 하는 작업:` body
  line only when native dependencies are unavailable. Read the legacy `Blocked
  by:` heading on existing issues. If both headings exist and name different
  blockers, stop on a dependency conflict; publish only the Korean heading.
- Define the frontier as open `ready-for-agent` role issues with no open
  blocker, no other-account assignee, and no active issue/session lease pair.
- Permit a missing readiness label only after an explicit user override.
- Treat a same-account assignee without a lease as ambiguous legacy work. Read
  comments, branches, commits, and PRs; require an explicit handoff before
  `--allow-shared-assignee`.

## Tracker states

Treat the role key as automation vocabulary and the label as human-facing text.
Under this fallback, publish exactly one Korean state label:

| Role key | Publish label | Legacy read alias | Description | Suggested color |
| --- | --- | --- | --- | --- |
| `needs-triage` | `상태: 분류 필요` | `needs-triage` | 사실 확인이나 범위 결정이 더 필요함 | `D4C5F9` |
| `needs-info` | `상태: 정보 필요` | `needs-info` | 사람이 답할 수 있는 구체적인 정보가 빠져 있음 | `FBCA04` |
| `ready-for-agent` | `상태: 에이전트 작업 가능` | `ready-for-agent` | 설명과 blocker가 완전해 에이전트가 구현할 수 있음 | `0E8A16` |
| `ready-for-human` | `상태: 사람 검토 필요` | `ready-for-human` | 사람이 승인·권한 부여·병합·수동 작업을 해야 함 | `B60205` |
| `wontfix` | `상태: 진행하지 않음` | `wontfix` | 중복·기구현·거절로 더 진행하지 않음 | `CCCCCC` |

Use this fallback category mapping and keep the category separate from the
single state label:

| Category role | Publish label | Legacy read alias | Description | Suggested color |
| --- | --- | --- | --- | --- |
| `bug` | `유형: 버그` | `bug` | 확인된 잘못된 동작을 수정하는 요청 | `D73A4A` |
| `enhancement` | `유형: 개선` | `enhancement` | 새 동작이나 기존 동작 개선 요청 | `A2EEEF` |

Colors are setup suggestions, not automation identity. Read the legacy category
aliases on existing issues, but never add a Korean category label beside its
English alias. Conflicting recognized categories require issue preparation.

The bundled lease helper also reads the legacy English labels `needs-triage`,
`needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. Use those only
for existing issue compatibility. Never attach both the Korean label and its
English alias; two recognized state labels are a conflict.

## Human action contract

Whenever an issue enters the `needs-info` or `ready-for-human` role, put this
filled block in the issue body or the latest authoritative comment. Do not use a
generic request such as "please review".

```markdown
## 사람에게 필요한 도움

**필요한 이유:** <에이전트가 안전하게 계속할 수 없는 이유>

**요청 종류:** <질문 | 결정 | 승인 | 권한 부여 | 병합 | 수동 작업 | 검토>

**대상:** <질문할 항목, PR, 계정, 권한 또는 시스템을 정확히 식별>

### 해 주실 일

- [ ] <위 대상을 직접 이름 붙인 구체적인 행동 하나>

**답변/결과를 남길 곳:** <이슈 댓글, 연결된 PR 리뷰 또는 지정 시스템>

<!-- `상태: 사람 검토 필요`에서만 아래 필드를 채웁니다. `상태: 정보 필요`이면 생략합니다. -->

**추천 댓글:** <위의 정확한 대상> — 결과: [<허용 결과 1> | <허용 결과 2>]. 판단 근거: [작성]. 완료 증거: [링크 붙여넣기].

**완료 조건:** <요청한 판단이나 작업이 끝났다고 볼 수 있는 관찰 가능한 조건>

**완료 증거:** <이슈 댓글 URL, PR 리뷰 링크, 로그·감사 이벤트 ID 또는 스크린샷 링크>

**완료 후 상태:** <authorized prepare-issue 재검증 후 상태: 에이전트 작업 가능 | 상태: 정보 필요 유지 | 완료 증거와 함께 종료>

**전환 담당:** <prepare-issue | work-github-issue>
```

When repository instructions require English, the bundled helper accepts the
equivalent headings `## Human action required`, `### What to do`, `**Why this
is needed:**`, `**Request type:**`, `**Target:**`, `**Where to respond:**`,
`**Completion condition:**`, `**Completion evidence:**`, and `**State after
completion:**`. Use `**Suggested comment:**` as the English alias of `**추천 댓글:**`.
Format it as `<exact target> — Result: [<accepted result 1> | <accepted result 2>]. Rationale: [write]. Evidence: [paste link].`
The suggested comment must consist only of that target/result/rationale/evidence
shape. Replace the result placeholders with at least two distinct, concrete
outcomes; generic choices such as `choice 1` and duplicate choices are invalid.
Each result choice must also appear in the concrete checklist action or be a
recognized outcome for its request type. Match recognized outcomes exactly:
substring variants, one-character abbreviations, and unrelated but concrete
options are invalid. Review and approval choices must name actual decisions such
as approval, rejection, or changes requested; `comment` and `review outcome` are
not result choices. Choose results that converge on the one next-state destination named in
the block. If the outcomes require different destinations, rewrite or split the
request before publication instead of putting conditional state branches here.
Keep the rationale and evidence fields editable, and make the evidence slot name
a durable reference such as a comment, review, log, URL, ID, or screenshot link.
Use one language per block and add `**Transition owner:**` with `prepare-issue` for an open-state
destination or `work-github-issue` for evidence-backed closure.

For `needs-info`, ask only questions whose answers can change the brief, and
name the accepted format or choices when useful. After the answer arrives,
the person records the answer but does not change the state. An authorized
`prepare-issue` workflow must revalidate the brief and blockers before replacing it
with `상태: 에이전트 작업 가능`; otherwise keep `상태: 정보 필요` with an
updated request. A suggested comment is optional for `needs-info`.

For `ready-for-human`, identify the exact judgment, permission, PR, access, or
manual action, explain the relevant choice or risk, and state what evidence
counts as completion. Include one copy-ready suggested comment that repeats the
exact target and follows the shape above with concrete result choices, rationale,
and evidence-reference slots without claiming the work is already done. The person
performs the named action, edits the suggestion to the actual result, and records its
evidence but does not edit the state label directly. When the action itself creates
the evidence on another surface, such as a PR review, make the response location
an issue comment where the person can post the suggested comment with that
evidence URL. The fallback release validator rejects a PR-review result that tells
the person to post the review's not-yet-created URL back into the same review. If agent work remains, an authorized `prepare-issue`
workflow revalidates and applies the next state. If the human action reaches the
repository completion point, an authorized `work-github-issue` completion flow
records the required evidence and closes the issue.

Do not enter `ready-for-human` for a review or merge already covered by an
applicable standing repository authorization. Complete the authorized local
tests, independent reviews, publication, and readbacks autonomously instead.

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
  exclusive `needs-info|ready-for-human` role, fill the Human action contract
  when either human-wait role is used, keep the issue open, then release as
  `blocked`. Use `ready-for-human` when required approval, access, or merge
  authority belongs to a person.
- **Handoff:** keep the issue open and post branch, HEAD, fixed point, tests,
  local state, publication state, and next action before releasing as `handoff`.
  Use this when another agent or separately authorized workflow can continue.

Every release uses an evidence comment on the leased issue with this Korean
shell. Fill every section; add `## 다음 행동` for `blocked` or `handoff`. The
bundled helper continues to accept the legacy English section headings.

```markdown
<!-- rca-issue-evidence:v1 session=<session> outcome=<completed|blocked|handoff> -->
## 결과
## 변경 사항
## 검증
## 제한 사항
## 안전
## 다음 행동
```

Omit `## 다음 행동` only for `completed`.
