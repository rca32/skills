# `local-work`: GitHub 없이 명세를 순차 구현하기

정확한 실행 계약: [`skills/local-work/SKILL.md`](../../skills/local-work/SKILL.md)

## 한마디로

한 에이전트가 순서대로 처리하는 프로젝트에서 `to-tickets → work-github-issue`의 원격 조정 비용을 생략합니다. 저장소 명세를 작은 로컬 work item으로 나누고 현재 worktree에서 하나씩 구현·검증합니다.

```text
docs/local-work/<spec-name>/
├── work.md
└── items/
    ├── W001-*.md
    └── W002-*.md
```

승인된 명세가 제품 동작의 유일한 원본입니다. Draft이거나 중요한 미해결 질문이 item 경계·seam·인수 조건을 막는 명세에서는 계획과 구현을 시작하지 않습니다. `work.md`와 item은 `normative: false`이며, 원본 spec ID와 정확한 fingerprint에 묶여 실행 순서·수정 범위·진행 상태·짧은 검증 증거만 관리합니다.

## 두 가지 사용 방식

- 계획만 요청: work set과 source traceability를 만들고 코드는 수정하지 않음
- 구현·계속·완료 요청: 첫 준비 item부터 순서대로 TDD, 검증, 상태 갱신 수행

한 item을 실행할 때 모든 item 본문을 읽지 않습니다. 현재 item, 그 item이 참조하는 `REQ-*`와 `AC-*`, 관련 코드와 테스트만 읽어 context를 작게 유지합니다.

명세 fingerprint가 달라지면 work set을 `stale`로 표시하고 구현을 멈춥니다. 새 요구사항이나 공개 interface·architecture 결정이 필요해도 추측하지 않고 `decision-map`, `to-spec`, `domain-modeling`, `codebase-design`으로 돌려보냅니다.

모든 item이 끝나면 전체 검증과 분리된 Standards/Spec 코드 리뷰를 수행합니다. 격리 reviewer를 우선 사용하되 불가능하면 두 축을 한 context에서 순차 검토하고 그 fallback을 명시합니다. 구현 candidate는 코드·테스트·제품 문서 diff이며 비규범 work-set과 index projection은 제외합니다. 따라서 `work.md`에는 구현 candidate identity, 제외 경로, 명령 결과, review mode와 provenance, finding 수를 기록하고 자체 fingerprint 대신 schema·readback checkpoint를 사용합니다. item마다 branch·worktree·commit을 만들지 않으며, 마지막 commit·push도 사용자가 별도로 요청할 때 한 번만 수행합니다.

## GitHub workflow와 선택 기준

| `local-work` | `to-tickets → work-github-issue` |
| --- | --- |
| 한 에이전트 또는 순차 세션 | 여러 작업자와 공유 tracker |
| 로컬 문서와 현재 worktree | GitHub issue, dependency, lease |
| 낮은 조정 비용 | 원격 가시성과 충돌 방지 |
| 마지막에 한 번 게시 | 티켓별 증거와 lifecycle |

동시 작업, 원격 인계, issue별 감사 증거가 필요하면 `local-work`를 사용하지 않습니다.
이미 GitHub issue에 연결된 구현이라면 작업자가 한 명이어도 `work-github-issue` lifecycle을 유지하며, 같은 작업에 두 실행 상태를 만들지 않습니다.

## 요청 예시

```text
$local-work docs/specs/payment-retry.md를 로컬 work item으로 나누고 순서대로 구현해 줘.
```
