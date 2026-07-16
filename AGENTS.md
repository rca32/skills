# Repository contract for skill-maintenance agents

## Mission and authority

This repository is the source of truth for personal, reusable Codex development skills. Produce portable skill packages that make agent behavior predictable across repositories without embedding machine-specific paths, project policy, credentials, or transient state.

Instructions in a consuming repository override generic behavior in these skills. Within this repository, this file governs maintenance; each skill's `SKILL.md` governs runtime behavior. When contracts conflict, stop and resolve the ownership conflict instead of duplicating the rule in multiple skills.

Treat `$CODEX_HOME/skills` as installed output. Never use an installed copy as the authoring source.

## Package contract

Every installable skill lives at `skills/<skill-name>/` and contains:

- `SKILL.md`: required runtime instructions;
- `agents/openai.yaml`: required UI and invocation metadata for this repository;
- `references/`: only branch-specific detail directly disclosed from `SKILL.md`;
- `scripts/`: only deterministic operations that are safer to execute than reproduce manually;
- `assets/`: only files copied into user output, never agent instructions.

Do not add a per-skill README. Keep user-facing catalog and installation guidance in the root `README.md`.

## Lifecycle ownership

`work-github-issue` is the sole runtime owner of:

- tracker-contract selection and pre-implementation readiness revalidation;
- blocker and frontier interpretation at claim time;
- same-account session leases and their renewal, takeover, and release;
- assignment/lease projection consistency;
- issue-backed implementation evidence, completion, blocked outcome, and handoff.

Companion skills have deliberately narrower authority:

| Skill | Owns | Must not own |
| --- | --- | --- |
| `triage` | Intake, claim verification, category/state recommendation, authorized labels/comments, durable readiness brief | Implementation lease, code changes, completion evidence |
| `to-spec` | Conversation synthesis, planning spec, testing seams, explicit assumptions/open questions | Invented requirements, implementation readiness, ticket claim |
| `to-tickets` | Authorized two-phase ticket creation, parent/dependency links, graph validation, readiness-state preparation | Ticket claim, implementation evidence, parent completion |
| `documenting-work` | Persistence tier, single authority, repository fallback path, document identity, metadata, index, pointers, and document lifecycle | Domain content, tracker lifecycle, leases, publication authorization |
| `diagnosing-bugs` | Reproduction, minimization, falsifiable diagnosis, and an authorized fix branch | Tracker or lease mutation, unsafe production reproduction, fixes under diagnose-only authorization |
| `complexity-optimizer` | Read-only hotspot analysis and explicitly authorized behavior-preserving optimization | Unknown-cause performance diagnosis, tracker or lease mutation, commit, push, publication |
| `tdd` | Public-seam red-green-refactor implementation after outer authorization | Lease management, tracker mutation, commit, push, publication |
| `code-review` | Read-only Standards and Spec review of a pinned complete worktree snapshot | Edits, tracker mutation, lease management, commit, push |

Planning skills may prepare tracker metadata only when the user authorized those external writes. They must leave runtime claim enforcement to `work-github-issue`.

Every planning mutation must be serialized by a `work-github-issue` lease with `purpose=planning`. Key it to the source/parent issue, or to repository-wide key `0` only when no source issue exists. Read-only assessment and drafting do not claim. Planning leases and implementation leases share the same atomic ref namespace, so they conflict by construction; an active lease cannot change purpose in place. Inner planning skills request, check, and release this outer lease but never redefine its protocol.

## Document-output contract

`documenting-work` is the single source of truth for where durable development documents live. Before another skill writes a spec, decision, research note, diagnosis, review, handoff, or evidence artifact, it must resolve:

1. persistence tier: conversation, tracker, repository, or artifact;
2. exactly one authoritative body;
3. repository path/document ID only when repository persistence is selected;
4. metadata, index, pointer, update, and supersession behavior;
5. write authorization and the outer planning/implementation lease.

Consuming-repository documentation instructions override the bundled fallback. Without a local convention, use `documenting-work/references/document-contract.md` and its resolver. Tracker-authoritative briefs, tickets, evidence, and issue handoffs must not be copied into editable Markdown bodies. Conversation-only reports create no file. Generated runtime output follows the repository artifact/retention contract, not `docs/`.

## Runtime prerequisites

The consuming repository must provide Git, Python 3, an authenticated GitHub CLI, a canonical GitHub remote that matches the requested repository, permission to push the atomic lease refs, and a documented tracker-state/dependency mapping. Implementation also requires an explicit user or repository execution/publication contract for every requested outcome: ticket base and fixed point, worktree eligibility, authorized delivery surface, PR and integration targets, merge authority and strategy, required checks, completion point, and cleanup policy as applicable. When repository instructions omit tracker semantics, use `work-github-issue/references/tracker-contract.md`; that fallback deliberately does not invent repository-specific publication values. Missing authentication, remote identity, tracker mapping, atomic-ref permission, or a publication field required by the requested outcome is a fail-closed preflight result, not authorization to bypass the lease or guess a target.

## Invocation policy

- Keep `tdd`, `diagnosing-bugs`, `complexity-optimizer`, `code-review`, `documenting-work`, and `work-github-issue` eligible for implicit discovery when their trigger descriptions are specific enough to avoid overlap.
- Keep `triage`, `to-spec`, and `to-tickets` explicit by setting `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; these workflows can mutate durable planning state when explicitly asked.
- A request to inspect, review, draft, or explain is read-only. It does not authorize issue creation, label changes, comments, closure, commit, push, or PR publication.
- A request to publish tickets authorizes the validated publication workflow, not implementation or parent closure.

## Authoring workflow

Use `writing-great-skills` for vocabulary, information hierarchy, trigger design, pressure testing, and pruning. Use `skill-creator` for initialization, metadata generation, and structural validation. The primary agent must read both selected instruction files completely before editing.

For a new skill:

1. Define one-sentence purpose, trigger, inputs, observable completion, and explicit non-ownership.
2. Run `skill-creator/scripts/init_skill.py` before manual scaffolding.
3. Replace all generated TODO content; delete unused resource directories.
4. Keep `SKILL.md` below 500 lines. Move detail to a directly linked reference only when it is needed on a conditional branch.
5. Add only resources that the runtime instructions actually reference.

For an existing skill, preserve its public contract unless the requested change intentionally changes behavior. Update the root catalog whenever purpose, invocation, installation, or composition changes.

## SKILL.md requirements

- Frontmatter contains `name` and a trigger-complete `description`. Do not use unsupported invocation fields in frontmatter.
- The description states what the skill does and concrete situations that should trigger it. Include negative scope when adjacent skills could collide.
- Lead with the invariant and decision boundaries, then the workflow.
- Give branches explicit entry conditions and observable exit criteria.
- Prefer public contracts and behavioral outcomes over current file paths, line numbers, framework folklore, or examples tied to one language.
- State mutation authority separately from read-only analysis authority.
- Keep each meaning in one authoritative location. Link to it rather than paraphrasing ownership or safety semantics into several skills.
- Do not depend on another skill that is absent from this public catalog unless the dependency is optional and a complete fallback invariant is stated.

## agents/openai.yaml requirements

- Quote all string values.
- Keep `interface.short_description` between 25 and 64 characters.
- Make `interface.default_prompt` one short sentence that explicitly names `$skill-name`.
- Use `policy.allow_implicit_invocation: false` only for explicitly invoked workflows; omit it when implicit discovery is desired.
- Do not declare tools, icons, or other dependencies that are not shipped or required.

## Safety and portability

- Never commit credentials, account identifiers, tokens, private issue data, production artifacts, or user-specific absolute paths.
- Never make a diagnostic reproduce real orders, payments, destructive writes, messages, or production traffic without separate explicit authorization and repository safety gates.
- Preserve dirty worktrees and unrelated user changes. Do not clean, reset, stash, switch revisions in place, or overwrite files to make a test convenient.
- Use disposable repositories, worktrees, remotes, fixtures, and synthetic tracker inputs for scripts and forward tests.
- Scripts that coordinate concurrency must use atomic remote operations, bind state to a repository/session identity, fail closed on ambiguous results, and include deterministic tests for competing actors.
- External write recovery must reconcile unknown outcomes before retrying. Never blindly repeat issue creation, order-like operations, or lease mutation.
- The `rca.*` identifiers in the version-1 issue-lease wire protocol are compatibility identifiers, not a project dependency. Do not rename them without a dual-read migration that preserves collision detection across installed versions.

## Required validation

For every changed skill:

1. Run `quick_validate.py skills/<skill-name>` from the installed `skill-creator`.
2. Execute every changed deterministic script against disposable inputs; syntax-check interactive templates.
3. Scan the package for TODO markers, local absolute paths, project-only names, obsolete dependencies, unsupported frontmatter, and broken relative references.
4. Forward-test complex behavior with realistic prompts that do not reveal the intended answer. Include authorization ambiguity, partial external failure, dirty-worktree coverage, and same-account collision when relevant.
5. Run independent Standards and Spec reviews. Do not let one reviewer see the other's conclusions before both reports are complete.
6. Run `git diff --check` after files are staged so new-file whitespace is included.

The Standards review checks this file, `writing-great-skills`, `skill-creator`, portability, disclosure, duplication, metadata, and safety. The Spec review checks the user's requested outcome, intended selection, composition boundaries, and missing runtime behavior.

Do not publish with unresolved blocker/high findings. Repair medium findings when they affect safety, ownership, invocation, or predictable completion; otherwise record the reason for deferral.

## Distribution sequence

1. Confirm the repository worktree contains only the intended skill/catalog changes.
2. Validate and review the source changes.
3. Commit intentionally and push the source repository.
4. Install or reinstall the affected `skills/<name>` packages from `rca32/skills` using `skill-installer`.
5. Verify each installed package matches the published source and instruct the user to start a new session for catalog refresh.

Installation is never evidence that unpublished local changes are correct. Publication must precede installation so the public repository remains reproducible.
