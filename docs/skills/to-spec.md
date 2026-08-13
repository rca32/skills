# `to-spec`: 대화를 명세로 바꾸기

정확한 실행 계약: [`skills/to-spec/SKILL.md`](../../skills/to-spec/SKILL.md)

## 한마디로

현재 대화와 저장소에서 **이미 합의된 결정**을 두 개의 분리된 결과로 만듭니다.

1. 구현·티켓·테스트·리뷰의 기준이 되는 작고 정확한 authoritative spec
2. 그 명세를 사람이 빨리 이해하도록 풀어 쓴 짧은 non-normative explainer

빈칸을 그럴듯한 요구사항으로 채우지 않습니다. 결정되지 않은 내용은 명세의 가정이나 열린 질문으로 남깁니다.

큰 작업의 결정 경로 자체가 아직 보이지 않으면 먼저 `decision-map`으로 질문을 하나씩 확정합니다. 결정 지도가 `ready-for-spec`이 된 뒤 그 결정 문서들을 입력으로 사용합니다.

## 개발 명세는 어떻게 쓰나요?

명세는 사람에게 배경을 반복 설명하는 글보다 에이전트가 정확히 분해하고 검증할 수 있는 계약에 가깝게 작성합니다.

- `REQ-*`로 식별되는 동작과 경계 조건
- 정상·실패·복구·권한·호환성 시나리오
- 이미 승인된 구현 제약과 그 권위
- 가장 높은 공개 검증 seam
- 요구사항으로 추적되는 `AC-*` 완료 조건
- 범위 밖, 가정과 미해결 질문

같은 의미를 여러 절에서 반복하지 않고 안정적인 ID로 연결합니다. 설명문서가 없어도 개발 명세만으로 구현과 검증을 진행할 수 있어야 합니다.

## 쉬운 설명은 어떻게 만드나요?

개발 명세를 완성하고 감사한 뒤 정확한 본문 fingerprint를 계산합니다. 그 고정된 revision만 사용해 별도의 쉬운 설명을 만듭니다.

- 왜 필요한가
- 무엇이 달라지는가
- 최대 7단계의 짧은 동작 순서
- 중요한 범위 밖
- 사람이 알아야 하는 미해결 질문

설명은 `bro`처럼 쉬운 말과 짧은 문장을 사용하지만 `$bro`를 직접 호출하지는 않습니다. 원본 의미를 보존하고 새로운 사실, 요구사항, 조언, 결정이나 해석을 추가하지 않습니다.

설명문서는 반드시 `kind: "spec-explainer"`, `normative: false`, `derived_from`, `source_fingerprint`를 가집니다. `to-tickets`, `tdd`, `code-review`는 이 문서를 개발 기준으로 사용할 수 없습니다.

## 어디에 저장하나요?

초안만 요청하면 두 결과에 서로 다른 대화 artifact ID를 부여하고 파일을 만들지 않습니다. 실행 환경이 독립 artifact를 지원하지 않으면 정확한 UTF-8 byte 길이가 적힌 envelope로 각각 감쌉니다. 개발 인계에는 완전한 spec envelope만 전달하며, 다음 세션에서 해소할 durable locator가 없으면 response-scoped ID만 넘길 수 없습니다. 저장소 명세 저장이 요청되고 별도 프로젝트 관례가 없으면 다음 위치를 사용합니다.

```text
docs/specs/<name>.md             개발용 authoritative spec
docs/spec-explainers/<name>.md  사람용 non-normative explainer
```

원본 spec을 먼저 저장하고 다시 읽은 본문으로 fingerprint를 계산한 뒤 explainer를 생성합니다. 원본이 바뀌면 explainer 전체를 다시 생성합니다. fingerprint가 맞지 않는 explainer는 오래된 설명이며 독립적으로 고칠 수 없습니다.

Tracker가 명세 원본일 때는 구현 workflow가 이슈 본문을 로드하므로 explainer를 이슈 본문이나 댓글에 복사하지 않습니다. 기본적으로 대화로 반환하고, 별도 저장소 쓰기 권한이 있을 때만 repository 문서로 저장합니다.

## 게시와 권한

게시된 명세는 구현 티켓이 아니라 계획 원본입니다. 저장소 명세는 순차·저비용 구현이면 `$local-work`, GitHub 공유 추적과 claim이 필요하면 `$to-tickets`로 이어집니다. Tracker 명세는 곧바로 `상태: 에이전트 작업 가능`을 붙이지 않으며 필요한 승인·질문·완료 증거를 기록합니다.

저장소 파일은 두 목적지의 fingerprint와 dirty-worktree 상태를 확인한 뒤 수정합니다. Tracker 게시에는 별도 권한과 planning lease가 필요합니다. Spec 저장은 성공했지만 explainer 결과가 불명확하면 spec을 되돌리지 않고 `explainer-pending`으로 보고한 뒤 explainer identity를 먼저 재확인합니다.

## 하지 않는 일

- 확인되지 않은 요구사항 발명
- explainer를 두 번째 개발 authority로 사용
- explainer 본문을 구현 workflow의 요구사항 context로 사용
- 명세를 구현 티켓으로 위장
- Tracker와 Markdown에 authoritative spec 본문을 중복 저장
- 구현 이슈 claim

## 요청 예시

```text
$to-spec 지금까지 합의한 결제 재시도 정책을 개발 명세와 별도의 쉬운 설명으로 정리해 줘.
```
