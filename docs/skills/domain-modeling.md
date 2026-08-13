# `domain-modeling`: edge case로 도메인 모델 다듬기

정확한 실행 계약: [`skills/domain-modeling/SKILL.md`](../../skills/domain-modeling/SKILL.md)

## 한마디로

설계 중 프로젝트의 용어, 불변식, 관계, 상태와 경계를 **예시·반례·edge case로 적극 검증하고 더 정확하게 만드는 스킬**입니다.

프로젝트가 정한 권위 있는 도메인 문서나 glossary를 읽어 이미 정해진 어휘를 사용하는 것은 모든 관련 스킬의 기본 습관입니다. 그 읽기만으로 `domain-modeling`을 실행하지는 않습니다. 서로 다른 의미가 한 용어에 섞였거나, 경계 사례 때문에 현재 모델을 바꿔야 할 때 사용합니다. 별도 문서 관례가 없는 프로젝트에서만 `docs/domain.md`를 fallback으로 사용합니다.

## 어떻게 모델을 검증하나요?

- 대표 예시와 거의 비슷하지만 해당하지 않는 반례를 비교
- 빈 상태, 경계값과 불가능한 조합 확인
- identity, ownership과 lifecycle 질문
- 순서 변경, 중복, retry, 취소와 늦게 도착한 event 확인
- actor, 권한, tenant, 시간이나 context가 바뀌는 경우 확인
- 제안한 invariant를 깨는 counterexample 탐색

가상 시나리오는 모델의 모호함을 드러내는 도구일 뿐입니다. 제품 요구사항이나 수락된 행동으로 자동 승격하지 않고, 관측된 사례인지, 기존 권위가 요구하는 사례인지, 검증용 가설인지 표시합니다.

## 무엇을 남기나요?

- 선호 용어와 정확한 뜻, alias, 피해야 할 오해
- 대표 예시와 non-example
- identity와 lifecycle, 유효한 상태 전환
- 관계, cardinality, ownership과 invariant
- 의미가 적용되는 context와 다른 context의 번역 경계
- 결정 근거, 거부한 대안과 상태

각 변경은 `established`, `proposed`, `unresolved` 중 하나로 구분합니다. 저장소 규칙이나 권한 있는 결정자가 확정한 내용만 `established`로 표시합니다.

## 문서에는 언제 쓰나요?

“검토해 줘”, “논의해 줘”, “초안을 만들어 줘”라는 요청에는 대화 안에서 제안만 반환하고 파일을 만들지 않습니다. 저장이 명시적으로 허가되면 `documenting-work`가 기존 프로젝트 관례를 먼저 찾습니다. 별도 관례가 없을 때만 `docs/domain.md`와 안정적인 ID `domain:project`를 사용해 기존 문서를 제자리에서 갱신합니다.

## 하지 않는 일

- edge case를 새 제품 요구사항으로 발명
- module interface나 architecture seam 설계
- 문서 위치·ID·인덱스·수명주기 결정
- 코드 구현, tracker 변경, lease 관리, commit, push 또는 게시

## 요청 예시

```text
$domain-modeling 주문, 결제 승인, 환불 완료의 의미와 상태 경계를 예시와 edge case로 검증해 줘. 아직 파일은 수정하지 마.
```
