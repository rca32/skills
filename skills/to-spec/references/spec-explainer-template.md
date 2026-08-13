# Non-normative spec explainer template

Read this after the authoritative spec body is audited. Before fingerprinting, use only the prose rules for a disposable explainability probe with no metadata or identity. Generate the final explainer only after the exact authoritative body is frozen and fingerprinted. Keep it separate; never append it to the spec.

Select metadata by persistence branch:

- Repository: use the full durable frontmatter below.
- Conversation draft: use `kind`, `status`, `authority: "conversation"`, `normative: false`, `derived_from: "conversation-spec:<key>"`, and `source_fingerprint`; omit durable dates, `source`, and `supersedes`.
- Tracker authority with a conversation explainer: use the same conversation fields, but set `derived_from` to the stable tracker identity.

Fingerprint scope is branch-specific and never includes the explainer: for a conversation spec, hash only the canonical `conversation-spec:<key>` content and exclude its length-delimited envelope; for a repository spec, hash the exact complete spec-file bytes after readback, including its own metadata; for a tracker spec, hash the exact issue-body bytes after readback, including stable markers and planning fields but excluding provider chrome. Identity, fingerprint, byte-count, and reporting fields that surround a conversation artifact stay outside its hashed content.

```markdown
---
document_id: "spec-explainer:<source-key>:<slug>"
kind: "spec-explainer"
title: "<spec title> — 쉬운 설명"
status: "<source status>"
authority: "repository"
source: "<authoritative spec path or URL>"
derived_from: "<authoritative spec document_id or tracker identity>"
source_fingerprint: "to-spec-body-v1:<sha256>"
normative: false
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
supersedes: null
---

# <spec title> — 쉬운 설명

> 이 문서는 사람의 이해를 위한 파생 설명입니다.
> 구현, 티켓 분해, 테스트와 리뷰 기준으로 사용할 수 없습니다.
> 개발 기준은 `derived_from`이 가리키는 원본 명세만 따릅니다.

## 왜 필요한가

<문제와 원하는 결과를 일상적인 말로 2~4문장>

## 무엇이 달라지는가

- <사람이 관찰할 변화>

## 동작 순서

1. <첫 단계>
2. <다음 단계>

## 하지 않는 것

- <중요한 범위 밖 또는 오해하기 쉬운 제외 사항>

## 아직 정해지지 않은 것

- <사람이 알아야 하는 material open question과 영향>
```

Use at most five sections and seven flow steps. Omit empty sections. Prefer short sentences and familiar words; explain an unavoidable term inline. Preserve material safety, failure, compatibility, and unresolved-state meaning, but omit requirement IDs, test mechanics, protocol markers, internal file paths, and implementation detail unless a human cannot understand the outcome without them.

Every sentence must be entailed by the frozen spec. Add no fact, requirement, advice, decision, workaround, or interpretation. If simplification would change meaning, keep the necessary precise term and explain it briefly.
