---
document_id: "research:2026-08-18:postgres-durable-workflow-preference"
kind: "research"
title: "PostgreSQL-native durable workflow research"
status: "active"
authority: "repository"
source: "https://github.com/microsoft/pg_durable"
created: "2026-08-18"
updated: "2026-08-18"
supersedes: null
---

> 이 문서는 연구 원문입니다. 여기서 정리한 runtime 취향의 원본은 [`apply-architecture-playbook` 항목 002](../../skills/apply-architecture-playbook/references/002-postgres-durable-workflows.md)입니다.

네, 저는 **추천할 만하다고 봅니다.** 특히 방금 글의 철학을 한 단계 더 밀어붙이는 선택에 가깝습니다.

Kerkour의 접근이 원래

```text
PostgreSQL
  ├─ DB
  ├─ Queue
  ├─ Scheduler
  └─ Coordination
```

이라면 `pg_durable`은 여기에 **durable execution / workflow orchestration 자체를 PostgreSQL 안으로 넣는 것**입니다. Microsoft도 프로젝트를 “PostgreSQL in-database durable execution”으로 설명하고 있고, SQL로 workflow를 정의하면 각 단계를 checkpoint하여 crash/restart/step failure 후 마지막 durable checkpoint부터 재개하도록 설계했습니다.

제가 이 글에 덧붙인다면 오히려 **단순 `FOR UPDATE SKIP LOCKED` queue를 직접 구현하는 것보다 pg_durable을 먼저 검토하라**고 쓰고 싶습니다.

## 왜 잘 맞는가

기존 글의 방식은 대략 이겁니다.

```text
jobs table
   ↓
FOR UPDATE SKIP LOCKED
   ↓
Rust worker
   ↓
status / retry_count / scheduled_at
```

훌륭하고 단순합니다. 다만 실제 시스템이 커지면 자연스럽게 이런 코드가 생깁니다.

```text
jobs
job_attempts
retry_count
next_retry_at
status
error
progress
parent_job_id
scheduled_at

worker polling
retry logic
backoff
crash recovery
job dependency
fan-out / fan-in
scheduler
monitoring
```

결국 **작은 workflow engine을 직접 만들고 있는 셈**입니다.

`pg_durable`의 문제의식이 정확히 이것입니다. README에서도 기존에 `pg_cron + jobs table + status columns + retry counters + polling worker`, 혹은 queue + workers + 별도 state table을 조합하는 상황을 대체 대상으로 명시하고 있습니다.

그래서 구조를

```text
Rust / Axum
     │
     │ df.start(...)
     ▼
PostgreSQL
 ├─ Application Data
 └─ pg_durable
      ├─ Queue
      ├─ State
      ├─ Checkpoints
      ├─ Retry
      ├─ Scheduling
      └─ Workflow Execution
```

까지 줄일 수 있습니다.

이게 Kerkour의 **“새 인프라를 추가하기 전에 PostgreSQL이 이미 할 수 있는지 보라”**는 철학과 아주 잘 맞습니다.

---

## 특히 `pg_durable`의 진짜 장점은 Queue가 아닙니다

이 부분을 강조하는 게 좋습니다.

`pg_durable`을 단순히

> PostgreSQL 기반 queue library

라고 보면 가치가 절반 이하로 줄어듭니다.

핵심은 **durable workflow**입니다.

예를 들어 AI 뉴스 파이프라인을 생각하면:

```text
기사 후보 생성
   ↓
원문 수집
   ↓
LLM 분석
   ↓
팩트 검증
   ↓
초안 생성
   ↓
Desk validation
   ↓
Publish
```

중간의 `LLM 분석`까지 끝났는데 서버가 죽었다면 일반 worker 방식에서는 복구 로직을 직접 만들어야 합니다.

`pg_durable` 방식의 핵심은:

```text
Step 1 ✓ checkpoint
Step 2 ✓ checkpoint
Step 3 ✓ checkpoint
Step 4 ← crash
```

재시작 후:

```text
Step 1 skip
Step 2 skip
Step 3 skip
Step 4 resume
```

입니다.

Microsoft의 README 역시 crash, restart 또는 특정 step 실패 후 **마지막 durable checkpoint에서 execution을 재개**하는 것을 핵심 모델로 설명합니다.

이건 단순 queue와 상당한 차이가 있습니다.

---

# 제가 구성한다면

Kerkour의 원래 아키텍처:

```text
             HTTP
               │
               ▼
            Service
               │
               ▼
          Repository
               │
               ▼
          PostgreSQL

Background worker
       │
       ├── jobs table
       ├── SKIP LOCKED
       └── advisory lock
```

를 다음처럼 바꾸겠습니다.

```text
                    Axum
                      │
                      ▼
                   Service
                  /       \
                 /         \
                ▼           ▼
          Repository     Workflow
                │           │
                └─────┬─────┘
                      ▼
                PostgreSQL 18
                 ┌─────────┐
                 │ SQLx    │
                 │         │
                 │pg_durable│
                 └─────────┘
```

그리고 역할을 명확하게 나눕니다.

**Repository**

```text
CRUD
query
transaction
```

**Service**

```text
business logic
validation
authorization
workflow initiation
```

**pg_durable**

```text
long-running jobs
retry
checkpoint
scheduling
fan-out
fan-in
workflow state
crash recovery
```

이 구성이 상당히 깨끗합니다.

---

# 예를 들어 Rust에서는

application이 모든 worker lifecycle을 관리할 필요 없이 대략:

```rust
let workflow_id = sqlx::query_scalar!(
    r#"
    SELECT df.start(
        'SELECT id
           FROM documents
          WHERE processed = false
          LIMIT 100'
        |= > 'batch'
        ~>
        'UPDATE documents
            SET processed = true
          WHERE id IN (SELECT id FROM $batch.*)'
    )
    "#
)
.fetch_one(&pool)
.await?;
```

같은 방향으로 갈 수 있습니다.

프로젝트가 제공하는 quick example도 실제로 `df.start()`와 SQL graph를 이용해 batch 작업을 durable하게 수행합니다.

그러면 Rust backend는 점점 더

```text
Request handler
Business logic
Workflow trigger
```

쪽에 집중할 수 있습니다.

---

# AI/Agent 시스템에서는 더 매력적입니다

저는 특히 **AI workflow에서는 pg_durable 가치가 더 크다**고 봅니다.

AI workflow는 일반적인 CRUD background job보다 실패 가능성이 훨씬 많습니다.

```text
LLM 호출
Embedding API
검색 API
웹 크롤링
외부 데이터 API
validation
human approval
retry
rate-limit
timeout
```

예를 들어:

```text
Document
   │
   ▼
Chunk
   │
   ├───────┬────────┬────────┐
   ▼       ▼        ▼        ▼
Embed    Entity   Summary   Metadata
   │       │        │        │
   └───────┴────────┴────────┘
                │
                ▼
             Index
```

같은 fan-out/fan-in workflow가 필요해집니다.

pg_durable README에서도 직접 사용 사례로 **vector embedding pipeline, ingest pipeline, external API workflow, fan-out aggregation, AI pipeline** 등을 명시하고 있습니다.

그래서 AI backend라면

```text
Rust + PostgreSQL + pg_durable
```

조합이 일반 CRUD backend보다 오히려 더 설득력 있습니다.

---

# 그렇다고 모든 job을 pg_durable로 넣지는 않겠습니다

여기에는 분명한 경계가 있습니다.

저라면 세 단계로 나눕니다.

### Level 1 — 그냥 SQL

```text
DELETE FROM sessions
WHERE expires_at < now();
```

이 정도를 굳이 durable workflow로 만들 필요 없습니다.

### Level 2 — 간단한 Queue

```text
send_email
generate_thumbnail
invalidate_cache
```

아주 짧고 idempotent한 작업이라면 기존

```sql
FOR UPDATE SKIP LOCKED
```

queue가 더 단순할 수도 있습니다.

### Level 3 — Durable Workflow

```text
LLM pipeline
document processing
article generation
data ingestion
multi-stage publication
approval flow
long-running batch
```

이런 경우부터 `pg_durable`이 아주 강합니다.

즉 저는:

```text
simple async task
     ↓
SKIP LOCKED queue

multi-step / expensive / recoverable
     ↓
pg_durable
```

로 가져가겠습니다.

---

# 중요한 단점도 있습니다

현재 시점에서 **프로덕션 표준으로 무조건 추천**이라고 쓰기에는 조금 조심해야 합니다.

프로젝트는 2026년 2월 만들어진 비교적 신생 프로젝트이며 현재도 매우 활발하게 개발 중입니다. 최근 며칠 사이에도 background worker lifecycle race condition 수정, graph node batch insertion 등의 변경이 계속 들어오고 있습니다.

그리고 가장 중요한 제약은 이것입니다.

### 1. PostgreSQL extension 설치가 필요

현재 PostgreSQL **17/18**을 대상으로 하고 있고 `shared_preload_libraries`에 `pg_durable`을 넣어 재시작해야 합니다. 관리형 PostgreSQL 환경에서는 extension 설치 여부가 큰 제약이 될 수 있습니다.

### 2. SQL-shaped workflow

pg_durable의 workflow는 의도적으로 SQL 중심입니다.

README에서도 arbitrary application code나 non-HTTP SDK, 복잡한 in-memory control flow가 주가 된다면 일반적인 orchestrator가 더 적합할 수 있다고 명시합니다.

예를 들어

```text
Python ML model
   ↓
GPU inference
   ↓
Kafka
   ↓
S3
   ↓
Spark
```

같은 시스템 전체를 pg_durable 안에 집어넣는 것은 좋지 않습니다.

### 3. DB가 compute까지 담당

이건 장점이면서 위험입니다.

```text
PostgreSQL
= database
+ workflow engine
+ worker
```

가 되므로 무거운 workflow가 DB workload와 서로 영향을 줄 수 있습니다.

따라서 저는 CPU-intensive 작업 자체를 Postgres 안에서 수행하기보다는

```text
pg_durable
    │
    ├── state
    ├── orchestration
    └── external HTTP call
              ↓
         Rust/AI worker
```

같은 방향을 더 선호합니다.

---

# 그래서 글에 추가한다면 이렇게 쓰는 게 좋겠습니다

단순히

> `pg_durable`을 추천한다.

보다 저는 다음 주장을 넣겠습니다.

> **PostgreSQL을 이미 시스템의 중심으로 사용한다면 직접 jobs table, retry counters, polling workers, scheduler state를 구현하기 전에 Microsoft의 `pg_durable` 같은 PostgreSQL-native durable execution layer를 검토할 가치가 있다.**
>
> 단순한 asynchronous job에는 `FOR UPDATE SKIP LOCKED`가 여전히 훌륭하지만, 작업이 multi-step workflow로 발전하는 순간 직접 구현해야 하는 retry, checkpoint, progress tracking, scheduling, fan-out/fan-in, crash recovery의 복잡성이 빠르게 증가한다. `pg_durable`은 바로 이 orchestration state를 PostgreSQL 안으로 가져온다.

그리고 아키텍처를 한 줄로 표현한다면:

```text
Tokio + Axum + SQLx + PostgreSQL + pg_durable
```

저는 이 조합이 **Kerkour 글의 2026년판 업그레이드 버전**에 상당히 가깝다고 봅니다.

특히 지금처럼 **PostgreSQL 중심으로 큐와 상태관리를 단순화하려는 시스템**이라면 `pg_durable`은 꽤 자연스러운 선택입니다. 다만 저는 초기부터 모든 queue를 pg_durable로 통일하기보다는, **단순 queue는 SKIP LOCKED, 복잡한 장기 workflow는 pg_durable**이라는 두 단계 구조를 권하겠습니다. 이 경계가 운영 면에서도 가장 안정적입니다.
