# can-migrate-es-toolkit — `rjsf-team/react-jsonschema-form`

```
/can-migrate-es-toolkit https://github.com/rjsf-team/react-jsonschema-form ko
```

**분석일:** 2026-08-09 · **저장소 상태:** `main` @ 6.7.1 · **판정: 78 / 100 — 권장**

---

## Stage 1 — 마이그레이션 게이트

`package.json` 19개 스캔 (pnpm + Nx 모노레포). 그중 9개에서 lodash 발견.

| 패키지                     | lodash          | lodash-es | 위치              |
| -------------------------- | --------------- | --------- | ----------------- |
| `@rjsf/core`               | ✅              | ✅        | `dependencies`    |
| `@rjsf/utils`              | ✅              | ✅        | `dependencies`    |
| `@rjsf/validator-ajv8`     | ✅              | ✅        | `dependencies`    |
| `@rjsf/validator-ata`      | ✅              | ✅        | `dependencies`    |
| `@rjsf/validator-cfworker` | ✅              | ✅        | `dependencies`    |
| `@rjsf/antd`               | ✅              | ✅        | `dependencies`    |
| `@rjsf/shadcn`             | ✅              | ✅        | `dependencies`    |
| `@rjsf/semantic-ui`        | ✅              | —         | `dependencies`    |
| `@rjsf/playground`         | ✅              | —         | `dependencies`    |
| root                       | `@types/lodash` | —         | `devDependencies` |

**→ Stage 2 진행.**

---

## Stage 2 — 마이그레이션 대상 평가

### 2-1. 프로젝트 성격

npm에 배포되는 **라이브러리 모노레포**. `@rjsf/*` 스코프로 18개 패키지 배포, Apache-2.0, JSON Schema 기반 React 폼 빌더이며 테마 플러그인 구조(antd, MUI, Chakra, shadcn, Semantic UI 등)를 가짐.

모든 패키지가 `main` / `module` / `exports` / `files: ["dist", "lib", "src"]`를 선언 — 전부 npm으로 나감.

**플러그인 노출: 없음.** 테마들은 `@rjsf/utils`가 직접 export하는 API를 통해서만 소비한다. lodash 인스턴스나 lodash 타입이 공개 API 표면으로 새지 않으므로 호환 shim이 필요 없다.

### 2-2. lodash가 배포 번들에 포함되는가?

**포함된다.** 9개 패키지 모두 `devDependencies`가 아니라 `dependencies`. `@rjsf/*`를 설치하는 모든 사용자가 lodash를 함께 받는다.

주목할 빌드 세부사항 — 이 저장소는 lodash를 두 모듈 시스템에서 모두 쓰기 위해 커스텀 `tsc-alias` replacer를 유지하고 있다.

```ts
// tsc-alias-replacer/lodashReplacer.ts
export default function lodashReplacer({
  orig,
}: AliasReplacerArguments): string {
  if (orig.startsWith("from 'lodash/")) {
    const origLodashEs = orig
      .substring(0, orig.length - 1)
      .replace("lodash/", "lodash-es/");
    return `${origLodashEs}.js'`;
  }
  return orig;
}
```

소스는 `lodash/*`로 작성하고, ESM 빌드 시 `lodash-es/*.js`로 치환한다. 7개 패키지가 `lodash`와 `lodash-es`를 **둘 다** 의존성으로 갖고, 패키지마다 `compileReplacer` 빌드 스텝과 `tsconfig.replacer.json`이 존재하는 이유가 이것이다. es-toolkit은 ESM/CJS 듀얼 빌드와 타입을 기본 제공하므로, 이 배관 전체를 삭제할 수 있다.

**전이 의존성 lodash (마이그레이션 후에도 잔존):** `pnpm-lock.yaml` 기준 20개 패키지가 여전히 lodash에 의존.

- 개발 전용: `@docusaurus/*` (문서 사이트), `html-webpack-plugin`, `caniuse-api`, `@babel/helper-define-polyfill-provider`
- **배포에 포함:** `semantic-ui-react` (→ `@rjsf/semantic-ui`), `@fluentui/*` (→ `@rjsf/fluentui-rc`)

즉 `core` / `utils` / `validator-*`는 완전히 lodash-free가 되지만, Semantic UI·Fluent UI 테마는 상위 UI 라이브러리를 통해 lodash를 계속 끌고 온다. 차단 요소는 아니지만, 주장할 수 있는 범위의 상한선이다.

### 2-3. import 패턴과 범위

| 패턴                                           | 개수    | 번들 영향                  |
| ---------------------------------------------- | ------- | -------------------------- |
| 전체 import (`import _ from 'lodash'`)         | 1       | 테스트 파일뿐              |
| 네임드 import (`import { get } from 'lodash'`) | 4       | 테스트 3, 플레이그라운드 1 |
| **서브패스 (`import get from 'lodash/get'`)**  | **179** | 이미 함수 단위 최적화됨    |

**101개 파일에 걸쳐 184개 import** (`src/` 63개, `test/` 38개).

| 패키지                              | 파일 수 |
| ----------------------------------- | ------- |
| `utils`                             | 58      |
| `core`                              | 18      |
| `validator-ata`                     | 7       |
| `validator-ajv8`                    | 6       |
| `validator-cfworker` / `playground` | 각 3    |
| `shadcn` / `semantic-ui` / `antd`   | 각 2    |

사용 빈도 상위: `get` (40), `noop` (28), `isObject` (14), `isEmpty` (14), `set` (10), `has` (10), `cloneDeep` (8), `isString` (7).

`src/` 기준 고유 함수 38개. **38개 전부 `es-toolkit/compat`에 존재**(런타임 `typeof` 검사로 확인).

> **이득 규모에 대한 참고:** 서브패스 import가 압도적이므로 lodash는 _이미_ 함수 단위로 트리셰이킹되어 있다. 따라서 `import _ from 'lodash'` 위주 코드베이스보다 상승폭이 작다. 이득은 함수별 바이트 크기, 의존성 그래프 단순화, 빌드 설정 제거이지 "실수로 lodash 70 kB를 배포하고 있었다"가 아니다.

### 2-4. 하드 블로커

`sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext` — **모두 없음.** `lodash/fp` 사용도 없음.

### Stage 2 요약

```
Repository: rjsf-team/react-jsonschema-form
2-1 (성격):   배포용 라이브러리 모노레포 (18패키지) — 플러그인 노출: 없음
2-2 (번들):   배포 포함 (dependencies) — 전이 lodash: semantic-ui-react, @fluentui/*, docusaurus(dev)
2-3 (import): 전체 ×1 / 네임드 ×4 / 서브패스 ×179 — 파일: 101 — 상위: get, noop, isObject, isEmpty, set
2-4 (블로커): 없음

Stage 2 판정: 마이그레이션 후보
```

---

## Stage 3 — 조직적 신호

| 신호                  | 결과                                                                                                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **활동성**            | 매우 활발. 2026-08-09, 08-08, 08-07, 08-03 커밋. 최근 2주간 외부 기여자 PR 다수 머지(#5171, #5174, #5175, #5159).                                                              |
| **릴리스 주기**       | 6.7.1이 2026-07-24 릴리스. Dependabot 활성화 및 머지 중.                                                                                                                       |
| **선행 사례**         | 이 저장소에서 `es-toolkit` GitHub 검색 → **0건**. lodash 관련은 dependabot 버전 범프뿐(#5020, #5018, lodash 4.17.23 → 4.18.1). 배려하거나 해명해야 할 실패한 선행 시도가 없음. |
| **CLA**               | **없음.** `CONTRIBUTING.md`에 CLA 문구 없고 `.github/`에 CLA 봇도 없음. 기여 마찰이 낮다.                                                                                      |
| **이슈 관리**         | `stale.yml` 임계값이 456일 — 이슈를 빨리 닫지 않는 인내심 있는 메인테이너.                                                                                                     |
| **공개 API의 lodash** | 없음. 내부 사용만.                                                                                                                                                             |

건강하고 활발히 유지보수되며 외부 PR을 받아들이는 저장소, 법적 절차도 없음. 제안하기 좋은 조건.

---

## Stage 4 — 검증 및 측정

모노레포 어디에도 `benchmark` / `bench` / `perf` 스크립트가 없어 스킬의 벤치마크 경로는 적용 불가. 대신 배포 라이브러리에서 더 중요한 두 가지로 대체했다 — **실제로 여전히 동작하는가**, 그리고 **소비자가 몇 바이트를 아끼는가**.

### 4-1. 마이그레이션 적용

`scripts/migrate_lodash_imports.py` dry-run → 184건 치환, 101개 파일, 블로커 0. `--write`로 적용 후 9개 패키지 매니페스트에서 `lodash` + `lodash-es`를 `es-toolkit`으로 교체.

**자동 변환 후 수동 수정이 3곳 필요했다** ([번들 스크립트의 알려진 문제](#번들-스크립트의-알려진-문제) 참조 — 2개는 스크립트 버그):

1. `import get from 'lodash/get'` → 스크립트가 `import get from 'es-toolkit/compat'`, 즉 **default** import를 생성. `es-toolkit/compat`에는 대응하는 default export가 없으므로 모든 호출부가 네임스페이스 객체를 받게 된다. 97개 파일 영향. 올바른 형태는 `import { get } from 'es-toolkit/compat'`.
2. 별칭 import(`import _get from 'lodash/get'`, `Form.tsx`에만 7개)는 `import { get as _get } from 'es-toolkit/compat'`가 되어야 한다. 3개 파일 영향.
3. `packages/utils/test/getTestIds.test.ts`가 `vi.mock('lodash/uniqueId')`를 사용. 테스트 하네스 경로라 네임드 export를 대상으로 바꿔야 한다 — 어떤 마이그레이션에서든 수작업이며 es-toolkit 결함이 아니다.

### 4-2. 테스트 결과

기준선 `@rjsf/utils`: **79개 파일 / 1440개 테스트 통과.**

| 단계                    | 결과                                                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 스크립트 원본 출력 직후 | 30개 파일 실패, **678개 테스트 실패** — 전부 default import 버그 때문(`Maximum call stack size exceeded`, `mockClear is not a function` 등) |
| import 수정 후          | 1개 파일 실패, 6개 테스트 실패 — 낡은 `vi.mock` 경로만                                                                                      |
| mock 수정 후            | **79개 파일 / 1440개 테스트 통과 — 기준선과 동일**                                                                                          |

모노레포 전체:

```
pnpm run build  →  NX  Successfully ran target build for 18 projects
pnpm run test   →  NX  Successfully ran target test for 17 projects
                    9,684개 테스트 통과, 0 실패
```

**9,684개 테스트 어디에서도 동작 차이가 발견되지 않았다.** 전체 스위트에서 `es-toolkit/compat` 비호환은 하나도 드러나지 않았다.

TypeScript 관련 참고 — `Form.tsx:1042`에는 재귀적인 `ErrorSchema` 타입에 대한 `_get(schemaValidationErrorSchema, path)` 때문에 `// @ts-expect-error TS2590`가 달려 있다. es-toolkit의 `get`도 동일하게 TS2590을 재현하므로 지시자는 그대로 유지 — 동일 동작이며 새 억제가 필요하지 않다.

diff 규모: **111개 파일 변경, +234 / −405.**

### 4-3. 번들 크기

**(a) 실제 소비자 번들** — `@rjsf/core` + `@rjsf/validator-ajv8` + `@rjsf/utils`를 `esbuild --bundle --minify`로 묶고 React는 external. 마이그레이션 전/후의 실제 `lib/` 산출물 기준.

|                   | minified              | gzip                 |
| ----------------- | --------------------- | -------------------- |
| 이전 (lodash-es)  | 392,823 B             | 131,667 B            |
| 이후 (es-toolkit) | 382,142 B             | 125,604 B            |
| **차이**          | **−10,681 B (−2.7%)** | **−6,063 B (−4.6%)** |

이 번들은 AJV가 대부분을 차지하기 때문에 비율로는 작게 보인다. 절대값이 정직한 숫자다: **모든 소비자 번들에서 약 10.4 kB(minified) / 5.9 kB(gzip) 감소.**

**(b) lodash 부분만 분리** — `src/`가 실제로 쓰는 38개 함수만으로 만든 합성 번들, `lodash-es` 서브패스 import vs `es-toolkit/compat`.

|                             | minified               | gzip                  |
| --------------------------- | ---------------------- | --------------------- |
| `lodash-es` (서브패스 38개) | 31,184 B               | 11,555 B              |
| `es-toolkit/compat`         | 20,721 B               | 6,353 B               |
| **차이**                    | **−10,463 B (−33.6%)** | **−5,202 B (−45.0%)** |

두 측정이 일치한다(minified −10,463 vs −10,681). 절감분이 빌드 노이즈가 아니라 실제 lodash 부분임을 교차 확인해 준다.

**(c) 디스크 사용량 — 유일한 후퇴.** `lodash` 4.9 MB + `lodash-es` 2.6 MB = 7.5 MB 대비, `es-toolkit`은 압축 해제 기준 16 MB(여러 빌드 포맷을 함께 배포). `node_modules`는 커지고 배포 바이트는 줄어든다. 숨기지 말고 명시할 사항.

---

## Stage 5 — 리포트

### 점수: 78 / 100 — 권장

**높게 나온 이유**

- 끝까지 검증됨: 마이그레이션 후 전체 빌드(18개 프로젝트)와 전체 테스트(**9,684개**)가 통과하며 동작 변화 없음.
- lodash가 배포 패키지의 `dependencies`에 있음 — 지금 모든 소비자가 비용을 지불 중.
- 실측 절감: core+validator+utils 번들에서 **약 10.4 kB(min) / 5.9 kB(gzip)**, lodash 부분만 보면 **gzip −45%**.
- 하드 블로커 0. 38개 함수 전부 `es-toolkit/compat`가 커버.
- **빌드 단순화가 오히려 더 큰 이득**: `lodashReplacer` tsc-alias 플러그인, `tsconfig.replacer.json` 6개, `compileReplacer` 빌드 스텝 6개, 7개 패키지의 `lodash` + `lodash-es` 이중 의존성 — 전부 lodash를 두 모듈 시스템에서 쓰려고 존재한다. es-toolkit은 ESM/CJS 듀얼 + 타입 내장이라 이 전부를 삭제 가능.
- 활발한 저장소, 매주 외부 PR 머지, **CLA 없음**, 우회해야 할 실패한 선행 시도 없음.

**90점대가 아닌 이유**

- **범위**: 9개 패키지, 101개 파일, 184개 import. 기계적이지만 리뷰 부담이 큰 diff이고, 프로젝트에서 가장 민감한 `@rjsf/core`와 `@rjsf/utils`를 건드린다.
- **이미 서브패스 import가 지배적**(179/184). 지금도 lodash를 과다 배포하고 있지 않으므로 바이트 이득이 실재하되 극적이지는 않다 — 현실적인 앱 번들 기준 2.7%.
- **전이 lodash 잔존**: `semantic-ui-react`, `@fluentui/*` 경유로 `@rjsf/semantic-ui`·`@rjsf/fluentui-rc`는 계속 lodash를 갖는다. "rjsf에서 lodash 제거"는 `core` / `utils` / `validator-*`에 한해서만 참이다.
- **`node_modules` 증가**: 압축 해제 기준 7.5 MB → 16 MB.
- 널리 쓰이는 라이브러리인 만큼, 메인테이너는 의존성 교체를 다운스트림 리스크와 저울질할 합당한 이유가 있다.

**권장 접근:** 101개 파일 단일 PR 대신 단계적 PR로 분할. `@rjsf/utils` 먼저(58개 파일, 가장 크고 독립적이며 테스트 커버리지 100%가 안전망), 이어서 `@rjsf/core`, 그다음 validator들, 마지막에 테마들.
