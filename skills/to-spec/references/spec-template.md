# Spec template

Write the spec in the language requested by the repository or user. When
neither specifies one, use Korean. Preserve quoted source text, code
identifiers, API names, links, and protocol markers exactly.

```markdown
# <결과 중심 제목>

## 상태와 근거

- 상태: 초안 | 승인됨 | 미해결 질문으로 차단됨
- 원본 대화 또는 상위 이슈:
- 관련 도메인 또는 아키텍처 결정:

## 문제

<사용자 또는 운영자가 겪는 문제와 실제로 존재한다는 증거>

## 원하는 결과

<내부 구현 방법을 정하지 않고 성공한 상태를 설명>

## 사용자와 시나리오

1. <구체적인 사용자>는 <동작>을 원한다. 그러면 <얻는 효과>가 있다.

<관련 있는 정상·실패·복구·권한·호환성 시나리오만 포함>

## 동작 요구사항

- <필수 동작과 경계 조건>
- <오류·안전·호환성 동작>
- <이미 결정된 데이터 또는 인터페이스 계약>

## 구현 결정

- <승인된 아키텍처 또는 소유권 결정>
- <구현이 지켜야 하는 제약>

## 테스트 결정

- 가장 높은 공개 검증 지점:
- 기존 테스트 선례:
- 필요한 실패·회귀 검증:

## 완료 조건

- [ ] <관찰 가능한 제품 또는 시스템 결과>
- [ ] <관찰 가능한 실패 또는 호환성 결과>
- [ ] <필요한 검증 증거>

## 범위 밖

- <명시적으로 제외한 인접 작업>

## 가정

- <진행할 수 있을 만큼 근거가 있는 가정>

## 미해결 질문

- <미해결 질문 — 답이 없을 때의 영향>

## 사람에게 필요한 도움

<!-- tracker 상태가 `상태: 정보 필요` 또는 `상태: 사람 검토 필요`일 때만 포함합니다. -->

**필요한 이유:** <에이전트가 안전하게 계속할 수 없는 이유>

**요청 종류:** <질문 | 결정 | 승인 | 권한 부여 | 병합 | 수동 작업 | 검토>

**대상:** <질문할 항목, 명세, 결정 또는 시스템을 정확히 식별>

### 해 주실 일

- [ ] <위 대상을 직접 이름 붙인 구체적인 행동 하나>

**답변/결과를 남길 곳:** <이슈 댓글, 연결된 PR 리뷰 또는 지정 시스템>

**완료 조건:** <요청한 판단이나 작업이 끝났다고 볼 수 있는 관찰 가능한 조건>

**완료 증거:** <이슈 댓글 URL, 결정 링크, 리뷰 링크 또는 기록 ID>

**완료 후 상태:** <승인 댓글을 남기고 `상태: 사람 검토 필요`를 유지한 채 `$to-tickets` 게시 요청>

**전환 담당:** triage
```

Omit empty scenario categories, but never omit material unknowns. A long list is not a substitute for traceability or observable criteria.

Omit `## 사람에게 필요한 도움` only when the selected persistence and state
require no human action. A tracker-published fallback planning issue in `상태:
사람 검토 필요` must fill it.
