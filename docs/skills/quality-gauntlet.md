# `quality-gauntlet`: 독립 평가로 품질 수렴시키기

정확한 실행 계약: [`skills/quality-gauntlet/SKILL.md`](../../skills/quality-gauntlet/SKILL.md)

## 한마디로

이미 수정 권한이 있는 코드, UI, 글, 연구 결과 같은 실제 산출물을 레퍼런스·benchmark·rubric과 반복 비교해 품질 격차를 줄이는 명시 호출형 스킬입니다.

작업자가 자기 결과를 평가하지 않습니다. builder가 한 부분을 개선하면 별도의 깨끗한 context를 가진 read-only critic이 실제 산출물을 검사하고 가장 큰 의미 있는 격차 하나를 돌려줍니다.

## 언제 사용하나요?

다음 조건이 함께 있을 때 사용합니다.

- 사용자가 `$quality-gauntlet`을 직접 호출함
- 개선할 실제 산출물이 있음
- critic이 반복해서 관찰할 실행 화면, 테스트 seam, 완성된 글, benchmark 같은 검사 방법이 있음
- 어느 쪽이 더 나은지 구분할 레퍼런스, 수치 목표 또는 rubric이 있음
- 여러 번의 builder·critic 실행에 사용할 시간이나 compute 범위가 있음

원인을 모르는 오류는 `diagnosing-bugs`, 이미 정해진 행동을 테스트부터 구현하는 일은 `tdd`, 완성된 변경을 한 번 검토하는 일은 `code-review`가 맡습니다.

## 품질 기준은 acceptance criteria와 다릅니다

테스트, 안전 조건, 필수 동작, 데이터 무결성 같은 acceptance criteria는 모든 후보가 반드시 통과해야 합니다. 시각적으로 좋아졌거나 레퍼런스와 비슷해졌다는 이유로 실패한 필수 조건을 무시할 수 없습니다.

품질 기준은 그 위에서 방향을 정합니다. 예를 들면 다음과 같습니다.

- 실행한 페이지와 승인된 레퍼런스의 레이아웃·계층·사용성 비교
- 같은 workload에서의 latency 또는 처리량 목표
- 완성된 글과 승인된 clarity rubric의 문단별 비교
- 실제 failure-recovery 시나리오와 정해진 복구 목표 비교

레퍼런스가 요구사항을 새로 만들거나 보호된 표현을 그대로 복사할 권한을 주지는 않습니다.

## 어떻게 반복하나요?

lead는 산출물을 독립적으로 바꾸고 평가할 수 있는 임시 improvement cell로 나눕니다. 이 cell은 실행 중 메모일 뿐 GitHub 티켓이 아닙니다.

항상 마지막으로 승인된 accepted candidate와 새 trial candidate를 구분합니다. 가능하면 trial을 격리된 복사본이나 session-owned patch에서 만들고, 제자리 수정이 불가피하면 허가된 경로만 정확히 복구할 방법을 먼저 마련합니다. dirty worktree 전체를 reset·checkout·stash해서 되돌리지 않습니다.

각 반복은 다음 순서로 진행됩니다.

1. accepted candidate와 관련 없는 작업 상태를 고정하고 fingerprint를 기록합니다.
2. builder 하나가 허가된 부분만 trial로 수정하고 focused verification을 실행합니다.
3. 쓰기를 멈추고 필수 gate를 통과한 trial을 다시 고정합니다.
4. fresh critic이 builder의 설명을 보지 않고 accepted candidate, trial, 품질 기준을 비교합니다.
5. critic은 기준 충족·개선·무의미·회귀·비교 불가·무효 중 하나와 직접 증거, 가장 큰 격차, 다음 성공 신호를 반환합니다.
6. 기준을 충족하거나 실제로 개선한 trial만 2단계 승격 대상으로 삼습니다. 정확한 trial을 적용한 뒤 필수 gate와 fingerprint를 다시 통과해야 accepted candidate가 됩니다.
7. 나머지 verdict와 승격 후 gate에 실패한 후보는 경로 한정 복구로 거부하고 이전 accepted fingerprint를 다시 확인합니다.
8. 남은 격차가 범위 안이고 필수 조건을 해치지 않을 때만 다음 builder가 수정합니다.

여러 부분이 바뀐 wave 뒤에는 전체 산출물을 보는 integration critic을 둡니다. 부분별로 좋아졌지만 서로 어울리지 않는 문제를 찾은 뒤, 겹치는 쓰기를 직렬화해 정리합니다.

builder 중단, critic 소실, 실행 환경 오류처럼 승격 전 어느 지점에서든 멈추면 같은 복구 절차를 적용합니다. 단, 복구 write 전에 수정 권한과 필요한 lease가 여전히 유효한지 다시 확인합니다. lease가 상실됐거나 불명확하면 파일을 복구하지 않고 read-only fingerprint, residual trial 상태와 복구 자료만 `blocked` 결과로 바깥 소유자에게 넘깁니다. 어떤 경우에도 확인 없이 accepted candidate가 남았다고 가정하지 않습니다.

## 모델과 에이전트는 어떻게 배치하나요?

스킬은 특정 모델 이름을 고정하지 않습니다.

- 모호한 계획과 최종 통합에는 강한 capability를 사용합니다.
- 범위와 성공 조건이 분명한 builder에는 역할 평가를 통과한 저비용 capability를 사용합니다.
- 객관적인 rubric critic은 효율적인 모델을, 전체적인 판단이나 고위험 검토는 더 강한 모델을 사용합니다.
- 높은 reasoning effort는 실제 대표 작업에서 품질 향상이 확인될 때만 사용합니다.

같은 모델을 여러 context로 나누는 것만으로 공통 blind spot이 사라지지는 않습니다. 중요한 wave와 최종 판정에는 더 강하거나 다른 성격의 checkpoint critic을 사용합니다.

## 언제 멈추나요?

임의로 세 번 같은 횟수를 정하지 않습니다. 다음 중 하나가 관찰되면 멈춥니다.

- `bar-met`: 필수 조건이 모두 통과하고 전체 산출물이 품질 기준을 만족함
- `budget-exhausted`: 다음 완전한 build·critic·검증 단계를 끝낼 자원이 부족함
- `user-stopped`: 사용자가 중단했고 검증되지 않은 trial을 거부한 뒤 accepted candidate를 보존함
- `no-authorized-gap`: 남은 격차를 고치려면 승인된 범위를 넘어야 함
- `blocked`: 독립 critic, 검사 방법, 안전한 환경, 정확한 후보 복구, lease 또는 필요한 권한을 확보할 수 없음

`bar-met`가 아닌 결과를 완료로 표현하지 않습니다. 코드 작업은 Gauntlet 뒤에도 최종 테스트와 별도의 `code-review`를 통과해야 합니다.

## 요청 예시

```text
$quality-gauntlet 이 대시보드를 승인된 레퍼런스와 실제 렌더링 화면으로 비교해 반복 개선해 줘. 동작 테스트는 항상 통과해야 하고, 겹치는 파일은 동시에 수정하지 마.
```
