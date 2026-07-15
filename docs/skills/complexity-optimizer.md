# `complexity-optimizer`: 복잡도와 성능 hotspot 개선하기

정확한 실행 계약: [`skills/complexity-optimizer/SKILL.md`](../../skills/complexity-optimizer/SKILL.md)

## 한마디로

큰 코드베이스에서 반복 스캔, 중첩 반복, 불필요한 재계산, 렌더링 낭비와 N+1 요청 같은 **복잡도·성능 hotspot을 찾아 우선순위를 정하고, 동작을 보존하는 안전한 개선을 제안하거나 구현하는 스킬**입니다.

Scanner 결과만 보고 코드를 고치지 않습니다. 실제 hot path인지, 입력 크기가 충분히 큰지, 기존 정렬·중복·권한 같은 의미가 바뀌지 않는지를 주변 코드와 테스트로 확인합니다.

## 언제 사용하나요?

- 여러 파일을 훑어 성능 hotspot 보고서를 만들 때
- `O(n²)` 중첩 탐색이나 반복 membership 검사를 찾을 때
- UI render 중 반복되는 filter·sort·grouping을 줄일 때
- 반복문 안의 DB/API 호출로 생기는 N+1을 개선할 때
- 이미 확인된 병목을 map, set, batching, memoization 등으로 최적화할 때

사용자가 겪는 느려짐의 원인이 아직 불명확하다면 먼저 `diagnosing-bugs`로 증상을 재현하고 원인을 분리합니다. 변경 전체를 저장소 규칙과 명세에 맞춰 리뷰하려는 요청은 `code-review`가 담당합니다.

## 보고서와 구현 권한은 다릅니다

“분석해 줘”, “scan해 줘”, “보고서를 작성해 줘”라는 요청은 읽기 전용입니다. 이때는 구현 파일을 수정하지 않고 다음 내용을 포함한 전체 보고서를 반환합니다.

- 조사 범위와 발견한 기술 stack
- 영향이 큰 hotspot 순위
- 파일과 줄, 현재 패턴과 예상 복잡도
- 추천 변경과 변경 후 예상 복잡도
- 위험도와 필요한 테스트·benchmark
- 구현 파일을 수정하지 않았다는 명시와, 저장했다면 권위 있는 보고서 위치

보고서는 기본적으로 대화에만 둡니다. 사용자가 저장이나 게시를 분명히 요청하면 `documenting-work`가 대화, tracker, 저장소 문서 중 권위 있는 원본 하나와 경로·metadata·index를 정합니다. GitHub 댓글이나 evidence 게시 권한은 바깥 `work-github-issue`가 담당합니다.

“최적화해 줘”, “적용해 줘”, “refactor해 줘”처럼 변경을 분명하게 요청한 경우에만 구현합니다. GitHub 이슈 작업이라면 바깥 `work-github-issue`가 현재 세션의 implementation lease를 확인해야 합니다.

## 실제 흐름

### 1. 기준점 확인

언어, framework, 테스트·빌드 명령, 성능에 민감한 경로와 기존 테스트를 확인합니다. 번들 scanner로 여러 언어의 의심 지점을 빠르게 찾지만, 그 결과는 조사 후보일 뿐 결론이 아닙니다.

### 2. 후보 순위화

hot path, 큰 입력, render loop, DB/API loop와 공유 utility를 우선합니다. 알고리즘 복잡도 개선과 작은 constant-factor 정리를 구분하고, 주변 코드를 읽어 현재와 추천 복잡도를 추정합니다.

### 3. 동작 보존 증명

빈 입력, 중복, 정렬 안정성, null, 오류, 권한, pagination, time zone과 mutation side effect를 확인합니다. 기존 동작이나 테스트 seam이 불명확하면 코드를 고치지 않고 필요한 결정을 보고합니다.

### 4. 작은 최적화와 검증

자료 형태가 허용할 때만 map·set, grouping, two-pointer, binary search, memoization, batching 같은 방법을 적용합니다. Focused test와 관련 suite를 실행하고, 성능 주장이 중요하면 반복 가능한 benchmark나 측정을 함께 남깁니다.

## Scanner 사용

설치된 스킬의 scanner는 다음처럼 실행합니다.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/complexity-optimizer/scripts/analyze_complexity.py" /path/to/repo --format markdown
```

Python, JavaScript·TypeScript, Java, Go, C/C++, C#, Ruby, PHP와 Swift 파일의 흔한 패턴을 탐색합니다. 아무것도 보고하지 않았다고 성능 문제가 없다는 뜻은 아니므로 framework lifecycle이나 database query처럼 정적 pattern만으로 찾기 어려운 경로는 직접 확인합니다.

## 하지 않는 일

- 일반적인 Standards·Spec 코드 리뷰
- 원인 미상의 성능 회귀를 증거 없이 추측
- 분석만 요청받고 구현 파일 수정
- issue lease, tracker 상태, commit, push, PR 또는 merge 처리
- 작은 입력의 차가운 경로를 복잡한 자료구조로 무조건 교체

## 요청 예시

```text
$complexity-optimizer 이 저장소를 분석해서 영향도가 높은 복잡도 hotspot과 개선안을 보고해 줘. 아직 수정하지 마.
```
