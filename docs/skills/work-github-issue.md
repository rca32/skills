# `work-github-issue`: GitHub 이슈를 안전하게 맡아 처리하기

정확한 실행 계약: [`skills/work-github-issue/SKILL.md`](../../skills/work-github-issue/SKILL.md)

아래 내용은 사람이 흐름을 이해하기 위한 개념 설명입니다. 실제 claim,
worktree 선택, 외부 쓰기와 결과 판정에는 위 실행 계약과 저장소가 선택한
tracker 계약만 권위가 있습니다.

## 한마디로

GitHub 이슈 하나를 **한 에이전트 세션만 안전하게 맡아 구현하고, 검증 증거와 함께 완료하거나 인계하게 하는 바깥 작업 흐름**입니다.

같은 GitHub 계정을 여러 에이전트가 공유하면 assignee만으로는 어느 세션이 작업 중인지 알 수 없습니다. 이 스킬은 원격 Git의 atomic lease ref를 이용해 정확히 한 세션만 작업권을 갖게 합니다.

## lease가 무엇인가요?

lease는 특정 이슈와 에이전트 세션을 묶는 임시 작업권입니다.

- `planning` lease: 이슈 brief, 명세, 하위 티켓, 라벨 같은 계획 상태를 짧게 변경할 때 사용
- `implementation` lease: 실제 코드와 이슈를 구현하고 완료할 때 사용

두 lease는 같은 원격 namespace를 사용하므로 하나의 이슈에서 계획 변경과 구현이 동시에 진행되지 않습니다. lease 목적을 중간에 바꿀 수 없고, 기존 lease를 해제한 다음 새 목적을 다시 획득해야 합니다.

## 기본 상태 라벨은 어떻게 보이나요?

저장소에 별도 tracker 규칙이 없으면 사람이 바로 이해할 수 있는 한국어 라벨을 사용합니다.

| 라벨 | 다음 행동 |
| --- | --- |
| `상태: 분류 필요` | 요청의 사실·범위·종류를 먼저 확인 |
| `상태: 정보 필요` | 이슈에 적힌 구체적인 질문에 사람이 답변 |
| `상태: 에이전트 작업 가능` | blocker가 없다면 에이전트가 claim 가능 |
| `상태: 사람 검토 필요` | 사람이 승인·권한 부여·PR 검토·병합·수동 작업 수행 |
| `상태: 진행하지 않음` | 중복·기구현·거절 근거 확인 후 더 진행하지 않음 |

자동화에서는 각각 `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`라는 역할 키를 사용합니다. 기존 영문 라벨도 읽을 수 있지만, 새 이슈에는 한국어 라벨 하나만 붙입니다.

## 언제 사용하나요?

- 준비된 GitHub 이슈를 실제로 시작할 때
- 중단된 이슈 작업을 이어받을 때
- `prepare-issue`, `to-spec`, `to-tickets`가 GitHub 계획 상태를 게시할 때
- 구현 결과와 테스트 증거를 이슈에 남길 때
- 작업을 완료, 차단 또는 다른 세션에 인계할 때

## 실제 구현 흐름

### 1. 준비 상태 확인

이슈 본문, 댓글, 라벨, 담당자, 부모와 blocker를 모두 읽습니다. 요청과 인수 조건이 완전하고, 저장소가 정한 frontier와 readiness 규칙을 만족해야 합니다. 원시 신고라면 `prepare-issue`, 큰 승인 계획이라면 `to-spec`과 `to-tickets`로 먼저 보냅니다.

구현을 claim하기 전에는 [준비 조건](../../skills/work-github-issue/SKILL.md#1-establish-readiness)에 따라 작업 시작점, 실행 공간, PR과 integration 대상, 단계별 게시 권한, 필수 검사, 완료 지점과 정리 정책을 해석합니다. 별도 정리 규칙이 없을 때는 현재 세션이 새로 만든 안전한 local 작업공간만 정리하는 번들 기본값을 사용합니다. 원격 기본 branch는 참고 정보일 뿐 merge 권한·대상이나 remote branch 삭제 권한을 자동으로 결정하지 않습니다. 요청 결과에 필요한 값이 없거나 충돌하면 claim 전에 멈추고 필요한 결정을 보고합니다.

### 2. 구현 lease 획득

Git 원격 주소, GitHub 인증, tracker 규칙, atomic ref push 권한을 사전 확인합니다. 하나라도 불명확하면 lease를 우회하지 않고 작업 시작을 거부합니다.

다른 활성 세션이 이미 lease를 가지고 있다면 그 이슈를 건드리지 않고 다른 frontier 티켓을 찾습니다. 만료된 lease를 인수할 때도 기존 브랜치, 커밋, 댓글과 작업 증거를 먼저 확인합니다.

### 3. 한 티켓만 구현

티켓 branch에서 인수 조건에 필요한 end-to-end 범위만 구현합니다. [실행 공간 선택 규칙](../../skills/work-github-issue/SKILL.md#3-execute-one-ticket)은 현재 checkout이 이미 ticket branch인 경우에만 그 공간을 사용합니다. 새 ticket branch가 필요하거나 현재 checkout에 관련 없는 변경·공유 작업이 있으면 기존 checkout을 바꾸지 않고 별도 linked worktree를 사용합니다.

사용하려는 ticket branch가 이미 안전하지 않은 다른 worktree에 checkout돼 있다면 강제로 다시 checkout하지 않습니다. 기존 공간을 안전하게 넘겨받거나, 허가된 continuation branch를 사용하거나, 둘 다 불가능하면 작업을 시작하지 않습니다. 실행 공간이 정해진 뒤 그 위치에서 lease를 갱신해 실제 branch와 `HEAD`를 반영합니다.

긴 작업 전에는 lease를 갱신하고, commit, push, 이슈 수정 같은 중요한 쓰기 전에는 현재 세션이 아직 소유자인지 다시 확인합니다.

소유권 확인이 실패하면 즉시 쓰기를 멈추고 로컬 증거를 보존합니다.

### 4. 리뷰와 증거 게시

작업 전 fixed point부터 현재 변경까지 `code-review`로 Standards와 Spec을 각각 검토합니다. [게시 절차](../../skills/work-github-issue/SKILL.md#4-review-and-publish-evidence)는 issue lease와 코드 게시 권한을 분리하고, commit, push, PR과 merge를 허가된 단계까지만 수행하게 합니다.

각 외부 쓰기는 원격 branch, PR, integration target 또는 tracker에서 다시 읽어 확인합니다. 응답이 끊겨 결과를 모르면 같은 작업을 반복하지 않고 고유한 branch·PR·evidence marker를 조회해 성공, 부재 또는 충돌을 먼저 판정합니다. 확인된 fixed point, branch, commit, 게시 상태, 테스트와 제한 사항은 이슈의 권위 있는 evidence 댓글에 기록합니다.

기본 evidence 댓글도 `결과`, `변경 사항`, `검증`, `제한 사항`, `안전`, `다음 행동`이라는 한국어 제목을 사용합니다. 숨은 marker는 자동화가 같은 댓글을 중복 생성하지 않도록 그대로 유지합니다.

### 5. 완료 또는 인계

[완료·인계 절차](../../skills/work-github-issue/SKILL.md#5-resolve-or-hand-off)는 저장소가 선택한 tracker 계약의 `completed`, `blocked`, `handoff` 의미를 따릅니다. `completed`는 모든 인수 조건과 저장소의 완료 지점을 모두 충족한 경우에만 사용할 수 있습니다. 사람의 승인 대기와 다른 에이전트로의 인계가 어떤 상태·outcome이 되는지는 저장소 계약이 우선하며, 별도 계약이 없을 때만 [번들 기본값](../../skills/work-github-issue/references/tracker-contract.md#session-outcomes)을 사용합니다.

`상태: 정보 필요` 또는 `상태: 사람 검토 필요`로 멈출 때는 이슈에 다음 안내가 있어야 합니다.

1. 왜 사람의 도움이 필요한지
2. 요청 종류와 정확한 대상
3. 사람이 해야 할 질문·결정·승인·권한 부여·병합·수동 작업
4. 답변이나 결과를 남길 위치
5. 완료를 확인할 수 있는 조건
6. 완료를 입증하는 댓글·리뷰·로그·링크·ID
7. 완료 후 상태와 그 상태를 적용할 스킬
8. `상태: 사람 검토 필요`라면 사람이 실제 결과로 수정해 바로 남길 수 있는 추천 댓글

사람이 할 일은 예를 들어 “연결된 PR의 보안 변경을 검토하고 승인 또는 수정 요청을 PR 리뷰로 남긴 뒤, 이슈 댓글에서 `prepare-issue` 재검증을 요청해 주세요”처럼 바로 실행할 수 있어야 합니다. “인간 리뷰 필요”만 적고 끝내지 않습니다.

추천 댓글은 실제 검토나 승인을 대신하지 않습니다. 정확한 대상과 허용된 결과 선택지를 미리 적고, 사람이 작업 후 판단 근거와 증거 링크만 채워 안내된 위치에 게시할 수 있게 합니다.

사람은 안내된 위치에서 작업하고 답변·승인·수동 작업의 증거만 남깁니다. 상태 라벨은 직접 바꾸지 않습니다. 에이전트 작업이 남았다면 GitHub 변경 권한을 받은 `prepare-issue`가 새 증거와 blocker를 다시 확인해 `상태: 에이전트 작업 가능`으로 바꾸거나 `상태: 정보 필요`를 유지합니다. 사람의 작업으로 저장소 완료 조건까지 충족됐다면 권한 있는 `work-github-issue` 완료 흐름이 증거를 확인하고 이슈를 종료합니다.

```markdown
## 사람에게 필요한 도움

**필요한 이유:** 결제 권한 변경은 유지보수자의 보안 승인이 있어야 병합할 수 있습니다.

**요청 종류:** 검토

**대상:** PR #128

### 해 주실 일

- [ ] PR #128의 권한 변경을 검토하고 승인 또는 수정 요청을 남겨 주세요.

**답변/결과를 남길 곳:** 이슈 #53 댓글 (승인 또는 수정 요청 자체는 PR #128 리뷰에 등록)

**추천 댓글:** PR #128 — 결과: [승인 | 수정 요청]. 판단 근거: [작성]. 완료 증거: [PR #128 리뷰 링크 붙여넣기].

**완료 조건:** 유지보수자의 승인 리뷰 또는 구체적인 수정 요청이 등록됨

**완료 증거:** PR #128 승인 또는 수정 요청 리뷰 링크

**완료 후 상태:** 승인 또는 수정 요청이 등록되면 authorized `prepare-issue` 재검증 후 `상태: 에이전트 작업 가능`

**전환 담당:** prepare-issue
```

완료한 세션이 새로 만든 linked worktree는 깨끗하고 commit을 복구할 수 있을 때 제거합니다. 그 worktree의 local ticket branch도 exact tip이 보존된 live remote 또는 integration ref에서 복구 가능하고 일반 `git branch -d`가 허용할 때 삭제합니다. 기존·공유·현재 작업공간과 `blocked`·`handoff` 작업은 보존하며, remote branch 삭제에는 저장소 규칙이나 사용자의 명시적 권한과 expected OID를 건 원자적 삭제가 필요합니다.

정리는 lease 해제에 묶지 않습니다. 다른 세션이 같은 이슈를 가져가는 경합을 피하려고 최종 evidence와 release 전에 lease를 다시 확인한 상태에서 수행하고, 제거 결과 또는 보존 이유를 evidence에 기록합니다. 강제 worktree 제거, `git branch -D`, 광범위한 prune은 사용하지 않습니다. release가 확인된 뒤에는 자동 정리를 새로 시작하지 않습니다.

마지막으로 이슈 상태, 부모 관계, 저장소 완료 지점, 게시 상태와 증거가 결과에 맞는지 다시 확인합니다.

## 중요한 안전 원칙

- GitHub assignee가 아니라 원격 lease ref가 세션 소유권의 기준입니다.
- lease가 불확실하거나 외부 쓰기 결과가 unknown이면 해제하거나 재시도하지 않습니다.
- 사용자가 허용한 범위 밖의 commit, push, PR 생성 또는 merge를 하지 않습니다.
- 원격 기본 branch만 보고 PR target이나 merge 대상을 정하지 않습니다.
- 이미 만료된 lease도 기존 작업을 검사하기 전에는 가져오지 않습니다.

## 요청 예시

```text
$work-github-issue 지금 시작 가능한 이슈 하나를 안전하게 맡아 구현하고 검증해 줘.
```
