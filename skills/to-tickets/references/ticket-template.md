# Ticket template

Write the title and body in the language requested by the repository or user.
When neither specifies one, use Korean. Preserve code identifiers, API names,
links, and protocol markers exactly. Use this shell and plain terms that a
non-specialist can act on.

```markdown
<!-- to-tickets:v1 source=<parent identifier> revision=<source fingerprint> key=<draft key> -->

## 상위 항목

<계획 이슈 또는 승인된 명세 링크>

## 완료되면 달라지는 점

<사용자 또는 운영자 관점에서 이 티켓 하나로 가능해지는 결과>

## 완료 조건

- [ ] <직접 확인할 수 있는 동작>
- [ ] <필요한 실패·안전·호환성 동작>
- [ ] <통과해야 하는 검증>

## 먼저 끝나야 하는 작업

- <초안 키 또는 이슈 번호>, 없으면 `없음`

## 이번 작업에 포함하지 않는 것

- <의도적으로 제외한 인접 작업>

## 요구사항 근거

- <승인된 원본의 요구사항 또는 완료 조건>

## 사람에게 필요한 도움

<!-- `상태: 정보 필요` 또는 `상태: 사람 검토 필요`일 때만 포함합니다. -->

**필요한 이유:** <에이전트가 안전하게 계속할 수 없는 이유>

**요청 종류:** <질문 | 결정 | 승인 | 권한 부여 | 병합 | 수동 작업 | 검토>

**대상:** <질문할 항목, PR, 계정, 권한 또는 시스템을 정확히 식별>

### 해 주실 일

- [ ] <위 대상을 직접 이름 붙인 구체적인 행동 하나>

**답변/결과를 남길 곳:** <이슈 댓글, 연결된 PR 리뷰 또는 지정 시스템>

**완료 조건:** <요청한 판단이나 작업이 끝났다고 볼 수 있는 관찰 가능한 조건>

**완료 증거:** <이슈 댓글 URL, PR 리뷰 링크, 로그·감사 이벤트 ID 또는 스크린샷 링크>

**완료 후 상태:** <authorized prepare-issue 재검증 후 상태: 에이전트 작업 가능 | 상태: 정보 필요 유지 | 완료 증거와 함께 종료>

**전환 담당:** <prepare-issue | work-github-issue>
```

Ticket titles should describe the delivered outcome, not a layer or activity. Avoid implementation file paths and line numbers. Include a short interface or state-machine shape only when the approved source made it part of the contract.

Omit `## 사람에게 필요한 도움` only when no human action is required. When
the selected tracker contract defines its own labels or human-action fields, use
that contract instead of this fallback wording.

Read `Blocked by` as the legacy alias of `먼저 끝나야 하는 작업` on existing
issues. If both sections exist and disagree, stop on a dependency conflict;
publish only the Korean section under the fallback contract.
