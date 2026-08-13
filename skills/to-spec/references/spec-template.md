# Authoritative spec template

Write a compact development contract, not an onboarding narrative. Use the language requested by the repository or user; otherwise use Korean. Preserve quoted source text, identifiers, API names, links, and protocol markers exactly.

```markdown
<!-- work-github-issue:state role=<needs-triage|ready-for-human> -->

# <결과 중심 제목>

## 권위와 상태

- 상태: 초안 | 승인됨 | 미해결 질문으로 차단됨
- 원본: <대화, 상위 이슈 또는 결정>
- 적용 결정: <도메인·아키텍처 결정 ID 또는 링크>

## 문제와 결과

- EVID-001: <문제가 실제로 존재한다는 관찰 또는 권위 있는 근거>
- OUT-001: <구현 방법을 정하지 않은 관찰 가능한 성공 상태>

## 동작 계약

- REQ-001: <정상 동작과 적용 조건>
- REQ-002: <실패·복구·권한·호환성 경계>
- REQ-003: <이미 승인된 데이터 또는 공개 인터페이스 계약>

## 시나리오

- SCN-001 [REQ-001]: Given <상태>, when <행동>, then <관찰 결과>.
- SCN-002 [REQ-002]: Given <경계 또는 실패 상태>, when <행동>, then <안전한 결과>.

## 구현 제약

- CON-001: <승인된 아키텍처, 소유권 또는 호환성 제약> — 근거: <authority>

## 검증 계약

- 검증 seam: <가장 높은 기존 공개 지점과 충분한 이유>
- AC-001 [REQ-001, SCN-001]: <관찰 가능한 완료 조건>
- AC-002 [REQ-002, SCN-002]: <관찰 가능한 실패·호환성 조건>
- 증거: <필요한 테스트, 명령 또는 artifact 종류>

## 범위 밖

- OUT-OF-SCOPE-001: <명시적으로 제외한 인접 작업>

## 가정

- ASM-001: <근거가 있으며 틀릴 경우 영향이 명시된 가정>

## 미해결 질문

- Q-001: <질문> — 영향: <답이 없을 때 차단되는 요구사항 또는 분해>

## 사람에게 필요한 도움

<!-- tracker 상태가 `상태: 정보 필요` 또는 `상태: 사람 검토 필요`일 때만 포함합니다. -->

**필요한 이유:** <에이전트가 안전하게 계속할 수 없는 이유>

**요청 종류:** <질문 | 결정 | 승인 | 권한 부여 | 병합 | 수동 작업 | 검토>

**대상:** <질문할 항목, 명세, 결정 또는 시스템>

### 해 주실 일

- [ ] <위 대상을 직접 이름 붙인 행동 하나>

**답변/결과를 남길 곳:** <이슈 댓글, PR 리뷰 또는 지정 시스템>

**추천 댓글:** <정확한 대상> — 결과: [승인 | 수정 요청]. 판단 근거: [작성]. 완료 증거: [링크 붙여넣기].

**완료 조건:** <관찰 가능한 완료 상태>

**완료 증거:** <댓글 URL, 결정 링크, 리뷰 링크 또는 기록 ID>

**완료 후 상태:** <승인 댓글을 남기고 `상태: 사람 검토 필요`를 유지한 채 `$to-tickets` 게시 요청>

**전환 담당:** prepare-issue
```

Omit empty scenario categories and sections that have no semantic content, except material unknowns. Keep each meaning once and cross-reference its ID. A long list is not traceability.

Include `사람에게 필요한 도움` only when the selected persistence and tracker state require it. A fallback tracker planning issue in `상태: 사람 검토 필요` must fill every field, including the copy-ready recommended comment.
