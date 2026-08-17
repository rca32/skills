# Codex 개발 스킬 모음

이 저장소는 제가 여러 프로젝트에서 반복해서 사용하는 Codex 업무 방식을 모아 둔 곳입니다.

여기서 **스킬(skill)**은 Codex에게 “이 종류의 일은 어떤 순서로, 무엇을 확인하며, 어디까지 해야 하는지” 알려 주는 작은 업무 매뉴얼입니다. 스킬을 설치하면 매번 긴 지시를 다시 쓰지 않아도 같은 품질과 안전 규칙으로 일을 시작할 수 있습니다.

## 이 저장소가 해결하는 문제

- 막연한 요청을 바로 코딩하지 않고 먼저 확인하고 정리합니다.
- 중요한 결정의 상속된 전제와 관행을 사실·제약·가정으로 분리해 다시 검토합니다.
- 새 서비스가 사람들이 선택하고 머무를 이유와 방어 가능한 경쟁 우위 조합을 찾습니다.
- 큰 기능을 한 번에 만들지 않고 검증 가능한 작은 작업으로 나눕니다.
- 버그의 원인을 추측으로 고치지 않고 재현과 증거로 찾습니다.
- 큰 코드베이스에서 복잡도와 성능 hotspot을 찾고 동작을 보존하며 최적화합니다.
- 테스트를 먼저 작성해 새 기능과 버그 수정을 안전하게 진행합니다.
- 실제 산출물을 구체적인 품질 기준과 비교하고, 독립 작업자와 평가자로 반복 개선합니다.
- 구현이 요구사항과 저장소 규칙을 모두 만족하는지 따로 검토합니다.
- 같은 GitHub 계정을 공유하는 여러 에이전트 세션이 같은 이슈를 동시에 수정하지 못하게 막습니다.

## 어떤 스킬을 언제 쓰나요?

| 스킬 | 이런 때 사용합니다 | 하는 일 |
| --- | --- | --- |
| `bro` | 마지막 메시지를 쉽게 다시 말해 달라고 할 때 | 전문 용어를 빼고 핵심 의미를 유지한 채 더 간단하고 자연스럽게 다시 씁니다. |
| `prepare-issue` | 새 이슈가 모호하거나 정말 작업할 준비가 됐는지 모르겠을 때 | 버그인지 기능 요청인지 분류하고, 실제 문제인지 확인한 뒤 작업 설명을 완성합니다. |
| `first-principles` | 중요한 제품·기술·업무 결정의 문제 정의나 상속된 전제를 원점에서 다시 검토할 때 | 관측 사실·고정 제약·가정·추론·선호를 분리해 최소 방안과 남은 검증을 제안합니다. 명시적으로 호출하며 설계나 구현은 맡지 않습니다. |
| `find-competitive-edge` | 새 서비스의 경쟁 전략을 기획하거나 기존 제품·조직·네트워크의 강점과 moat를 분석할 때 | 경쟁 자원과 선택 행동을 밝히고, 74개 전략 벡터에서 소수의 핵심·보조·방어 조합과 검증 실험을 도출합니다. |
| `domain-modeling` | 설계 중 도메인 용어·불변식·상태·경계의 의미를 적극적으로 다듬을 때 | 예시·반례·edge case로 모델을 검증하고, 합의된 변경과 제안을 구분해 다음 명세와 구현이 같은 의미를 사용하게 합니다. |
| `codebase-design` | module interface나 seam을 결정하거나 얕은 구조를 합치고 싶을 때 | 여러 설계안을 depth·locality·testability로 비교해 구현 전에 하나를 추천합니다. |
| `decision-map` | 한 세션에 담기 어려운 큰 작업의 결정 경로가 아직 흐릴 때 | 목적지와 fog를 작은 로컬 결정 문서로 관리하고 하나씩 해결해 명세 가능한 상태를 만듭니다. |
| `to-spec` | 대화에서 결정한 내용을 문서로 정리하고 싶을 때 | 개발 기준이 되는 작은 명세와, 그 명세에서만 파생된 별도의 쉬운 설명을 만듭니다. |
| `to-tickets` | 하나의 명세가 커서 여러 작업으로 나눠야 할 때 | 새 설계 결정을 하지 않고 분해 가능한지 먼저 확인한 뒤 작은 이슈와 선행 관계를 만듭니다. 설계가 미정이면 티켓 생성 전에 중단합니다. |
| `local-work` | 한 에이전트가 GitHub issue 없이 명세를 순차 구현할 때 | spec에 묶인 작은 로컬 item을 만들고 현재 worktree에서 TDD·검증·최종 리뷰까지 진행합니다. |
| `documenting-work` | 명세·결정·진단·리뷰를 어디에 남겨야 할지 정할 때 | 대화, GitHub, 저장소 문서, 실행 artifact 중 원본 하나를 정하고 표준 위치·이름·인덱스를 적용합니다. |
| `work-github-issue` | GitHub 이슈를 실제로 시작하거나 지속 goal에서 여러 이슈를 처리할 때 | goal thread는 조정만 맡고 이슈마다 새 worker를 시작합니다. worker는 전용 임대로 충돌을 막으며 검증·리뷰·PR 병합·정리까지 한 이슈만 완료합니다. |
| `diagnosing-bugs` | 오류, 간헐적 실패, 속도 저하의 원인을 찾을 때 | 재현 방법을 만들고 가능한 원인을 하나씩 반증해 실제 원인을 찾습니다. “진단만” 요청했다면 코드를 고치지 않습니다. |
| `complexity-optimizer` | 비효율적인 반복·재계산·N+1과 알고리즘 hotspot을 찾거나 개선할 때 | scanner와 코드 문맥으로 후보를 순위화하고, 동작을 보존하는 작은 최적화와 검증 방법을 제안하거나 구현합니다. |
| `tdd` | 기능을 만들거나 버그를 테스트부터 고칠 때 | 실패하는 테스트를 먼저 확인하고, 최소 구현과 정리를 작은 단위로 반복합니다. |
| `quality-gauntlet` | 레퍼런스·benchmark·rubric과 비교하며 산출물을 여러 차례 개선할 때 | 실제 산출물을 고정해 독립 builder와 critic이 가장 큰 품질 격차를 하나씩 줄이도록 조정합니다. |
| `code-review` | 커밋이나 PR 전 변경 전체를 검토할 때 | 후보와 축마다 대화 이력을 상속하지 않는 새 리뷰어가 저장소 규칙과 원래 요구사항을 서로 섞지 않고 검토합니다. |
| `writing-great-skills` | Codex 스킬을 새로 만들거나 기존 스킬을 다듬을 때 | 호출 조건, 작업 분기, 완료 기준, 안전 경계를 점검해 스킬이 매번 예측 가능한 절차를 따르게 합니다. |

## 가장 흔한 사용 흐름

```text
새 요청
  → bro?                  마지막 메시지를 평이한 말로 다시 표현
  → first-principles?      명시 호출 시 문제 framing과 상속된 전제를 재검토
  → find-competitive-edge? 선택·잔존 메커니즘과 방어 가능한 전략 조합 분석
  → prepare-issue           요청이 실제로 준비됐는지 확인
  → decision-map?          여러 세션이 필요한 fog와 결정을 순차 문서로 해소
      → domain-modeling?   결정 중 도메인 언어·불변식·경계를 검증
      → codebase-design?   결정 중 interface·seam 추천안을 마련
  → to-spec                합의 내용을 명세로 정리
      ├─ local-work        한 에이전트가 현재 worktree에서 순차 구현
      │   → tdd → code-review
      └─ to-tickets        공유할 큰 명세를 작은 GitHub 이슈로 분해
          → work-github-issue 이슈별 worker가 tdd·검증·review·인계를 수행
```

모든 작업에 전부 사용할 필요는 없습니다. 경쟁 구도와 moat를 먼저 세워야 하는 새 서비스라면 `find-competitive-edge`로 전략 가설과 검증 방법을 만들고, 합의된 요구사항은 이후 계획 workflow로 넘깁니다. 결정 경로가 흐린 큰 일만 `decision-map`을 사용하고, 이미 합의가 충분하면 바로 `to-spec`으로 갑니다. 한 에이전트가 순차 처리하고 원격 추적이 필요 없다면 `local-work`, 여러 작업자·세션의 공유 가시성과 충돌 방지가 필요하면 `to-tickets → work-github-issue`를 선택합니다. `first-principles`는 사용자가 이름을 직접 불러 중요한 결정의 문제 framing이나 상속된 전제를 재검토할 때만 사용합니다. `domain-modeling`은 도메인 개념·불변식·상태·경계를 실제로 바꾸거나 모호함을 해결할 때, `codebase-design`은 interface나 seam 선택이 실제로 열려 있을 때 사용합니다. 작은 로컬 변경은 `tdd`와 `code-review`만으로 충분할 수 있습니다. `quality-gauntlet`은 사용자가 직접 호출했고 실제 산출물·검사 방법·비교 품질 기준이 있을 때만 사용합니다.

각 스킬의 동작과 안전 경계를 더 쉽게 풀어 쓴 설명은 [한국어 스킬 안내서](docs/README.md)에서 볼 수 있습니다.

## 문서는 어디에 저장되나요?

`documenting-work`는 결과를 무조건 파일로 만들지 않습니다. 먼저 얼마나 오래 보관해야 하는지와 어느 시스템이 원본인지 정합니다.

| 보관 방식 | 사용하는 경우 | 기본 동작 |
| --- | --- | --- |
| 대화 응답 | 초안, 일회성 진단, 코드 리뷰 | 파일을 만들지 않고 응답으로 반환합니다. |
| GitHub | Agent brief, 구현 티켓, 완료 증거, 이슈 인계 | Issue·PR·댓글·의존 관계가 원본입니다. 로컬에는 전체 내용을 복사하지 않습니다. |
| 저장소 문서 | 코드와 함께 검토·버전 관리해야 하는 명세, 결정, 연구 | 프로젝트 규칙을 따르고, 없으면 아래 fallback을 사용합니다. |
| 실행 artifact | 로그, trace, screenshot, benchmark 결과 | 프로젝트의 artifact 위치와 보존 정책을 사용하며 `docs/`에 원시 출력을 넣지 않습니다. |

프로젝트에 별도 규칙이 없을 때의 저장소 fallback은 다음과 같습니다.

```text
docs/README.md                          문서 인덱스
docs/domain.md                          프로젝트 도메인 모델과 용어
docs/specs/                             제품·개발 명세
docs/spec-explainers/                   명세에서 파생된 비규범적 쉬운 설명
docs/decision-maps/                      큰 작업의 순차 결정 지도와 결정 문서
docs/local-work/                         spec에 묶인 로컬 실행 item과 진행 상태
docs/decisions/                         아키텍처·제품 결정
docs/research/                          장기 보관할 조사 결과
docs/reports/diagnostics/               요청받은 진단 보고서
docs/reports/reviews/                   요청받은 코드 리뷰 보고서
```

이슈와 연결된 파일은 `issue-42-payment-retry.md`, 연결된 이슈가 없으면 `2026-07-13-payment-retry.md`처럼 이름을 만듭니다. 같은 지식을 GitHub와 Markdown 양쪽에 복사하지 않고, 원본이 아닌 쪽에는 링크만 남깁니다. `spec-explainer`와 `local-work`는 원본 spec ID와 정확한 fingerprint에 묶인 명시적 비규범 projection입니다. `decision-map`은 map을 인덱스로만 쓰고 각 결정 상세를 하나의 child 문서에 둡니다. 프로젝트의 `AGENTS.md`, 문서 인덱스, 기존 ADR 규칙이 있다면 항상 fallback보다 우선합니다.

## 같은 계정을 쓰는 여러 에이전트가 왜 충돌하지 않나요?

GitHub의 담당자 표시만으로는 부족합니다. 여러 세션이 같은 GitHub 계정으로 보이기 때문입니다.

`work-github-issue`는 이슈 번호와 에이전트 세션을 묶은 별도 임대를 원격 Git에 원자적으로 생성합니다. 먼저 임대한 세션만 파일을 수정할 수 있고, 다른 세션은 현재 소유자를 확인한 뒤 멈춥니다. 이슈 라벨·명세·하위 이슈를 게시하는 짧은 작업도 같은 임대 방식으로 직렬화하므로, 두 세션이 똑같은 계획 이슈를 만드는 것도 막습니다. 임대가 만료되거나 작업을 넘겨받을 때는 기존 브랜치·커밋·테스트·이슈 상태를 먼저 확인합니다.

다른 스킬은 이 임대를 직접 만들거나 해제하지 않습니다. 이 단일 소유권 규칙 덕분에 스킬을 조합해도 충돌 방지 방식이 달라지지 않습니다.

## 설치

Codex에게 다음처럼 요청하면 됩니다.

> `rca32/skills` 저장소에서 `bro`, `prepare-issue`, `first-principles`, `find-competitive-edge`, `domain-modeling`, `codebase-design`, `decision-map`, `to-spec`, `local-work`, `to-tickets`, `work-github-issue`, `documenting-work`, `diagnosing-bugs`, `complexity-optimizer`, `tdd`, `quality-gauntlet`, `code-review`, `writing-great-skills` 스킬을 설치해 줘.

또는 이미 설치된 `skill-installer`로 `skills/<스킬 이름>` 경로를 선택해 설치할 수 있습니다. 설치가 끝난 뒤 새 세션을 시작하면 스킬 목록이 갱신됩니다.

설치된 `${CODEX_HOME:-$HOME/.codex}/skills`는 사용용 복사본입니다. 스킬을 수정할 때는 이 저장소를 고치고 검증·push한 뒤 다시 설치합니다.

`work-github-issue` 스킬 설치만으로 개인 Codex 설정을 바꾸지는 않습니다. 이슈별 context-isolated worker에 번들된 Luna 프로필을 사용하려면 “`$work-github-issue`로 개인 `luna_worker` 호환성을 점검하고 diff를 보여준 뒤 설치해 줘”라고 명시적으로 요청합니다. 스킬은 설치된 Codex 버전과 `gpt-5.6-luna`의 `max` reasoning 지원을 확인하고, 기존 `${CODEX_HOME:-$HOME/.codex}/agents/luna-worker.toml`이 다르면 덮어쓰지 않고 중단합니다. 설치가 끝난 뒤 새 Codex 세션을 시작해야 프로필이 검색됩니다.

## 처음 사용할 프로젝트의 준비 사항

GitHub 이슈 작업을 시작하기 전에 프로젝트에 다음이 준비되어 있어야 합니다.

- Git, Python 3, GitHub CLI(`gh`)가 설치되어 있어야 합니다.
- `gh auth status`가 작업에 사용할 GitHub 계정으로 로그인됐다고 표시해야 합니다.
- `origin` 같은 임대용 원격 저장소가 `https://github.com/owner/repo.git` 또는 이에 해당하는 정식 SSH 주소를 가리켜야 합니다.
- 그 계정은 이슈를 읽고 수정할 권한과 원격 임대 ref를 push할 권한이 있어야 합니다.
- 프로젝트 문서에 이슈 상태 라벨과 선행 작업 표시 방법이 정의되어 있어야 합니다. 별도 규칙이 없다면 `work-github-issue`의 기본 계약은 `상태: 분류 필요`, `상태: 정보 필요`, `상태: 에이전트 작업 가능`, `상태: 사람 검토 필요`, `상태: 진행하지 않음` 중 하나를 상태로 사용합니다. 기존 영문 라벨은 호환을 위해 읽을 수 있지만 새 이슈에는 한국어 라벨을 사용합니다.
- 구현 전에는 ticket base와 worktree 조건만 확정하고, push·PR·merge에 필요한 값은 해당 작업 직전에 단계적으로 확정합니다. 충돌하는 지침이 없고 원격 기본 branch가 하나뿐이면 base와 PR target으로 사용할 수 있지만 merge나 remote branch 삭제 권한을 뜻하지 않습니다. 별도 정리 규칙이 없으면 완료한 세션이 직접 만든 안전한 linked worktree와 local ticket branch만 기본 정리합니다.

`work-github-issue`는 소비 저장소의 `AGENTS.md`에 publication 정책을 설치하거나 merge 권한을 부여하지 않습니다. push·PR·merge 권한과 방식은 기존 저장소 지침 또는 현재 사용자 요청에서 확인하며, 필요한 권한이 없으면 그 작업 직전에 멈춰 정확한 결정을 요청합니다.

기본 tracker 라벨은 선택 사항입니다. 사람이 보기 편한 한국어 상태·유형 라벨을 준비하려면 먼저 읽기 전용으로 전체 label catalog를 확인합니다.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  check /absolute/path/to/repository --remote origin
```

누락 라벨 생성을 명시적으로 허가한 경우에만 다음 초기화 절차를 실행합니다. source 또는 parent 이슈가 있으면 그 번호를 `LEASE_KEY`로 사용하고, source가 없는 저장소 전체 설정 요청에만 `0`을 사용합니다.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim LEASE_KEY --purpose planning --ttl-minutes 10 --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  install /absolute/path/to/repository --remote origin \
  --lease-key LEASE_KEY \
  --lease-session SESSION_FROM_CLAIM \
  --expected-snapshot LABEL_SNAPSHOT_FROM_CHECK

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  check LEASE_KEY --session SESSION_FROM_CLAIM --remote origin

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_tracker_labels.py" \
  check /absolute/path/to/repository --remote origin

# 위 check가 current를 반환한 뒤 해제합니다.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  release LEASE_KEY --session SESSION_FROM_CLAIM --remote origin
```

`check`가 반환한 opaque `snapshot`을 `install`에 전달합니다. 라벨 외부 쓰기는 repository-wide planning lease로 보호하며, installer는 누락 라벨만 생성하고 기존 라벨을 수정·이름 변경·삭제하지 않습니다. 설치 뒤 전체 catalog가 `current`인지 다시 읽은 후 lease를 해제합니다. 확신이 없다면 Codex에게 “이 저장소의 `work-github-issue` tracker 라벨 상태를 읽기 전용으로 점검해 줘”라고 요청하면 됩니다. 라벨을 만들지 않아도 이슈 body marker를 사용해 계속 작업할 수 있습니다.

`상태: 정보 필요`나 `상태: 사람 검토 필요`인 이슈에는 라벨만 붙이지 않습니다. 이슈 본문 또는 최신 댓글에 요청 종류와 정확한 대상, 사람이 해야 할 일, 답변 위치, 완료 조건, 완료 후 상태와 전환 담당 스킬을 함께 적습니다. `상태: 사람 검토 필요`라면 사람이 작업 후 바로 수정해 남길 수 있는 추천 댓글도 제공합니다. 예를 들어 “검토 필요” 대신 “PR #128의 권한 변경을 검토하고 승인 또는 수정 요청을 PR 리뷰로 남긴 뒤, 권한 있는 `prepare-issue`에 재검증을 요청해 주세요”처럼 작성합니다.

선택된 tracker 라벨이 없으면 `to-spec`, `prepare-issue`, `to-tickets`는 이슈 body의 상태 marker를 사용해 계속 진행합니다. 라벨은 별도 권한이 있을 때만 생성하는 선택적 human-facing projection입니다.

## 사용 예시

```text
$prepare-issue 이슈 #42가 에이전트가 작업할 만큼 구체적인지 확인해 줘.
$bro 방금 답변을 전문 용어 없이 더 쉽게 다시 말해 줘.
$first-principles 마이크로서비스 전환이 정말 필요한지 관측 사실과 고정 제약부터 다시 검토해 줘.
$find-competitive-edge 새로운 동네 운동 모임 서비스가 사람들이 가입하고 계속 참여할 경쟁 우위 조합을 분석해 줘.
$domain-modeling 주문·결제·환불 용어와 상태 경계를 edge case로 검증해 줘.
$codebase-design 이 결제 흐름의 module interface와 seam 대안을 비교하고 하나를 추천해 줘.
$decision-map 결제 시스템 재설계처럼 아직 결정할 것이 많은 큰 작업을 로컬 결정 지도로 시작해 줘.
$to-spec 지금까지 합의한 결제 재시도 정책을 명세로 정리해 줘.
$local-work docs/specs/payment-retry.md를 로컬 item으로 나누고 순서대로 구현해 줘.
$to-tickets 승인된 이슈 #50을 한국어로 이해하기 쉬운 작은 이슈로 나누고 게시해 줘.
$documenting-work 이 설계 문서의 원본 위치와 표준 파일명을 정해 줘.
$work-github-issue 현재 시작할 수 있는 이슈 하나를 안전하게 맡아서 완료해 줘.
$diagnosing-bugs 간헐적인 타임아웃의 원인만 진단해 줘. 아직 수정하지 마.
$complexity-optimizer 이 코드베이스의 복잡도와 성능 hotspot을 분석하고 전체 보고서를 작성해 줘.
$tdd 이 변경을 공개 인터페이스 테스트부터 구현해 줘.
$quality-gauntlet 이 대시보드를 승인된 레퍼런스와 나란히 비교하며 독립 builder와 critic으로 반복 개선해 줘.
$code-review 커밋 전 현재 작업 전체를 규칙과 명세 기준으로 검토해 줘.
$writing-great-skills 이 스킬의 호출 조건과 완료 기준을 더 예측 가능하게 고쳐 줘.
```

`bro`, `prepare-issue`, `first-principles`, `decision-map`, `to-spec`, `local-work`, `to-tickets`는 의도하지 않은 문서·코드·이슈 변경을 피하기 위해, `quality-gauntlet`은 고비용 다중 에이전트 반복을 뜻하기 때문에 이름을 직접 불러 사용합니다. 또한 “검토해 줘”, “초안을 만들어 줘”는 파일 수정이나 외부 게시 권한을 뜻하지 않습니다.

## 저장소를 관리할 때

각 스킬은 `skills/<스킬 이름>/`에 있습니다. 기본 구조는 다음과 같습니다.

```text
SKILL.md             에이전트가 따르는 핵심 업무 계약
agents/openai.yaml   스킬 목록에 표시되는 이름과 시작 문장
references/          필요할 때만 읽는 상세 규칙과 템플릿
scripts/             반복 작업을 안전하게 실행하는 도구
```

변경한 스킬은 구조 검사를 통과해야 합니다.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/<스킬 이름>
```

스크립트가 포함된 스킬은 해당 테스트도 실행합니다.

```bash
python3 skills/work-github-issue/scripts/test_issue_lease.py -v
python3 skills/work-github-issue/scripts/test_configure_luna_worker.py -v
python3 skills/to-tickets/scripts/test_source_fingerprint.py -v
python3 skills/to-spec/scripts/test_fingerprint_spec.py -v
python3 skills/to-spec/scripts/test_envelope_artifact.py -v
python3 skills/documenting-work/scripts/test_resolve_document_path.py -v
python3 skills/complexity-optimizer/scripts/test_analyze_complexity.py -v
python3 skills/complexity-optimizer/scripts/analyze_complexity.py . --format json
bash -n skills/diagnosing-bugs/scripts/hitl-loop.template.sh
```

에이전트용 상세 작성·검증·배포 계약은 [AGENTS.md](AGENTS.md)에 있습니다.
