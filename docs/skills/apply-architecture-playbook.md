# `apply-architecture-playbook`: 개인 아키텍처 취향 적용하기

정확한 실행 계약: [`skills/apply-architecture-playbook/SKILL.md`](../../skills/apply-architecture-playbook/SKILL.md)

## 한마디로

내가 선호하는 stack, topology와 운영 방식을 구체적인 시스템에 적용하는 **명시 호출 전용 설계 취향 사전**입니다.

보편적인 “best architecture”를 찾는 스킬이 아닙니다. 프로젝트의 확정 제약과 실제 증거가 먼저이며, 그 안에서 여러 선택이 가능할 때 내 취향을 기본값으로 사용합니다. 맞지 않는 경우에는 억지로 적용하지 않고 이탈 이유와 다시 적용할 조건을 밝힙니다.

## 처음 등록된 항목

### 001 — Rust + PostgreSQL 계층형 모놀리스

중간 규모의 transactional backend를 stateless Rust application과 PostgreSQL 중심으로 시작합니다. HTTP·scheduler·worker는 얇은 delivery layer, authorization·validation·business rule·transaction orchestration은 service, SQL과 data access는 repository가 맡습니다.

명시적인 SQLx 쿼리, service-layer cache policy, PostgreSQL advisory lock과 작은 `SKIP LOCKED` queue를 우선하며, 측정된 병목이나 독립 운영 요구가 생기기 전에는 microservice와 별도 인프라를 추가하지 않습니다.

### 002 — PostgreSQL-native durable workflow

001 위에 선택적으로 적용하는 overlay입니다. 여러 단계로 구성되고 중간 결과가 비싸며 retry·checkpoint·scheduling·fan-out/fan-in·crash recovery가 중요한 작업에는 직접 작은 workflow engine을 만들기 전에 `pg_durable` 같은 PostgreSQL-native durable execution을 검토합니다.

한 SQL 문은 plain SQL, 짧고 idempotent한 비동기 작업은 작은 `SKIP LOCKED` queue, 복잡한 장기 작업만 durable workflow 후보로 구분합니다. CPU-heavy 또는 SDK-heavy compute는 PostgreSQL 안에 밀어 넣지 않고 외부 worker와 명시적인 경계를 둡니다.

`pg_durable`은 현재 maturity와 지원 조건이 변할 수 있으므로 실제 도입 전 공식 문서를 다시 확인하는 조건부 취향입니다.

## 어떻게 적용하나요?

먼저 workload, latency와 consistency, data ownership, failure recovery, 배포 환경, database extension 권한, 팀 역량과 기존 결정을 확인합니다. 이어서 각 사전 항목을 다음 상태 중 하나로 판정합니다.

- **적용:** 제약과 증거가 선호 기본값을 지지함
- **조건부 적용:** 명시한 가정이나 현재 기술 조건이 성립할 때 적합함
- **보류:** 판단을 바꿀 정보가 부족함
- **이탈:** 확정 제약이나 관측된 부적합이 취향보다 우선함

결과는 선택한 base와 overlay, component-level 책임, 취향과 증거의 구분, 운영 비용, 이탈 조건, 아직 남은 module interface·seam 질문을 포함합니다. 구체적인 interface와 seam 선택은 `codebase-design`이 담당합니다.

## 사전을 계속 확장하려면

새 항목은 사용자가 직접 작성하거나 승인한 취향만 등록합니다. 각 항목에는 안정적인 ID, base 또는 overlay 종류, 기본 상태, 적용·회피 조건, 선호 구조, 책임 경계, 비용, 이탈 조건, 다른 항목과의 관계, 다시 확인해야 할 날짜 기반 사실을 둡니다.

사전 추가는 이 스킬의 읽기 전용 runtime 동작이 아니라 스킬 유지보수 작업입니다. 새 연구 문서를 주면서 `apply-architecture-playbook`에 새 항목으로 추가해 달라고 요청하면 됩니다.

## 요청 예시

```text
$apply-architecture-playbook 이 문서 처리 서비스에 내 아키텍처 취향 사전을 적용해 기본 구조와 예외 조건을 정리해 줘.
```
