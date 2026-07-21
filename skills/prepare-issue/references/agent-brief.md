# Agent brief contract

An agent brief is the durable behavioral contract attached before an issue or pull request becomes implementation-ready. Prefer interfaces and behavior over file paths and line numbers that can go stale.

Write the brief in the language selected by the tracker contract. The bundled
fallback uses Korean headings and plain language:

```markdown
## 에이전트 작업 설명

**유형:** 버그 | 개선
**한 줄 결과:** <완료되면 달라지는 점>

### 현재 동작

<지금 일어나는 일과 확인된 문제 또는 기능 차이>

### 원하는 동작

<변경 후 동작, 경계 조건과 실패 동작 포함>

### 지켜야 할 계약

- <공개 인터페이스 또는 도메인 개념 — 필요한 동작 변화>
- <데이터 또는 설정 형태 — 호환성 기대사항>

### 완료 조건

- [ ] <직접 확인할 수 있는 조건>
- [ ] <회귀 또는 호환성 조건>
- [ ] <필수 검증 통과>

### 먼저 해결할 일

- <tracker 의존 관계>, 없으면 `없음`

### 이번 작업에 포함하지 않는 것

- <바꾸지 않을 인접 동작>

### 확인한 증거

- <재현·조사·명령과 결과>

## 사람에게 필요한 도움

<!-- `상태: 정보 필요` 또는 `상태: 사람 검토 필요`일 때만 포함합니다. -->

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

For a pull request, describe the current state of the diff and the remaining gaps. Do not rewrite the request as if no code exists.

A brief is incomplete when it relies on phrases such as “works correctly,” gives only implementation steps, omits negative or compatibility behavior, or cannot be verified without guessing the intended result.

Omit `## 사람에게 필요한 도움` when no human action is required. For a human-wait state, a brief is also incomplete when it says only “review this” or “provide more information” without naming the exact action, response location, completion evidence, and next state. For `상태: 사람 검토 필요`, the brief is incomplete without a copy-ready suggested comment that repeats the exact target and provides bracketed `결과`, `판단 근거`, and `완료 증거` slots; omit that field for `상태: 정보 필요` when it adds no value.
