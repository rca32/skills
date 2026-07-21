# Codex 개발 스킬 모음

이 저장소는 제가 여러 프로젝트에서 반복해서 사용하는 Codex 업무 방식을 모아 둔 곳입니다.

여기서 **스킬(skill)**은 Codex에게 “이 종류의 일은 어떤 순서로, 무엇을 확인하며, 어디까지 해야 하는지” 알려 주는 작은 업무 매뉴얼입니다. 스킬을 설치하면 매번 긴 지시를 다시 쓰지 않아도 같은 품질과 안전 규칙으로 일을 시작할 수 있습니다.

## 이 저장소가 해결하는 문제

- 막연한 요청을 바로 코딩하지 않고 먼저 확인하고 정리합니다.
- 큰 기능을 한 번에 만들지 않고 검증 가능한 작은 작업으로 나눕니다.
- 버그의 원인을 추측으로 고치지 않고 재현과 증거로 찾습니다.
- 큰 코드베이스에서 복잡도와 성능 hotspot을 찾고 동작을 보존하며 최적화합니다.
- 테스트를 먼저 작성해 새 기능과 버그 수정을 안전하게 진행합니다.
- 구현이 요구사항과 저장소 규칙을 모두 만족하는지 따로 검토합니다.
- 같은 GitHub 계정을 공유하는 여러 에이전트 세션이 같은 이슈를 동시에 수정하지 못하게 막습니다.

## 어떤 스킬을 언제 쓰나요?

| 스킬 | 이런 때 사용합니다 | 하는 일 |
| --- | --- | --- |
| `prepare-issue` | 새 이슈가 모호하거나 정말 작업할 준비가 됐는지 모르겠을 때 | 버그인지 기능 요청인지 분류하고, 실제 문제인지 확인한 뒤 작업 설명을 완성합니다. |
| `codebase-design` | module interface나 seam을 결정하거나 얕은 구조를 합치고 싶을 때 | 여러 설계안을 depth·locality·testability로 비교해 구현 전에 하나를 추천합니다. |
| `to-spec` | 대화에서 결정한 내용을 문서로 정리하고 싶을 때 | 이미 합의된 내용만 모아 제품·개발 명세를 만듭니다. 모르는 요구사항을 임의로 만들지 않습니다. |
| `to-tickets` | 하나의 명세가 커서 여러 작업으로 나눠야 할 때 | 각각 완성 결과를 확인할 수 있는 작은 이슈로 나누고, 먼저 끝나야 하는 작업을 연결합니다. |
| `documenting-work` | 명세·결정·진단·리뷰를 어디에 남겨야 할지 정할 때 | 대화, GitHub, 저장소 문서, 실행 artifact 중 원본 하나를 정하고 표준 위치·이름·인덱스를 적용합니다. |
| `work-github-issue` | GitHub 이슈를 실제로 시작하거나 이어서 작업할 때 | 준비 상태와 선행 작업을 확인하고, 세션 전용 임대로 충돌을 막으며, 허가된 로컬 검증·독립 리뷰·PR 병합·안전한 정리까지 완료합니다. |
| `diagnosing-bugs` | 오류, 간헐적 실패, 속도 저하의 원인을 찾을 때 | 재현 방법을 만들고 가능한 원인을 하나씩 반증해 실제 원인을 찾습니다. “진단만” 요청했다면 코드를 고치지 않습니다. |
| `complexity-optimizer` | 비효율적인 반복·재계산·N+1과 알고리즘 hotspot을 찾거나 개선할 때 | scanner와 코드 문맥으로 후보를 순위화하고, 동작을 보존하는 작은 최적화와 검증 방법을 제안하거나 구현합니다. |
| `tdd` | 기능을 만들거나 버그를 테스트부터 고칠 때 | 실패하는 테스트를 먼저 확인하고, 최소 구현과 정리를 작은 단위로 반복합니다. |
| `code-review` | 커밋이나 PR 전 변경 전체를 검토할 때 | 저장소 규칙 준수 여부와 원래 요구사항 충족 여부를 서로 섞지 않고 따로 검토합니다. |
| `writing-great-skills` | Codex 스킬을 새로 만들거나 기존 스킬을 다듬을 때 | 호출 조건, 작업 분기, 완료 기준, 안전 경계를 점검해 스킬이 매번 예측 가능한 절차를 따르게 합니다. |

## 가장 흔한 사용 흐름

```text
새 요청
  → prepare-issue           요청이 실제로 준비됐는지 확인
  → codebase-design?       interface·seam이 미정일 때 추천안을 마련
  → to-spec                합의 내용을 명세로 정리
  → to-tickets             큰 명세를 작은 이슈로 분해
  → work-github-issue      한 세션이 이슈를 안전하게 점유
      → diagnosing-bugs    버그라면 먼저 원인을 확인
      → complexity-optimizer 복잡도·성능 hotspot을 분석하거나 최적화
      → codebase-design?   티켓 범위 안의 module 구조 결정이 필요할 때
      → tdd                테스트부터 구현
      → code-review        규칙과 요구사항을 독립적으로 검토
  → work-github-issue      검증 증거를 남기고 완료 또는 인계
```

모든 작업에 전부 사용할 필요는 없습니다. `codebase-design`은 interface나 seam 선택이 실제로 열려 있을 때만 사용합니다. 계획 단계에서는 `to-spec` 전에 추천안을 만들고, 이슈 구현 중에는 `work-github-issue`가 점유한 범위 안에서 `tdd` 전에 사용합니다. 승인 범위를 넘는 공개 interface나 architecture 변경은 사용자 또는 저장소의 해당 권위가 수락해야 결정이 됩니다. 승인된 티켓이 범위 안의 module-shape 선택을 명시적으로 위임했다면 별도 승인을 반복하지 않습니다. 권고안이 승인된 동작이나 티켓 경계를 바꾸면 구현을 멈추고 계획 단계로 돌아갑니다. 작은 로컬 변경은 `tdd`와 `code-review`만으로 충분할 수 있습니다. 성능 증상의 원인을 모르면 `diagnosing-bugs`부터 사용하고, 코드베이스 전반의 hotspot을 찾거나 이미 확인된 병목을 개선할 때는 `complexity-optimizer`를 사용합니다. GitHub 이슈를 여러 에이전트가 다룬다면 반드시 `work-github-issue`를 바깥 작업 흐름으로 사용합니다.

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
docs/specs/                             제품·개발 명세
docs/decisions/                         아키텍처·제품 결정
docs/research/                          장기 보관할 조사 결과
docs/reports/diagnostics/               요청받은 진단 보고서
docs/reports/reviews/                   요청받은 코드 리뷰 보고서
```

이슈와 연결된 파일은 `issue-42-payment-retry.md`, 연결된 이슈가 없으면 `2026-07-13-payment-retry.md`처럼 이름을 만듭니다. 같은 지식을 GitHub와 Markdown 양쪽에 복사하지 않고, 원본이 아닌 쪽에는 링크만 남깁니다. 프로젝트의 `AGENTS.md`, 문서 인덱스, 기존 ADR 규칙이 있다면 항상 그 규칙이 fallback보다 우선합니다.

## 같은 계정을 쓰는 여러 에이전트가 왜 충돌하지 않나요?

GitHub의 담당자 표시만으로는 부족합니다. 여러 세션이 같은 GitHub 계정으로 보이기 때문입니다.

`work-github-issue`는 이슈 번호와 에이전트 세션을 묶은 별도 임대를 원격 Git에 원자적으로 생성합니다. 먼저 임대한 세션만 파일을 수정할 수 있고, 다른 세션은 현재 소유자를 확인한 뒤 멈춥니다. 이슈 라벨·명세·하위 이슈를 게시하는 짧은 작업도 같은 임대 방식으로 직렬화하므로, 두 세션이 똑같은 계획 이슈를 만드는 것도 막습니다. 임대가 만료되거나 작업을 넘겨받을 때는 기존 브랜치·커밋·테스트·이슈 상태를 먼저 확인합니다.

다른 스킬은 이 임대를 직접 만들거나 해제하지 않습니다. 이 단일 소유권 규칙 덕분에 스킬을 조합해도 충돌 방지 방식이 달라지지 않습니다.

## 설치

Codex에게 다음처럼 요청하면 됩니다.

> `rca32/skills` 저장소에서 `work-github-issue`, `prepare-issue`, `codebase-design`, `to-spec`, `to-tickets`, `documenting-work`, `diagnosing-bugs`, `complexity-optimizer`, `tdd`, `code-review`, `writing-great-skills` 스킬을 설치해 줘.

또는 이미 설치된 `skill-installer`로 `skills/<스킬 이름>` 경로를 선택해 설치할 수 있습니다. 설치가 끝난 뒤 새 세션을 시작하면 스킬 목록이 갱신됩니다.

설치된 `${CODEX_HOME:-$HOME/.codex}/skills`는 사용용 복사본입니다. 스킬을 수정할 때는 이 저장소를 고치고 검증·push한 뒤 다시 설치합니다.

## 처음 사용할 프로젝트의 준비 사항

GitHub 이슈 작업을 시작하기 전에 프로젝트에 다음이 준비되어 있어야 합니다.

- Git, Python 3, GitHub CLI(`gh`)가 설치되어 있어야 합니다.
- `gh auth status`가 작업에 사용할 GitHub 계정으로 로그인됐다고 표시해야 합니다.
- `origin` 같은 임대용 원격 저장소가 `https://github.com/owner/repo.git` 또는 이에 해당하는 정식 SSH 주소를 가리켜야 합니다.
- 그 계정은 이슈를 읽고 수정할 권한과 원격 임대 ref를 push할 권한이 있어야 합니다.
- 프로젝트 문서에 이슈 상태 라벨과 선행 작업 표시 방법이 정의되어 있어야 합니다. 별도 규칙이 없다면 `work-github-issue`의 기본 계약은 `상태: 분류 필요`, `상태: 정보 필요`, `상태: 에이전트 작업 가능`, `상태: 사람 검토 필요`, `상태: 진행하지 않음` 중 하나를 상태로 사용합니다. 기존 영문 라벨은 호환을 위해 읽을 수 있지만 새 이슈에는 한국어 라벨을 사용합니다.
- 구현을 게시하려면 티켓 branch의 base, 현재 worktree 사용 조건, PR target과 integration target, merge 권한과 방식, 필수 검사, 완료로 보는 시점이 프로젝트 문서나 사용자 요청으로 정해져 있어야 합니다. 별도 정리 규칙이 없으면 완료한 세션이 직접 만든 안전한 linked worktree와 local ticket branch만 기본 정리하고, 기존·공유 작업공간, 미완료 작업, remote branch는 보존합니다. 원격 기본 branch만으로 merge 대상이나 remote branch 삭제 권한을 추정하지 않습니다.

소비 저장소가 GitHub Actions 없이 로컬 검증과 독립 리뷰를 통과한 에이전트에게 `main` PR 자동 병합 및 안전한 worktree 정리 권한을 상시 부여하려면, 명시적인 저장소 정책 변경 권한으로 다음 관리형 계약을 설치할 수 있습니다.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  check /absolute/path/to/repository/AGENTS.md \
  --integration-target main --merge-method squash

python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_repository_contract.py" \
  install /absolute/path/to/repository/AGENTS.md \
  --expected-snapshot SNAPSHOT_FROM_CHECK \
  --integration-target main --merge-method squash
```

먼저 `render`로 문구를 보고 기존 지침과의 충돌을 해결한 뒤, `check`가 반환한 opaque `snapshot` 값을 `install`에 전달합니다. 이 token은 렌더된 계약, 저장소 root와 대상 파일의 identity 또는 부재, 내용 hash를 함께 묶으므로 검사 후 템플릿·파일·저장소가 교체되면 쓰기 전에 중단합니다. 이 기능은 Git 저장소 root의 `AGENTS.md`에만 하나의 versioned managed block을 append-only로 추가하며 기존의 다른 내용을 교체하지 않습니다. 다른 내용의 관리 블록, 동시 설치 lock, 중복 marker, 경로의 symlink, 유효하지 않은 Git branch 이름 또는 상위 지침 충돌은 자동으로 덮어쓰지 않습니다. GitHub 저장소 설정의 Actions와 required hosted checks가 비활성화돼 있고, 외부 사람의 PR 승인을 요구하거나 lease 소유 에이전트가 충족할 수 없는 branch rule도 없어야 합니다. 또한 Actions 없이 PR head와 integration base의 stale 상태를 모두 원자적으로 거부할 provider-side 규칙이나 병합 연산이 확인돼야 설치가 완료된 것으로 봅니다.

확신이 없다면 Codex에게 “이 저장소에서 `work-github-issue`를 쓰기 위한 준비 상태를 읽기 전용으로 점검해 줘”라고 요청하면 됩니다. 실제 첫 임대는 인증·원격 주소·원자적 ref push 또는 요청 결과에 필요한 publication 계약이 맞지 않으면 작업을 시작하지 않고 실패하도록 설계되어 있습니다.

`상태: 정보 필요`나 `상태: 사람 검토 필요`인 이슈에는 라벨만 붙이지 않습니다. 이슈 본문 또는 최신 댓글에 요청 종류와 정확한 대상, 사람이 해야 할 일, 답변 위치, 완료 조건, 완료 후 상태와 전환 담당 스킬을 함께 적습니다. `상태: 사람 검토 필요`라면 사람이 작업 후 바로 수정해 남길 수 있는 추천 댓글도 제공합니다. 예를 들어 “검토 필요” 대신 “PR #128의 권한 변경을 검토하고 승인 또는 수정 요청을 PR 리뷰로 남긴 뒤, 권한 있는 `prepare-issue`에 재검증을 요청해 주세요”처럼 작성합니다.

선택된 tracker 계약의 라벨이 저장소에 아직 없다면 `to-spec`, `prepare-issue`, `to-tickets`는 임의로 새 라벨을 만들지 않습니다. 별도 계약이 없을 때는 기본 한국어 라벨의 정확한 이름과 의미를 보고하고, 저장소 라벨 생성까지 별도로 허가받은 경우에만 설정한 뒤 이슈 게시를 계속합니다.

## 사용 예시

```text
$prepare-issue 이슈 #42가 에이전트가 작업할 만큼 구체적인지 확인해 줘.
$codebase-design 이 결제 흐름의 module interface와 seam 대안을 비교하고 하나를 추천해 줘.
$to-spec 지금까지 합의한 결제 재시도 정책을 명세로 정리해 줘.
$to-tickets 승인된 이슈 #50을 한국어로 이해하기 쉬운 작은 이슈로 나누고 게시해 줘.
$documenting-work 이 설계 문서의 원본 위치와 표준 파일명을 정해 줘.
$work-github-issue 현재 시작할 수 있는 이슈 하나를 안전하게 맡아서 완료해 줘.
$diagnosing-bugs 간헐적인 타임아웃의 원인만 진단해 줘. 아직 수정하지 마.
$complexity-optimizer 이 코드베이스의 복잡도와 성능 hotspot을 분석하고 전체 보고서를 작성해 줘.
$tdd 이 변경을 공개 인터페이스 테스트부터 구현해 줘.
$code-review 커밋 전 현재 작업 전체를 규칙과 명세 기준으로 검토해 줘.
$writing-great-skills 이 스킬의 호출 조건과 완료 기준을 더 예측 가능하게 고쳐 줘.
```

`prepare-issue`, `to-spec`, `to-tickets`는 의도하지 않은 이슈 변경을 피하기 위해 이름을 직접 불러 사용하는 방식입니다. 또한 “검토해 줘”, “초안을 만들어 줘”는 외부 게시 권한을 뜻하지 않습니다. 이슈 생성·라벨 변경·게시까지 원한다면 요청에 분명히 포함해야 합니다.

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
python3 skills/documenting-work/scripts/test_resolve_document_path.py -v
python3 skills/complexity-optimizer/scripts/test_analyze_complexity.py -v
python3 skills/complexity-optimizer/scripts/analyze_complexity.py . --format json
bash -n skills/diagnosing-bugs/scripts/hitl-loop.template.sh
```

에이전트용 상세 작성·검증·배포 계약은 [AGENTS.md](AGENTS.md)에 있습니다.
