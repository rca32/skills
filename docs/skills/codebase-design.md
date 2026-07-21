# `codebase-design`: 깊은 module interface 설계하기

정확한 실행 계약: [`skills/codebase-design/SKILL.md`](../../skills/codebase-design/SKILL.md)

## 한마디로

여러 호출자가 복잡한 내부 동작을 적은 지식으로 사용할 수 있도록 **작은 interface 뒤에 행동을 모으고 적절한 seam을 선택하는 읽기 전용 설계 스킬**입니다.

`codebase-design`은 코드를 직접 고치지 않습니다. 현재 호출자, 테스트, dependency와 architecture 결정을 읽고 설계안을 추천한 뒤, 명세화는 `to-spec`, 구현은 `tdd`, 이슈 생명주기는 `work-github-issue`에 넘깁니다. 승인 범위를 넘는 공개 interface나 architecture 변경은 사용자 또는 저장소의 해당 권위가 수락하기 전까지 결정으로 취급하지 않습니다. 반대로 승인된 티켓이나 실행 계약이 범위 안의 module-shape 선택을 명시적으로 위임했다면 그 한계 안에서는 별도 승인을 다시 요구하지 않습니다.

## 언제 사용하나요?

- 여러 shallow module에 흩어진 정책을 하나의 deep module로 모을 때
- 공개 interface의 method, parameter, invariant와 error mode를 정할 때
- 어느 위치에 seam을 두어야 할지 결정할 때
- 서로 다른 interface 대안을 비교할 때
- 확정되지 않은 module 구조를 `to-spec`이나 `tdd` 전에 결정할 때

일반 기능 구현, 원인 미상의 버그 진단, 성능 hotspot 탐색, 완료된 변경 리뷰에는 사용하지 않습니다.

## 무엇을 비교하나요?

- **Depth:** 호출자가 배워야 하는 interface에 비해 얼마나 많은 행동을 얻는지
- **Locality:** 정책, 변경, 버그와 검증이 한 module 안에 모이는지
- **Seam placement:** 실제로 행동이 달라지는 위치에 seam이 있는지
- **Testability:** 호출자와 테스트가 같은 interface로 행동을 관찰할 수 있는지
- **Compatibility:** 기존 계약과 호출자를 안전하게 옮길 수 있는지

Dependency가 in-process인지, local stand-in으로 대체할 수 있는지, 소유한 remote service인지, true external system인지에 따라서도 adapter와 테스트 전략을 다르게 정합니다.

## workflow에서는 어디에 들어가나요?

계획 단계에서는 `triage` 뒤, `to-spec` 앞에 조건부로 사용합니다. 설계 결정을 먼저 끝내고 `to-spec`이 그 결정을 명세로 고정하게 합니다.

GitHub 이슈 구현 중에는 `work-github-issue`가 implementation lease를 잡았다고 확인한 뒤, `tdd`의 첫 Red 전에 사용합니다. `codebase-design`이 직접 lease를 만들지는 않습니다. 추천안이 승인된 동작, architecture, 티켓 경계나 dependency를 바꾼다면 코드를 고치지 않고 계획 단계로 돌아갑니다.

## 결과로 무엇을 주나요?

- 선택한 module과 seam
- invariant, ordering, error, configuration, 성능 특성을 포함한 전체 interface
- interface 뒤에 숨길 행동
- dependency와 adapter 전략
- 호출자와 테스트 사용 예시
- 비교한 대안과 결정적인 trade-off
- migration과 남은 위험
- 기존 권위로 고정됨, 승인 범위 안에서 위임됨, 명시적으로 수락됨, 또는 수락 대기 중이라는 상태
- 다음 담당 workflow

## 요청 예시

```text
$codebase-design 결제 재시도 로직이 여러 helper에 흩어져 있어. deep module 후보와 interface 대안을 비교하고 하나를 추천해 줘. 아직 코드는 수정하지 마.
```
