# 한국어 스킬 안내서

이 문서는 이 저장소의 Codex 스킬을 처음 접하는 사람도 쉽게 고를 수 있도록 설명한 안내서입니다.

스킬은 Codex에게 특정 업무의 순서, 확인할 증거, 허용된 변경, 완료 조건을 알려 주는 업무 매뉴얼입니다. 아래 문서는 그 계약을 쉬운 한국어로 풀어 쓴 설명이며, 에이전트가 실제로 따르는 정확한 규칙의 원본은 각 `skills/<이름>/SKILL.md`입니다.

## 어떤 스킬부터 보면 되나요?

| 하고 싶은 일 | 사용할 스킬 | 쉬운 설명 |
| --- | --- | --- |
| 마지막 답변을 쉽게 다시 표현 | `bro` | [마지막 메시지를 쉽게 다시 말하기](skills/bro.md) |
| 새 이슈를 분류하고 작업 가능한 상태인지 확인 | `prepare-issue` | [개발 이슈 준비하기](skills/prepare-issue.md) |
| 중요한 결정의 문제 정의와 상속된 전제를 재검토 | `first-principles` | [근본 사실에서 결정을 다시 세우기](skills/first-principles.md) |
| 도메인 용어·불변식·상태·경계를 능동적으로 다듬기 | `domain-modeling` | [edge case로 도메인 모델 다듬기](skills/domain-modeling.md) |
| module interface나 seam을 설계 | `codebase-design` | [깊은 module interface 설계하기](skills/codebase-design.md) |
| 한 번에 명세로 만들기 어려운 큰 일의 결정을 순차 정리 | `decision-map` | [큰 일의 결정 경로 밝히기](skills/decision-map.md) |
| 합의 내용을 개발 명세와 별도 쉬운 설명으로 정리 | `to-spec` | [대화를 명세로 바꾸기](skills/to-spec.md) |
| 큰 명세를 작은 구현 이슈로 분해 | `to-tickets` | [명세를 티켓으로 나누기](skills/to-tickets.md) |
| GitHub 없이 명세를 로컬 item으로 나누고 순차 구현 | `local-work` | [GitHub 없이 명세를 순차 구현하기](skills/local-work.md) |
| 문서의 원본 위치와 수명 결정 | `documenting-work` | [개발 문서의 자리 정하기](skills/documenting-work.md) |
| GitHub 이슈를 충돌 없이 구현 | `work-github-issue` | [GitHub 이슈를 안전하게 맡아 처리하기](skills/work-github-issue.md) |
| 원인을 모르는 오류나 성능 저하 조사 | `diagnosing-bugs` | [증거로 버그 원인 찾기](skills/diagnosing-bugs.md) |
| 복잡도·성능 hotspot 분석 또는 안전한 최적화 | `complexity-optimizer` | [복잡도와 성능 hotspot 개선하기](skills/complexity-optimizer.md) |
| 테스트를 먼저 작성해 기능 또는 수정 구현 | `tdd` | [작은 Red-Green-Refactor 반복](skills/tdd.md) |
| 실제 산출물을 비교 기준까지 반복 개선 | `quality-gauntlet` | [독립 평가로 품질 수렴시키기](skills/quality-gauntlet.md) |
| 변경 사항이 규칙과 요구사항을 만족하는지 검토 | `code-review` | [두 기준을 분리한 코드 리뷰](skills/code-review.md) |
| 새 스킬을 만들거나 기존 스킬 개선 | `writing-great-skills` | [예측 가능한 스킬 작성하기](skills/writing-great-skills.md) |

## 대표적인 조합

큰 기능은 불확실성과 협업 방식에 따라 다음 두 경로로 이어집니다.

```text
큰 불확실성 → decision-map? → domain-modeling?/codebase-design? → to-spec
                                                              ├─ local-work → tdd → code-review
                                                              └─ to-tickets → work-github-issue
```

- `first-principles`는 사용자가 이름을 직접 불렀을 때만 중요한 결정의 문제 framing, 관측 사실, 고정 제약과 상속된 가정을 다시 정리합니다. 이슈 intake, 설계, 진단과 구현은 해당 전문 스킬에 넘깁니다.
- `prepare-issue`는 요청이 실제로 작업할 준비가 됐는지 확인합니다.
- `domain-modeling`은 설계가 도메인 용어, 불변식, 관계, 상태나 경계를 실제로 바꾸거나 모호함을 해소해야 할 때 예시와 반례로 모델을 검증합니다. 기존 `domain.md`의 어휘를 읽는 것만으로는 실행하지 않습니다.
- `codebase-design`은 interface나 seam 선택이 열려 있을 때 구현 전에 설계안을 비교하고 하나를 추천합니다. 승인 범위를 넘는 공개 계약 변경은 사용자나 저장소 권위가 수락한 뒤에만 구현하고, 티켓이 범위 안의 설계 재량을 명시적으로 위임했다면 그 안에서는 바로 이어갑니다.
- `decision-map`은 지금 질문할 수 있는 결정만 작은 로컬 문서로 만들고 하나씩 해결합니다. 열린 결정과 fog가 사라지면 `to-spec`으로 넘깁니다.
- `to-spec`은 합의된 범위를 작은 개발 명세로 고정하고 별도의 쉬운 설명을 생성합니다. 후속 workflow는 가능하면 설명의 제한된 metadata만 확인하며, 설명 본문을 구현 권위로 소비하지 않습니다.
- `to-tickets`는 새 계획 결정 없이 분해 가능한지 먼저 확인합니다. 가능하면 의존성이 분명한 작은 작업으로 나누고, 불가능하면 티켓을 만들지 않은 채 적절한 설계·명세 workflow로 돌려보냅니다.
- `local-work`는 한 에이전트가 순서대로 처리하는 경우 repository spec을 로컬 item으로 나누고 현재 worktree에서 구현합니다. GitHub issue, lease, item별 branch와 commit은 만들지 않습니다.
- `work-github-issue`는 한 세션만 이슈를 맡도록 조정하고 완료나 인계까지 책임집니다.
- 원인을 모르면 `diagnosing-bugs`, 복잡도·성능 hotspot을 찾거나 개선하면 `complexity-optimizer`, 도메인 의미를 바꿔야 하는 모호함이 드러나면 `domain-modeling`, module 구조 선택이 남아 있으면 `codebase-design`, 구현할 행동과 seam이 정해졌으면 `tdd`, 명시된 비교 품질 기준까지 반복 개선해야 하면 `quality-gauntlet`, 구현이 끝났으면 `code-review`를 안쪽 과정으로 사용합니다.

모든 작업에 이 전체 흐름이 필요한 것은 아닙니다. `first-principles`는 상속된 framing이나 관행을 실제로 재검토해야 할 때만 명시적으로 호출합니다. 작은 로컬 변경이라면 `tdd`와 `code-review`만으로 충분할 수 있습니다. `quality-gauntlet`은 사용자가 이름을 직접 불러 고비용 반복을 요청했을 때만 실행합니다.

## 실행 가이드

- [`to-tickets` 티켓 그래프를 Goal로 끝까지 구현하기](workflows/complete-ticket-graph-with-goal.md): PR 생성에서 멈추지 않고, 허가된 merge·이슈 완료·lease 해제·안전한 worktree 정리까지 반복하는 kickoff 프롬프트

## 꼭 알아둘 권한 원칙

“살펴봐”, “설명해 줘”, “초안을 만들어 줘”는 읽기와 초안 작성만 허용합니다. 다음 행동은 별도로 분명하게 요청해야 합니다.

- GitHub 이슈 생성이나 수정
- 라벨, 댓글, 상태 또는 의존 관계 변경
- 코드 수정, 커밋, push 또는 PR 게시
- 기존 문서나 성공한 외부 작업 삭제

여러 에이전트 세션이 같은 GitHub 계정을 사용할 수 있는 작업에서는 `work-github-issue`의 lease가 실제 작업 세션을 구분합니다. 담당자 표시만으로는 어느 세션이 작업 중인지 구분할 수 없기 때문입니다.
