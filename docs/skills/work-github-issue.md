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

## 언제 사용하나요?

- 준비된 GitHub 이슈를 실제로 시작할 때
- 중단된 이슈 작업을 이어받을 때
- `triage`, `to-spec`, `to-tickets`가 GitHub 계획 상태를 게시할 때
- 구현 결과와 테스트 증거를 이슈에 남길 때
- 작업을 완료, 차단 또는 다른 세션에 인계할 때

## 실제 구현 흐름

### 1. 준비 상태 확인

이슈 본문, 댓글, 라벨, 담당자, 부모와 blocker를 모두 읽습니다. 요청과 인수 조건이 완전하고, 저장소가 정한 frontier와 readiness 규칙을 만족해야 합니다. 원시 신고라면 `triage`, 큰 승인 계획이라면 `to-spec`과 `to-tickets`로 먼저 보냅니다.

구현을 claim하기 전에는 [준비 조건](../../skills/work-github-issue/SKILL.md#1-establish-readiness)에 따라 작업 시작점, 실행 공간, PR과 integration 대상, 단계별 게시 권한, 필수 검사, 완료 지점과 정리 정책을 해석합니다. 원격 기본 branch는 참고 정보일 뿐 merge 권한이나 대상을 자동으로 결정하지 않습니다. 요청 결과에 필요한 값이 없거나 충돌하면 claim 전에 멈추고 필요한 결정을 보고합니다.

### 2. 구현 lease 획득

Git 원격 주소, GitHub 인증, tracker 규칙, atomic ref push 권한을 사전 확인합니다. 하나라도 불명확하면 lease를 우회하지 않고 작업 시작을 거부합니다.

다른 활성 세션이 이미 lease를 가지고 있다면 그 이슈를 건드리지 않고 다른 frontier 티켓을 찾습니다. 만료된 lease를 인수할 때도 기존 브랜치, 커밋, 댓글과 작업 증거를 먼저 확인합니다.

### 3. 한 티켓만 구현

티켓 branch에서 인수 조건에 필요한 end-to-end 범위만 구현합니다. [실행 공간 선택 규칙](../../skills/work-github-issue/SKILL.md#3-execute-one-ticket)은 현재 checkout에 관련 없는 변경이나 공유 작업이 있으면 그것을 건드리지 않고 별도 worktree를 사용하게 합니다.

사용하려는 ticket branch가 이미 안전하지 않은 다른 worktree에 checkout돼 있다면 강제로 다시 checkout하지 않습니다. 기존 공간을 안전하게 넘겨받거나, 허가된 continuation branch를 사용하거나, 둘 다 불가능하면 작업을 시작하지 않습니다. 실행 공간이 정해진 뒤 그 위치에서 lease를 갱신해 실제 branch와 `HEAD`를 반영합니다.

긴 작업 전에는 lease를 갱신하고, commit, push, 이슈 수정 같은 중요한 쓰기 전에는 현재 세션이 아직 소유자인지 다시 확인합니다.

소유권 확인이 실패하면 즉시 쓰기를 멈추고 로컬 증거를 보존합니다.

### 4. 리뷰와 증거 게시

작업 전 fixed point부터 현재 변경까지 `code-review`로 Standards와 Spec을 각각 검토합니다. [게시 절차](../../skills/work-github-issue/SKILL.md#4-review-and-publish-evidence)는 issue lease와 코드 게시 권한을 분리하고, commit, push, PR과 merge를 허가된 단계까지만 수행하게 합니다.

각 외부 쓰기는 원격 branch, PR, integration target 또는 tracker에서 다시 읽어 확인합니다. 응답이 끊겨 결과를 모르면 같은 작업을 반복하지 않고 고유한 branch·PR·evidence marker를 조회해 성공, 부재 또는 충돌을 먼저 판정합니다. 확인된 fixed point, branch, commit, 게시 상태, 테스트와 제한 사항은 이슈의 권위 있는 evidence 댓글에 기록합니다.

### 5. 완료 또는 인계

[완료·인계 절차](../../skills/work-github-issue/SKILL.md#5-resolve-or-hand-off)는 저장소가 선택한 tracker 계약의 `completed`, `blocked`, `handoff` 의미를 따릅니다. `completed`는 모든 인수 조건과 저장소의 완료 지점을 모두 충족한 경우에만 사용할 수 있습니다. 사람의 승인 대기와 다른 에이전트로의 인계가 어떤 상태·outcome이 되는지는 저장소 계약이 우선하며, 별도 계약이 없을 때만 [번들 기본값](../../skills/work-github-issue/references/tracker-contract.md#session-outcomes)을 사용합니다.

Lease 해제와 동시에 branch나 worktree를 자동으로 삭제하지 않습니다. 증거와 release가 확인된 뒤, 깨끗하고 commit을 복구할 수 있는 disposable worktree만 허가된 정리 규칙에 따라 제거합니다. Branch 삭제는 별도 권한이 필요하며, 미게시·미커밋·untracked 상태가 있으면 작업 공간을 보존합니다.

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
