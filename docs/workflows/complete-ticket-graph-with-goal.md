# Goal로 `to-tickets` 티켓 그래프 끝까지 구현하기

이 문서는 `to-tickets`가 게시한 구현 이슈들을 Codex Goal로 가능한 범위까지
연속 처리하기 위한 kickoff 프롬프트입니다. 정확한 티켓 생성 계약은
[`to-tickets`](../../skills/to-tickets/SKILL.md), claim·구현·게시·완료 계약은
[`work-github-issue`](../../skills/work-github-issue/SKILL.md)가 원본입니다.

Goal의 문구는 첫 요청인 동시에 완료 조건입니다. 따라서 “이슈를 처리해 줘”처럼
활동만 적지 말고 결과, 권한 경계와 검증 가능한 종료 조건을 함께 적어야 합니다.
Goal 시작 자체는 기존 sandbox, 저장소 정책 또는 외부 쓰기 권한을 넓히지 않습니다.
Codex의 현재 Goal 사용법은 [Long-running work](https://learn.chatgpt.com/docs/long-running-work)를
참고하세요.

## 시작 전에 정할 값

아래 kickoff의 `<...>`를 실제 값으로 바꿉니다.

- canonical GitHub 저장소와 `to-tickets`의 source/parent issue
- ticket base, PR target, 최종 integration target
- merge 방식, 필수 checks와 사람 승인 필요 여부
- remote ticket branch 삭제 허용 여부

이 값들이 consuming repository의 `AGENTS.md`나 publication 문서에 이미 정확히
정의되어 있다면 `저장소 계약을 따른다`고 적어도 됩니다. 서로 충돌하는 값이나
필수 값이 없으면 Codex가 임의로 정하지 않고 해당 필드에서 멈추는 것이 정상입니다.

## Kickoff 프롬프트

Codex에서 `/goal`을 시작한 뒤 다음 블록을 붙여 넣습니다. 한 Goal은 티켓을
순차적으로 처리합니다. 별도 세션을 병렬로 실행할 때는 각 세션이 서로 다른
티켓 lease와 worktree를 사용하게 해야 합니다.

```text
$work-github-issue를 사용해 아래 `to-tickets` 티켓 그래프를 저장소의 실제 완료
지점까지 처리하라. PR 생성만으로 이슈나 이 Goal을 완료하지 마라.

대상
- canonical repository: <owner/name>
- source/parent issue: #<번호>
- 범위: 위 parent에 연결되고 동일한 `to-tickets:v1` source/revision에서 생성된
  구현 child issue. 관련 없는 이슈와 새 요구사항은 포함하지 않는다.

실행·게시 계약
- ticket base: <branch 또는 저장소 계약>
- PR target: <branch>
- integration target: <branch>
- 권한: 각 티켓의 코드 수정, 테스트, commit, ticket branch push, PR 생성·갱신,
  이슈 evidence/상태 갱신, 필수 checks 확인, 아래 조건을 만족한 PR merge,
  완료된 child issue 종료와 parent 진행 상태 갱신을 허가한다.
- merge 방식: <squash|merge commit|rebase|저장소 계약>
- merge 조건: <필수 checks 통과 및 필요한 승인 조건>
- 완료 지점: 변경이 integration target에 포함되고 checks가 통과하며, 모든 인수
  조건의 evidence가 child issue에 기록되고 child issue와 lease가 완료된 상태다.
- 정리: evidence와 lease release를 read back한 뒤 commit이 원격에서 복구 가능한
  clean disposable worktree를 제거하고 merged local ticket branch를 삭제해도 된다.
  merged remote ticket branch 삭제는 <허용|금지>한다.

루프
1. parent, child 본문·댓글·상태·assignee·dependency·기존 branch/PR과 전체
   publication 계약을 다시 읽고 그래프 및 현재 frontier를 재구성한다.
2. readiness와 publication preflight를 통과한 unblocked `ready-for-agent` 티켓
   하나를 고른다. 활성 lease가 있는 티켓은 건드리지 않고 다른 frontier를 찾는다.
3. implementation lease를 획득한 뒤 고정된 base에서 전용 branch/worktree를
   사용한다. 관련 없는 dirty state를 정리·stash·reset하거나 덮어쓰지 않는다.
4. 인수 조건을 end-to-end로 구현하고 적절한 최고 공개 seam에서 테스트한다.
   focused test와 전체 관련 suite를 실행하고 Standards와 Spec을 독립적으로
   review하여 blocker/high 및 안전·소유권 관련 medium finding을 해결한다.
5. lease ownership을 확인하고 commit, push, PR 생성 또는 갱신까지 수행한다.
   pending checks는 결과가 날 때까지 확인한다. 티켓 변경으로 실패한 check는
   진단·수정하고 다시 검증한다.
6. merge 조건과 권한이 충족되면 지정 방식으로 merge하고 integration target에
   정확한 변경이 포함됐는지 read back한다. 그 뒤 evidence 기록, child issue
   종료, parent pointer 갱신, lease release를 확인하고 허가된 cleanup을 수행한다.
7. 그래프를 새로 읽고 다음 frontier 티켓으로 반복한다. 한 PR을 열었거나 한
   티켓을 끝냈다는 이유로 Goal을 종료하지 않는다.

중단·복구
- 외부 쓰기 결과가 unknown이면 재시도하지 말고 원격 branch, PR, tracker의
  고유 상태를 조회해 present exactly once 또는 absent를 먼저 판정한다.
- merge 권한·필수 승인·정보가 부족한 티켓은 정확한 사람 행동, 대상, 응답 위치,
  완료 조건과 증거를 기록해 tracker 계약의 blocked/handoff 상태로 둔다. 다른
  독립 frontier가 있으면 계속 처리한다.
- 충돌, 인프라 장애, 관련 없는 check 실패 또는 안전하지 않은 worktree는 증거와
  다음 안전 행동을 남기고 보존한다. 범위를 넓혀 우회하지 않는다.

Goal 완료 조건
- 범위 안의 모든 child issue가 저장소 completion point에 도달했고 닫혔다.
- parent의 모든 인수 조건과 dependency가 충족됐으며, 계약이 허가하면 parent도
  evidence와 함께 완료됐다.
- 열린 agent-actionable 티켓, 미확정 publication 결과, 활성 lease, 미보고 작업
  공간이 없고 cleanup 결과가 확인됐다.
- 사람의 결정·승인·권한 때문에 남은 이슈가 하나라도 있으면 Goal을 complete로
  표시하지 말고 blocked로 보고한다.
```

## 기대되는 종료 모습

정상 완료에서는 각 child issue가 단순히 PR 링크만 가진 상태가 아니라 merge된
변경의 검증 증거, 완료된 issue 상태와 해제된 lease를 가집니다. 작업용 worktree는
깨끗하고 원격에서 복구 가능할 때 제거됩니다.

사람 승인이나 권한이 반드시 필요한 저장소라면 완전 자동 merge는 불가능합니다.
이 경우 Goal은 처리 가능한 다른 frontier를 계속 소진한 뒤, 남은 정확한 사람
행동과 증거 위치를 보고하고 `blocked`로 남아야 합니다. 이것은 조기 완료가 아니라
권한 경계를 지킨 정상적인 비완료 결과입니다.
