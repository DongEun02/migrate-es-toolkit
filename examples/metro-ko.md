# can-migrate-es-toolkit — `react/metro`

```
/can-migrate-es-toolkit https://github.com/react/metro ko
```

**분석일:** 2026-08-09 · **저장소 상태:** `main` @ 0.87.0 (최종 푸시 2026-08-08)

## 결론: 15 / 100 — 마이그레이션하지 말 것

**Metro는 자기 자신이 번들링되지 않는 Node.js 번들러다. 따라서 바이트 절감은 받을 사람이 없고, 대신 es-toolkit이 모든 설치에 3.7 MB를 더한다.**

**이슈도 PR도 열지 말 것.** "아마 별로일 것 같다"가 아니라, 주장할 근거 자체가 없다. 동일한 제안이 이미 [PR #1534](https://github.com/react/metro/pull/1534)로 올라왔다가 타당하게 거절되었고, 그 이후의 모든 측정치는 반대 방향으로 더 기울었다.

변경 자체는 사소하고 검증도 완벽히 통과한다(5파일 diff에 테스트 2,542개, Flow, 전체 빌드 모두 그린). 그건 실행 근거가 되지 못한다. 순가치가 음수인 변경을 완벽하게 만들어도 결과는 여전히 음수다.

---

## 1단계 — 마이그레이션 게이트

`package.json` 20개 스캔(Yarn v1 워크스페이스). 그중 2개에서 lodash 발견.

| 패키지 | 패키지명 | 위치 |
| ------ | -------- | ---- |
| `metro` | `lodash.throttle@^4.1.1` | `dependencies` |
| `metro-core` | `lodash.throttle@^4.1.1` | `dependencies` |

`lodash`, `lodash-es`, `@types/lodash` 모두 없음. 단일 메서드 패키지 `lodash.throttle` 하나뿐.

**→ 2단계로 진행.**

---

## 2단계 — 마이그레이션 대상 판단

### 2-1. 프로젝트 성격

**빌드 도구 / Node.js 런타임.** Metro는 React Native의 JavaScript 번들러다. CLI + Node API 형태이며 약 20개 npm 패키지(`metro`, `metro-core`, `metro-resolver` 등)로 배포된다. 모든 패키지가 `main: "src/index.js"`와 `exports` 맵을 선언하고 npm에 배포된다.

`"engines": { "node": "^22.13.0 || ^24.3.0 || >= 26.0.0" }` — Node 전용, 브라우저 타깃 없음.

**이 사실 하나가 분석 전체를 결정한다.** Metro의 코드는 사용자의 브라우저 번들에 절대 들어가지 않는다. Metro는 번들을 *만드는* 쪽이지 번들 *안에* 사는 쪽이 아니다. 따라서 es-toolkit의 표준 논거인 "사용자가 내려받는 바이트가 줄어든다"는 주장은 여기서는 수신자가 없다. Metro에서 의미를 갖는 유일한 크기 지표는 **설치 용량**이고, 하필 그 지표에서 es-toolkit이 진다(4-3 참고).

**플러그인 노출: 없음.** `throttle`은 생성자 두 곳에서 내부적으로만 쓰인다. 재export되지 않으며 공개 API 표면에도 등장하지 않는다(`scripts/generateApiSnapshots.js`의 검증된 API 스냅샷 14개로 확인).

### 2-2. lodash가 배포 산출물에 포함되는가

**런타임 `dependency`로 배포되지만, 번들링되지는 않는다.** `npm i metro@0.87.0 --omit=dev`로 새로 설치하면 lodash 계열은 정확히 하나만 딸려온다.

```
node_modules/lodash.throttle
```

**전이 의존 lodash: 전부 개발용.** `yarn.lock`의 나머지 lodash는 모두 빌드/린트 도구 소유이며 프로덕션 트리에는 없다.

| 패키지 | 끌어오는 주체 |
| ------ | ------------- |
| `lodash@~4.17.15` | `@microsoft/api-extractor` |
| `lodash@^4.17.14` | `async` (→ `babel-plugin-tester`) |
| `lodash@^4.17.21` | `eslint-plugin-ft-flow` |
| `lodash.merge` | `eslint` |
| `lodash.mergewith` | `babel-plugin-tester` |
| `lodash.debounce` | `@babel/helper-define-polyfill-provider` |

즉 마이그레이션하면 Metro의 **프로덕션** 의존성 트리는 실제로 lodash-free가 된다. 매우 작지만 진짜 성과이고, 이 마이그레이션을 옹호할 수 있는 가장 강한 근거다.

### 2-3. import 패턴과 범위

| 패턴 | 개수 | 번들 영향 |
| ---- | ---- | --------- |
| 전체 import (`import _ from 'lodash'`) | 0 | — |
| 명명 import | 0 | — |
| **단일 메서드 패키지 (`import throttle from 'lodash.throttle'`)** | **2** | 이미 최적화 한계 |

**파일 2개, import 2개, 고유 함수 1개.**

| 파일 | 라인 | 사용 |
| ---- | ---- | ---- |
| [`packages/metro/src/lib/TerminalReporter.js`](https://github.com/react/metro/blob/main/packages/metro/src/lib/TerminalReporter.js#L21) | 107 | `throttle(data => …, 100)` — 번들 진행률 업데이트 |
| [`packages/metro-core/src/Terminal.js`](https://github.com/react/metro/blob/main/packages/metro-core/src/Terminal.js#L15) | 116 | `throttle(status => …, 3500)` — 비 TTY 상태 출력, 163번 줄에서 `.flush()` 호출 |

두 호출부 모두 `{leading, trailing}` 옵션을 넘기지 않는다. 한 곳이 `.flush()` 메서드에 의존한다.

`lodash.throttle` 같은 단일 메서드 패키지는 lodash 사용이 취할 수 있는 *가장* 최적화된 형태다. 의존성 0개짜리 독립 16 KB 패키지이므로 트리셰이킹으로 더 걷어낼 것이 애초에 남아 있지 않다.

### 2-4. 하드 블로커

`sortedUniq`, `sortedUniqBy`, `mixin`, `noConflict`, `runInContext` — **없음.** `lodash/fp` 사용도 없음.

### 2단계 요약

```
저장소: react/metro
2-1 (성격):   빌드 도구 / Node.js 런타임 (배포 패키지 20개) — 플러그인 노출: 없음
2-2 (배포):   런타임 의존성이지만 Node 전용 — 소비자 번들에 절대 들어가지 않음
              전이 lodash: 개발 도구에만 존재 (eslint, api-extractor, babel)
2-3 (import): 전체 ×0 / 명명 ×0 / 단일메서드 ×2 — 파일: 2 — 함수: throttle
2-4 (블로커): 없음

2단계 판정: 기술적으로는 마이그레이션 가능 — 단 번들 크기 논거는 성립하지 않음
```

---

## 3단계 — 조직적 신호

| 신호 | 확인 결과 |
| ---- | --------- |
| **활동성** | 매우 활발. 최종 푸시 2026-08-08, 최종 커밋 2026-08-06(`Deploy 0.326.0 to xplat`). 스타 5,621개, 열린 이슈 458개. Meta 내부 우선 개발 후 GitHub로 동기화. |
| **선행 사례** | 🔴 **[PR #1534 — "Replace lodash.throttle with es-toolkit's throttle"](https://github.com/react/metro/pull/1534). 2025-07-16 생성, 2025-07-17 종료 — 24시간 이내 거절.** |
| **CLA** | 🔴 **필수.** Meta CLA(`CONTRIBUTING.md` 7항, `code.facebook.com/cla`), `facebook-github-bot`이 강제. PR #1534도 즉시 CLA에 막혔다. |
| **공개 API의 lodash** | 없음. |

### PR #1534 — 무슨 일이 있었고 왜 중요한가

이건 "흐지부지된 이전 시도"가 아니다. 동일한 변경을, es-toolkit 메인테이너가 직접 제안했고, 내용을 근거로 거절당했다.

**@vzaidman**(메인테이너):

> Hey! Thanks for your contribution. This would have too little benefits / impact for us to replace the well tested and highly reliable and secure lodash.
>
> (기여 감사합니다. 다만 충분히 검증되고 신뢰성·보안이 확보된 lodash를 교체하기에는 이득/영향이 너무 작습니다.)

**@robhogan**(메인테이너) — 실질적 반박:

> ```
> $ gdu -sh --apparent-size node_modules/es-toolkit node_modules/lodash node_modules/lodash.throttle
> 2.5M    node_modules/es-toolkit
> 1.4M    node_modules/lodash
> 17K     node_modules/lodash.throttle
> ```
>
> Metro is a Node.js application, so install size would be the only relevant size consideration (though not a particularly important one). `es-toolkit` is actually larger than `lodash`, let alone `lodash.throttle`, which is the package you're proposing to replace. It'd be different if we included `lodash` in bundler output, but we don't.
>
> Besides that, we do tend to be cautious about accepting PRs from folks promoting their own packages, especially when they don't mention their affiliation.
>
> (Metro는 Node.js 애플리케이션이므로 크기 관점에서 유일하게 유의미한 건 설치 용량입니다. es-toolkit은 lodash보다도, 하물며 교체 대상인 lodash.throttle보다는 훨씬 큽니다. 번들러 출력물에 lodash를 포함시켰다면 이야기가 달랐겠지만 그렇지 않습니다. 덧붙여, 본인이 만든 패키지를 홍보하는 PR은 — 특히 소속을 밝히지 않은 경우 — 신중하게 봅니다.)

제안자(**@raon0211**, es-toolkit 작성자)는 결론을 받아들였다.

> Thank you for the clear feedback and explaining the reasoning! ❤️

여기서 세 가지가 따라온다.

1. **메인테이너의 기술적 판단이 맞다.** 2-1의 결론과 정확히 같은 지점을 독립적으로 짚었다. Metro는 번들링되지 않으므로 설치 용량만 의미가 있고, 설치 용량에서 es-toolkit은 퇴보다.
2. **그들의 반대 근거는 약해진 게 아니라 강해졌다.** 2025년 7월 시점에 es-toolkit을 2.5 MB로 측정했다. 현재(v1.50.0)는 **apparent 3.70 MB / 디스크 16 MB**다. 이미 거절당한 크기의 약 1.5배이고, 실제 디스크 블록 기준으로는 16 MB다.
3. **소속 미고지에 대한 명시적 우려가 기록되어 있다.** 새로운 근거 없이, 특히 es-toolkit과 연관된 사람이 이 제안을 다시 꺼내면 같은 영업을 두 번 하는 것으로 읽힌다.

---

## 4단계 — 검증 및 측정

격리된 클론에서 **Tier 2**(전체 빌드 + 전체 테스트 + Flow 타입체크)까지 수행.

이렇게 작은 저장소에 Tier 2까지 돌린 이유는 마이그레이션을 정당화하기 위해서가 아니다. 낮은 점수가 "위험해 보여서"라는 검증 안 된 추측이 아니라 *비용 쪽*을 정직하게 반영한 결과임을 확인하기 위해서다. 이 변경은 위험하지 않다. 다만 할 가치가 없을 뿐이다.

### 4-1. 적용한 변경

이 분석을 수행한 시점에는 번들된 코드모드가 단일 메서드 패키지(`lodash.throttle`)를 인식하지 못해 Tier 0이 `No lodash usage found in shipped source.`를 반환했고, 변경은 수동으로 적용했다. **이 결함은 이후 수정되었다** — `measure_bundle_size.py`와 `migrate_lodash_imports.py`가 이제 `lodash.<fn>` 패키지를 탐지하고, 전부 소문자인 이름을 정규 표기로 복원하며, 설치 용량을 함께 보고한다. 수정된 스크립트를 깨끗한 클론에 다시 돌리면 import 2건을 모두 찾아내고 용량 퇴보를 경고한다.

```diff
- // $FlowFixMe[untyped-import] lodash.throttle
- import throttle from 'lodash.throttle';
+ // $FlowFixMe[untyped-import] es-toolkit
+ import {throttle} from 'es-toolkit';
```

두 매니페스트에서 `lodash.throttle` → `es-toolkit@^1.50.0` 교체.

`es-toolkit/compat`이 아니라 `es-toolkit` 메인 엔트리를 썼다. 여기서는 메인 엔트리로 충분하며(4-2에서 검증), compat은 바이트만 더 늘린다.

코드모드가 놓쳤을 수동 수정 2건:

1. **default → named import.** `lodash.throttle`은 CJS default를 export하지만 `es-toolkit`은 `throttle`을 named export한다. `import throttle from 'es-toolkit'`으로 두면 네임스페이스 객체 전체가 바인딩되어 import 시점이 아니라 호출 시점에 터진다.
2. **Flow suppression을 유지하되 대상을 바꿔야 한다.** Metro는 Flow 코드베이스다. es-toolkit은 TypeScript 타입을 제공하고 Flow 타입은 없으므로 `$FlowFixMe[untyped-import]`가 여전히 필요하다. 게다가 Metro는 *사용되지 않는* suppression도 오류로 잡기 때문에, 지워도 `flow check`가 깨진다. `Terminal.js`는 원래 suppression이 없었는데(저장소에 `lodash.throttle`용 `flow-typed` libdef가 있었다) 새로 추가해야 했다.

### 4-2. 동작 동등성 검증

Metro의 사용 형태는 기본 edges의 `throttle(fn, ms)` + `.flush()`다. 세 구현을 그 형태 그대로 비교:

| 구현 | `.flush` | `.cancel` | 동기 3회 호출 | `.flush()` 후 | 250ms 후 |
| ---- | -------- | --------- | ------------- | ------------- | -------- |
| `lodash.throttle` | ✅ | ✅ | `["a"]` | `["a","c"]` | `["a","c"]` |
| `es-toolkit` | ✅ | ✅ | `["a"]` | `["a","c"]` | `["a","c"]` |
| `es-toolkit/compat` | ✅ | ✅ | `["a"]` | `["a","c"]` | `["a","c"]` |

**세 구현 모두 동작이 완전히 동일.** `es-toolkit` 메인 엔트리가 leading edge 발화, trailing 병합, `.flush()` 의미론 모두에서 lodash와 일치하므로 더 무거운 `compat`은 불필요하다.

### 4-3. 테스트 / 타입체크 / 빌드

| 검사 | 변경 전 | 변경 후 |
| ---- | ------- | ------- |
| `jest --ci` (모노레포 전체) | 140 스위트, **2,542 통과**, 14 스킵, 스냅샷 510 | 140 스위트, **2,542 통과**, 14 스킵, 스냅샷 510 |
| `flow check` (1,050 파일) | No errors | **No errors** |
| `yarn run build` (전체 패키지) | OK | **OK** |
| 수정 파일 2개 `eslint` | clean | clean |
| API 스냅샷 | 14개 검증 | 14개 검증 |

**회귀 0건, 동작 차이 0건.** diff 크기: **5개 파일 변경, +14 / −13**(`yarn.lock` 포함).

마이그레이션이 이보다 깔끔하기는 어렵다.

### 4-4. 크기 — 여기서 무너진다

**(a) `throttle` 단독 합성 번들** — `esbuild --bundle --minify --format=esm`:

| | minified | gzip |
| --- | --- | --- |
| `lodash.throttle` | 2,504 B | 1,210 B |
| `es-toolkit` | 844 B | 435 B |
| `es-toolkit/compat` | 1,054 B | 544 B |
| **차이(메인 엔트리)** | **−1,660 B (−66.3%)** | **−775 B (−64.0%)** |

−66%는 실제 수치이고, PR #1534가 인용한 것과 같은 숫자다. **그리고 여기서는 무의미하다.** Metro는 브라우저용으로 번들링·minify되지 않는다. 다운스트림 누구도 이 2,504바이트를 다운로드 비용으로 지불하지 않는다. 이 행은 Metro 사용자가 회수할 수 없는 절감량을 재고 있다.

**(b) 설치 용량 — 실제로 적용되는 지표:**

| | tarball | 압축 해제(apparent) | 디스크 |
| --- | --- | --- | --- |
| `lodash.throttle@4.1.1` | 5,554 B | **16,478 B (16.1 KB)** | 28 KB |
| `es-toolkit@1.50.0` | 473,418 B | **3,879,844 B (3.70 MB)** | 16 MB |
| **차이** | **+467,864 B (85배)** | **+3.68 MB (235배)** | **+16 MB** |

es-toolkit의 덩치는 다중 포맷 출력물에서 온다. `dist/` 11 MB, `compat/` 4.6 MB. Metro는 그중 함수 하나를 쓴다.

**(c) Metro 실제 프로덕션 트리 기준:**

```
npm i metro@0.87.0 --omit=dev   →   25,977,316 B  (24.8 MB)
  lodash.throttle 비중                  16,478 B  (0.063%)

마이그레이션 후                  →   29,840,682 B  (28.5 MB, +14.9%)
```

**함수 하나의 구현을 바꾸자고 모든 React Native 개발자의 `node_modules`를 약 15% 키우는 셈이다.** 거래 조건은 이렇다. 아무도 다운로드하지 않는 1.6 kB를 아끼고, 모두가 설치하는 3.7 MB를 지불한다.

*(의존성 개수는 무승부 — 두 패키지 모두 전이 의존성 0개.)*

---

## 5단계 — 리포트

### 점수: 15 / 100 — 마이그레이션하지 말 것

**마이그레이션이 실제로 주는 것**

- Metro 프로덕션 의존성 트리가 lodash-free가 된다(런타임 lodash 패키지 1개 중 1개 제거).
- `throttle` 구현이 바이트 기준 66% 작고 활발히 유지보수된다. `lodash.throttle`은 2016년 이후 릴리스가 없다.
- 위험 0 검증 완료: 5파일 diff에 테스트 2,542개, Flow, 전체 빌드 모두 그린.

**그것으로 부족한 이유**

| 감점 | 사유 |
| ---- | ---- |
| **−45** | **번들 크기 논거가 성립하지 않는다.** Metro는 번들링되는 코드가 아니라 Node.js 번들러다. es-toolkit의 핵심 이점이 사용자에게 도달할 경로 자체가 없다. 66% 절감은 회수 불가능하다. |
| **−25** | **설치 용량이 크게 퇴보한다.** 함수 하나에 apparent +3.68 MB(235배), Metro 프로덕션 트리 전체 기준 +14.9%. Node 도구에 적용되는 *유일한* 크기 지표에서 이 마이그레이션은 상황을 악화시킨다. |
| **−10** | **이미 제안되어 거절됨**([#1534](https://github.com/react/metro/pull/1534)). 그 근거는 타당했고, es-toolkit이 두 배로 커지면서 오히려 강화되었다. 이후 새로운 근거는 없으며, 이번 분석도 만들어내지 못했다. |
| **−5** | **Meta CLA 필수**, 더해 es-toolkit 관련 PR에 대한 메인테이너의 명시적 경계심. |

**정직한 요약:** 하지 말아야 할 마이그레이션을 흠결 없이 해낸 사례다. 범위는 2파일, 위험은 0, 검증은 완벽하다. 하지만 순가치가 음수인 변경을 완벽히 수행해도 결과는 여전히 음수다. `lodash.throttle`은 *이미* 최적 형태에 도달한 드문 lodash 의존성이다. 17 KB, 의존성 0, 함수 1개, 동결되었고 충분히 검증됨. Node.js 도구에서 유일하게 의미 있는 축에서 es-toolkit은 이를 이길 수 없다.

**권고: 이슈도 PR도 열지 말 것.** 메인테이너가 이미 답했고, 그 답은 기술적으로 옳았으며, 사실관계는 그들 쪽으로 더 기울었다.

---

## 6단계 — 이슈 초안

**작성하지 않음.** 점수 15로 70 미만이고, "그래도 가치가 있는 경우" 예외에도 해당하지 않는다.

6단계는 메인테이너가 받아서 반가울 제안을 쓰기 위해 존재한다. 여기서는 메인테이너가 이미 그 제안을 받았고, 24시간 안에 검토했고, 거절 이유를 정확히 설명했다. 그리고 동원 가능한 가장 강력한 반대 근거(위 크기 측정치)는 제안이 아니라 *그들의* 입장을 뒷받침한다. 다시 제출하는 건 이미 올바르게 결론난 사안을 재론하는 일이다.

### 상황이 바뀐다면

이 결론은 Metro의 특성이 아니라 es-toolkit의 설치 용량에 달려 있다. 다음 중 하나가 성립하면 재검토할 가치가 있다.

- **es-toolkit이 슬림 배포본을 제공하는 경우** — 3.7 MB가 아니라 수십 KB로 설치되는 Node용 엔트리 포인트. 이것이 유일한 블로커이며, 마이그레이션의 나머지 요소는 이미 전부 그린이다.
- **Metro의 lodash 사용이 함수 하나를 넘어 늘어나거나**, Metro가 번들 출력물에 자기 코드를 싣기 시작하는 경우. 둘 다 예정에 없다.

그 전까지 올바른 행동은 아무것도 하지 않는 것이다.

---

## 부록 — 재현 방법

```bash
git clone --depth 1 https://github.com/react/metro.git && cd metro
yarn install --frozen-lockfile
npx jest --ci                                   # 기준선: 2,542 통과

# 적용: TerminalReporter.js + Terminal.js에서 lodash.throttle → es-toolkit,
#       packages/metro/package.json + packages/metro-core/package.json 의존성 교체
yarn install
npx jest --ci                                   # 2,542 통과 — 동일
npx flow check                                  # No errors!
yarn run build                                  # 전체 패키지 OK

# 설치 용량
npm i metro@0.87.0 --omit=dev                   # 24.8 MB
npm pack es-toolkit@1.50.0 lodash.throttle@4.1.1  # 473,418 B vs 5,554 B
```

**저장소 URL 참고:** `facebook/metro`는 현재 **`react/metro`**로 리다이렉트된다(조직 이전). `git clone`과 GitHub API 모두 리다이렉트를 따라가지만, API 호출은 `curl -L`이 필요하다(그냥 호출하면 `301 Moved Permanently` 반환).
