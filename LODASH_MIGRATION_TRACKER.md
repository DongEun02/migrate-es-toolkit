# Lodash → es-toolkit 후보 검토 체크리스트

조사 기준일: **2026-09-04** · npm 다운로드 집계: **2026-08-23~2026-08-29** · 등록 후보: **336개 npm 패키지**

이 파일 하나에 조사 근거와 후속 검토 기록을 함께 보관한다. 인기 조건 충족은 마이그레이션 타당성을 뜻하지 않는다. 실제 검토는 이 저장소의 [README 절차](README.md)에 따른다.

## 진행 상황을 기록하는 방법

패키지당 체크박스는 하나다. **체크는 해당 패키지의 검토가 종료되었다는 뜻이며, 코드 변경 완료나 PR 병합을 뜻하지 않는다.** 마이그레이션을 제안하기로 결정한 경우와 근거를 남기고 대상에서 제외한 경우 모두 검토를 종료할 수 있다.

1. 항목의 `상태`를 `진행 중`으로 바꾸고 `담당`, `최근 작업일`, `현재 재확인`을 채운다.
2. 아래 단계에 따라 검토하며 `검증 단계`, `점수`, `메모·다음 행동`을 갱신한다. 기다려야 하면 `대기`와 사유를 기록한다.
3. 검토가 끝나면 `판정`을 `제안` 또는 `제외`로 정하고 `결과·이슈·PR`에 보고서 링크 또는 구체적인 결론·근거를 남긴다. 이슈·PR을 반드시 만들 필요는 없다.
4. `상태: 종료`로 바꾸고 해당 패키지의 `[ ]`를 `[x]`로 체크한다. 실제 코드 이관·PR 제출·병합 여부는 `실제 이관 결과`에 따로 기록한다.
5. 같은 저장소를 함께 검토하면 `공동 작업`에 대표 항목 ID를 적고 결과를 연결한다. 각 패키지의 판정은 별도로 확인한다. 항목을 재정렬해도 `L001` 같은 ID는 바꾸지 않는다.

| 필드 | 기록할 값 |
|---|---|
| 상태 | `미착수` / `진행 중` / `대기` / `종료` |
| 판정 | `미정` / `제안` / `제외` / `추가 조사` — 종료할 때는 제안 또는 제외 |
| 검증 단계 | `미수행` / `Gate` / `대상성 판단` / `Tier 0` / `Tier 1` / `Tier 2` |
| 점수 | `미정` 또는 점수와 잠정/확정 구분. Tier 0–1만으로 확정 점수 70 이상을 부여하지 않음 |
| 현재 재확인 | 작업일 / 현재 버전 또는 커밋 / 직접 선언 및 실제 사용 확인 / 근거 링크 |
| 실제 이관 결과 | 미실행, 변경 검증, PR 제출, 병합, 릴리스 등 실제 도달 결과와 링크 |

등록할 때의 상태는 **미착수 336개 / 검토 종료 0개**다. 이 숫자는 시작 기록이며 현재 진행률이 아니다. 현재 진행률은 아래 명령이 이 파일의 체크박스와 상태에서 직접 계산한다. 별도 파일 생성이나 패키지 설치는 없다.

```bash
python3 - ~/migrate-es-toolkit/LODASH_MIGRATION_TRACKER.md <<'PY'
from pathlib import Path
from collections import Counter
import re
import sys

path = Path(sys.argv[1]).expanduser()
text = path.read_text(encoding="utf-8")
pattern = r"(?ms)^- \[(?P<done>[ xX])\] \*\*\[(?P<id>L\d{3})\] (?P<name>.+?)\*\*\n(?P<body>.*?)(?=^- \[[ xX]\] \*\*\[L\d{3}\] |\Z)"
items = list(re.finditer(pattern, text))
if not items:
    raise SystemExit("추적 항목을 찾지 못했습니다. 체크박스와 L번호 형식을 확인하세요.")

def field(item, label):
    found = re.search(r"^  - " + re.escape(label) + r": (.+)$", item["body"], re.M)
    return found.group(1).strip() if found else "누락"

closed = [item for item in items if item["done"].lower() == "x"]
states = Counter(field(item, "상태") for item in items)
verdicts = Counter(field(item, "판정") for item in closed)
print(f"검토 종료: {len(closed)}/{len(items)} ({len(closed) / len(items):.1%})")
print("상태: " + ", ".join(f"{key} {states[key]}" for key in ["미착수", "진행 중", "대기", "종료"]))
print("종료 판정: " + (", ".join(f"{key} {value}" for key, value in verdicts.items()) or "없음"))
print("※ 검토 종료율입니다. 실제 마이그레이션·PR 병합률이 아닙니다.")

issues = []
seen = set()
for item in items:
    ident = item["id"]
    checked = item["done"].lower() == "x"
    state = field(item, "상태")
    verdict = field(item, "판정")
    if ident in seen:
        issues.append(f"{ident}: 중복 ID")
    seen.add(ident)
    if state not in {"미착수", "진행 중", "대기", "종료"}:
        issues.append(f"{ident}: 허용되지 않은 상태 '{state}'")
    if checked != (state == "종료"):
        issues.append(f"{ident}: 체크박스와 상태 불일치")
    if verdict not in {"미정", "제안", "제외", "추가 조사"}:
        issues.append(f"{ident}: 허용되지 않은 판정 '{verdict}'")
    if checked and verdict not in {"제안", "제외"}:
        issues.append(f"{ident}: 종료 판정은 제안 또는 제외로 기록")
    if checked and field(item, "결과·이슈·PR") in {"—", "누락"}:
        issues.append(f"{ident}: 종료 근거 또는 결과 링크 누락")
    if state == "대기" and field(item, "메모·다음 행동") in {"—", "누락"}:
        issues.append(f"{ident}: 대기 사유와 다음 행동 누락")
    if state in {"진행 중", "대기"}:
        print(f"  {ident} {item['name']} | {state} | {field(item, '메모·다음 행동')}")
if issues:
    print("확인 필요:")
    for issue in issues:
        print("- " + issue)
else:
    print("기록 정합성: 정상")
PY
```

## 공통 검토 순서

1. **기존 결과와 현재 Gate 확인:** 같은 저장소의 기존 보고서를 먼저 읽고 현재 `package.json`과 코드 사용을 확인한다. 아래 고정 버전 링크는 조사 당시 증거이므로 현재 상태로 덮어쓰지 않는다. 현재 Lodash가 제거되었다면 새 근거를 남기고 제외할 수 있다.
2. **대상성 판단:** 코드가 브라우저 번들에 포함되는지, 공개 API·타입에 노출되는지, 전이 의존성 때문에 Lodash가 남는지, 실제 이익을 받는 사용자가 누구인지 확인한다. 근거가 없으면 이 단계에서 종료할 수 있다.
3. **조직 신호 및 Tier 0–1:** 활동성·기존 제안·기여 규칙을 확인하고 필요한 합성 측정과 codemod 형태를 기록한다. Node 전용 프로젝트에 브라우저 번들 절감 수치를 이점으로 적용하지 않는다.
4. **조건을 만족할 때만 Tier 2:** 잠정 점수 70 이상이며 실제 제안을 진행할 의도가 있는 후보에 대해 기준 빌드와 변경 후 빌드·테스트·배포 산출물을 비교한다. 조기 제외 후보에는 전체 설치·테스트를 강제하지 않는다.
5. **결론 기록:** 판단 근거, 측정 한계, 점수, 다음 행동을 기록한다. Tiers 0–1만으로 종료한 제안은 미검증이라는 점을 명확히 한다.

Codex에서 개별 저장소 검토를 시작할 때 사용할 기존 스킬 호출 형식:

```text
$can-migrate-es-toolkit https://github.com/OWNER/REPO ko
```

기존 분석 예시: [Metro](examples/metro-ko.md), [react-jsonschema-form](examples/react-jsonschema-form-ko.md). 두 문서는 2026-08-09 기준 예시다. 아래 해당 항목에 연결했으며, 예시가 있다는 이유로 현재 검토를 완료 처리하지 않았다.

## 조사 요약과 집계 한계

| 항목 | 조사 결과 |
|---|---:|
| 조회 후보 | 2,641개 |
| 최신 배포 정보를 확인한 패키지 | 2,446개 |
| Lodash 계열 자체를 제외한 직접 선언 확인 | 1,794개 |
| 이 파일에 등록한 조건 충족 패키지 | 336개 |
| 일반 의존성 선언 | 306개 |
| 개발 의존성만 선언 | 30개 |
| 주간 다운로드 100,000회 이상으로 통과 | 266개 |
| 스타 3,000개 이상으로 추가 | 70개 |
| 연결된 저장소 URL의 고유 수 | 281개 |
| 저장소 URL을 확인하지 못한 패키지 | 2개 |

공식 npm 페이지의 검색 노출 캐시에서는 `lodash` 하나의 Dependents가 **197,414개(약 19.7만)**로 관측되었다. [npm 집계 근거](https://www.npmjs.com/package/lodash?activeTab=versions). 이는 전세계 비공개 프로젝트까지 포함한 총수나 현재 최신 소비 패키지만의 수가 아니다. 계열별 수치를 더하면 중복된다.

- 전체 전수목록이 아니라, 공개 후보 조사에서 조건 충족을 확인한 npm 패키지 목록입니다.
- 대상: lodash, lodash-es, @types/lodash, @types/lodash-es, lodash.*, @types/lodash.*의 직접 선언. Lodash 계열 패키지 자체는 소비자 목록에서 제외했습니다.
- 라이브러리·프레임워크·개발 도구를 포함한 npm 패키지 단위입니다. 동일 모노레포의 여러 패키지는 각각 셉니다.
- 의존성은 조회 시점 npm latest 배포본에 선언된 dependencies/devDependencies/peerDependencies/optionalDependencies 기준입니다. 간접 의존성, lockfile만 있는 관계, 번들에 복사된 코드는 판정에 포함하지 않았습니다.
- 일반 의존성은 dependencies/peerDependencies/optionalDependencies 중 하나에 선언된 관계입니다. @types 선언 또는 peer/optional 선언은 런타임 실행에 항상 필요하다는 뜻이 아닙니다.
- 개발 의존성만은 조사 대상 이름이 devDependencies에만 선언된 경우입니다. npm 배포본에 devDependencies가 없더라도 저장소에서 개발용으로 쓰지 않는다는 뜻은 아닙니다.
- 조건: npm 주간 다운로드 100,000회 이상 또는 연결된 GitHub 저장소 스타 3,000개 이상. 미조회 숫자는 0이 아닌 빈칸입니다.
- 다운로드는 2026-08-23~2026-08-29 양끝 포함 7일, 패키지의 모든 버전 합계입니다. 최신 버전만의 사용량이나 이용자 수가 아닙니다.
- 스타는 저장소 단위이며 모노레포 패키지끼리 공유할 수 있습니다. GitHub API 또는 deps.dev 프로젝트 통계를 조회했으며 출처의 관측 시점은 데이터 JSON에 보존했습니다.
- npm 웹의 Dependents 수와 deps.dev 버전별 direct count는 집계 범위와 시점이 다릅니다. 최신 소비 패키지만의 개수가 아니며 계열별 숫자를 더하면 중복됩니다.
- 공개 색인의 directSample과 추가 주요 패키지를 후보로 사용했습니다. 샘플은 전수가 아니고 npm API 일부 요청이 제한되어, 전체 적격 패키지 수 또는 완전한 최신 개발 의존성 총수를 뜻하지 않습니다.

집계 숫자가 없는 항목은 `미조회`로 표시한다. 특히 다운로드 미조회 40개는 스타 조건으로 포함된 항목이다. 저장소 링크는 npm 메타데이터에 연결된 URL 기준이므로 작업을 시작할 때 공식 저장소와 모노레포 내 패키지 위치를 재확인한다.

### deps.dev에서 확인한 계열별 규모

아래 수치는 특정 대상 버전에 의존한다고 알려진 패키지의 수다. 과거 소비 버전도 포함되며, 중복을 제거한 최신 소비 패키지 총수가 아니다. [공식 집계 정의](https://docs.deps.dev/api/v3alpha/#getdependents)

| 대상 버전 | 직접 의존 패키지 수 | 근거 |
|---|---:|---|
| `lodash@4.18.1` | 175,859 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash/versions/4.18.1:dependents) |
| `lodash-es@4.18.1` | 17,741 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash-es/versions/4.18.1:dependents) |
| `@types/lodash@4.17.25` | 11,462 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/%40types%2Flodash/versions/4.17.25:dependents) |
| `@types/lodash-es@4.17.12` | 1,968 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/%40types%2Flodash-es/versions/4.17.12:dependents) |
| `lodash.merge@4.6.2` | 8,782 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.merge/versions/4.6.2:dependents) |
| `lodash.debounce@4.0.8` | 6,643 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.debounce/versions/4.0.8:dependents) |
| `lodash.isequal@4.5.0` | 5,235 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.isequal/versions/4.5.0:dependents) |
| `lodash.clonedeep@4.5.0` | 5,664 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.clonedeep/versions/4.5.0:dependents) |
| `lodash.get@4.4.2` | 6,334 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.get/versions/4.4.2:dependents) |
| `lodash.throttle@4.1.1` | 3,861 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.throttle/versions/4.1.1:dependents) |
| `lodash.memoize@4.1.2` | 1,831 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.memoize/versions/4.1.2:dependents) |
| `lodash.omit@4.18.0` | 1,513 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.omit/versions/4.18.0:dependents) |
| `lodash.pick@4.4.0` | 1,917 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.pick/versions/4.4.0:dependents) |
| `lodash.mergewith@4.6.2` | 1,340 | [API](https://api.deps.dev/v3alpha/systems/npm/packages/lodash.mergewith/versions/4.6.2:dependents) |

출처와 조사 방식: [npm Registry API](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md), [npm 다운로드 API](https://github.com/npm/registry/blob/main/docs/download-counts.md), [deps.dev 후보 조회](https://blog.deps.dev/enumerating-dependents/). 숫자는 2026-09-04 조사 스냅샷이며 자동 갱신되지 않는다.

## 같은 저장소의 후보

아래 그룹은 저장소 URL이 같은 후보다. 한 번의 조사나 PR로 함께 다룰 수 있으므로 시작 전에 대표 항목을 정한다. 각 항목의 직접 의존성과 판정까지 같다고 가정하지 않는다.

| 저장소 | 관련 항목 |
|---|---|
| [alibaba/hooks](https://github.com/alibaba/hooks) | [L097 · `ahooks`](#l097), [L290 · `@ahooksjs/use-request`](#l290) |
| [ant-design/ant-design-charts](https://github.com/ant-design/ant-design-charts) | [L165 · `@ant-design/plots`](#l165), [L205 · `@ant-design/charts`](#l205) |
| [ant-design/pro-components](https://github.com/ant-design/pro-components) | [L163 · `@ant-design/pro-utils`](#l163), [L166 · `@ant-design/pro-layout`](#l166), [L200 · `@ant-design/pro-form`](#l200), [L201 · `@ant-design/pro-field`](#l201), [L202 · `@ant-design/pro-table`](#l202) |
| [antvis/x6](https://github.com/antvis/x6) | [L238 · `@antv/x6`](#l238), [L254 · `@antv/x6-common`](#l254) |
| [babel/babel](https://github.com/babel/babel) | [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138) |
| [chakra-ui/panda](https://github.com/chakra-ui/panda) | [L298 · `@pandacss/core`](#l298), [L299 · `@pandacss/node`](#l299) |
| [feathersjs/feathers](https://github.com/feathersjs/feathers) | [L288 · `@feathersjs/authentication`](#l288), [L289 · `@feathersjs/authentication-jwt`](#l289) |
| [grpc/grpc-node](https://github.com/grpc/grpc-node) | [L001 · `@grpc/proto-loader`](#l001), [L233 · `grpc`](#l233) |
| [ianstormtaylor/slate](https://github.com/ianstormtaylor/slate) | [L044 · `slate-react`](#l044), [L324 · `slate`](#l324) |
| [import-js/eslint-plugin-import](https://github.com/import-js/eslint-plugin-import) | [L090 · `eslint-import-resolver-webpack`](#l090), [L309 · `eslint-plugin-import`](#l309) |
| [mattallty/Caporal.js](https://github.com/mattallty/Caporal.js) | [L243 · `caporal`](#l243), [L255 · `@caporal/core`](#l255) |
| [Milkdown/milkdown](https://github.com/Milkdown/milkdown) | [L144 · `@milkdown/plugin-listener`](#l144), [L147 · `@milkdown/plugin-slash`](#l147), [L148 · `@milkdown/plugin-tooltip`](#l148), [L149 · `@milkdown/components`](#l149), [L150 · `@milkdown/plugin-block`](#l150), [L294 · `@milkdown/crepe`](#l294) |
| [nuxt/nuxt](https://github.com/nuxt/nuxt) | [L208 · `@nuxt/utils`](#l208), [L213 · `@nuxt/config`](#l213), [L214 · `@nuxt/vue-renderer`](#l214), [L215 · `@nuxt/core`](#l215), [L216 · `@nuxt/webpack`](#l216), [L217 · `@nuxt/builder`](#l217), [L336 · `@nuxt/kit-edge`](#l336) |
| [open-telemetry/opentelemetry-js](https://github.com/open-telemetry/opentelemetry-js) | [L304 · `@opentelemetry/metrics`](#l304), [L305 · `@opentelemetry/sdk-metrics-base`](#l305), [L306 · `@opentelemetry/tracing`](#l306) |
| [plouc/nivo](https://github.com/plouc/nivo) | [L069 · `@nivo/core`](#l069), [L263 · `nivo`](#l263) |
| [react/metro](https://github.com/react/metro) | [L006 · `metro-core`](#l006), [L007 · `metro`](#l007) |
| [reduxjs/redux-devtools](https://github.com/reduxjs/redux-devtools) | [L033 · `react-base16-styling`](#l033), [L095 · `react-json-tree`](#l095), [L237 · `react-dock`](#l237), [L253 · `redux-devtools-log-monitor`](#l253), [L291 · `@redux-devtools/log-monitor`](#l291) |
| [rjsf-team/react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form) | [L081 · `@rjsf/utils`](#l081), [L086 · `@rjsf/core`](#l086), [L093 · `@rjsf/validator-ajv8`](#l093) |
| [sequelize/sequelize](https://github.com/sequelize/sequelize) | [L042 · `sequelize`](#l042), [L279 · `@sequelize/utils`](#l279) |
| [transloadit/uppy](https://github.com/transloadit/uppy) | [L274 · `@uppy/core`](#l274), [L275 · `@uppy/dashboard`](#l275), [L276 · `@uppy/golden-retriever`](#l276), [L277 · `@uppy/utils`](#l277) |
| [umijs/dumi](https://github.com/umijs/dumi) | [L246 · `dumi`](#l246), [L260 · `dumi-theme-default`](#l260), [L303 · `@umijs/preset-dumi`](#l303) |
| [vuejs/vue-cli](https://github.com/vuejs/vue-cli) | [L280 · `@vue/cli`](#l280), [L281 · `@vue/cli-service`](#l281), [L282 · `@vue/cli-ui`](#l282) |
| [vuejs/vuepress](https://github.com/vuejs/vuepress) | [L285 · `@vuepress/plugin-active-header-links`](#l285), [L286 · `@vuepress/plugin-back-to-top`](#l286) |

## 일반 의존성 선언 — 306개

<a id="l001"></a>

- [ ] **[L001] `@grpc/proto-loader`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [grpc/grpc-node](https://github.com/grpc/grpc-node)
  - 같은 저장소 항목: [L233 · `grpc`](#l233)
  - 조사 당시 배포본: [@grpc/proto-loader@0.8.1](https://registry.npmjs.org/%40grpc%2Fproto-loader/0.8.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0` / **devDependencies**: `@types/lodash.camelcase ^4.3.4`
  - 조사 당시 인기: 주간 다운로드 [66,597,144회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40grpc%2Fproto-loader) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l002"></a>

- [ ] **[L002] `jsonwebtoken`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [auth0/node-jsonwebtoken](https://github.com/auth0/node-jsonwebtoken)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [jsonwebtoken@9.0.3](https://registry.npmjs.org/jsonwebtoken/9.0.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.once ^4.0.0`, `lodash.includes ^4.3.0`, `lodash.isnumber ^3.0.3`, `lodash.isstring ^4.0.1`, `lodash.isboolean ^3.0.3`, `lodash.isinteger ^4.0.4`, `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [57,329,187회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/jsonwebtoken) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l003"></a>

- [ ] **[L003] `archiver-utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [archiverjs/archiver-utils](https://github.com/archiverjs/archiver-utils)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [archiver-utils@5.0.2](https://registry.npmjs.org/archiver-utils/5.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [53,997,345회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/archiver-utils) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l004"></a>

- [ ] **[L004] `ts-jest`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [kulshekhar/ts-jest](https://github.com/kulshekhar/ts-jest)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [ts-jest@29.4.12](https://registry.npmjs.org/ts-jest/29.4.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.memoize ^4.1.2` / **devDependencies**: `@types/lodash.set ^4.3.9`, `@types/lodash.memoize ^4.1.9`, `@types/lodash.camelcase ^4.3.9`
  - 조사 당시 인기: 주간 다운로드 [27,914,491회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ts-jest) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l005"></a>

- [ ] **[L005] `table`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [gajus/table](https://github.com/gajus/table)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [table@6.9.0](https://registry.npmjs.org/table/6.9.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.truncate ^4.4.2` / **devDependencies**: `lodash.mapvalues ^4.6.0`, `@types/lodash.truncate ^4.4.6`, `@types/lodash.mapvalues ^4.6.6`
  - 조사 당시 인기: 주간 다운로드 [22,851,085회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/table) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l006"></a>

- [ ] **[L006] `metro-core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [react/metro](https://github.com/react/metro)
  - 같은 저장소 항목: [L007 · `metro`](#l007)
  - 조사 당시 배포본: [metro-core@0.87.0](https://registry.npmjs.org/metro-core/0.87.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [16,127,706회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/metro-core) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - 기존 참고 분석: [Metro · 2026-08-09 · 15점/제외 의견](examples/metro-ko.md) — 예시 결과이며 현재 검토와 별개

<a id="l007"></a>

- [ ] **[L007] `metro`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [react/metro](https://github.com/react/metro)
  - 같은 저장소 항목: [L006 · `metro-core`](#l006)
  - 조사 당시 배포본: [metro@0.87.0](https://registry.npmjs.org/metro/0.87.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [16,083,422회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/metro) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - 기존 참고 분석: [Metro · 2026-08-09 · 15점/제외 의견](examples/metro-ko.md) — 예시 결과이며 현재 검토와 별개

<a id="l008"></a>

- [ ] **[L008] `html-webpack-plugin`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jantimon/html-webpack-plugin](https://github.com/jantimon/html-webpack-plugin)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [html-webpack-plugin@5.6.8](https://registry.npmjs.org/html-webpack-plugin/5.6.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [15,713,737회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/html-webpack-plugin) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l009"></a>

- [ ] **[L009] `pretty-error`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [AriaMinaei/pretty-error](https://github.com/AriaMinaei/pretty-error)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [pretty-error@4.0.0](https://registry.npmjs.org/pretty-error/4.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.20`
  - 조사 당시 인기: 주간 다운로드 [15,116,848회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/pretty-error) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l010"></a>

- [ ] **[L010] `renderkid`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [AriaMinaei/RenderKid](https://github.com/AriaMinaei/RenderKid)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [renderkid@3.0.0](https://registry.npmjs.org/renderkid/3.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [15,100,000회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/renderkid) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l011"></a>

- [ ] **[L011] `dagre-d3-es`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [tbo47/dagre-es](https://github.com/tbo47/dagre-es)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [dagre-d3-es@7.0.14](https://registry.npmjs.org/dagre-d3-es/7.0.14) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [14,441,381회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/dagre-d3-es) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l012"></a>

- [ ] **[L012] `lru-memoizer`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jfromaniello/lru-memoizer](https://github.com/jfromaniello/lru-memoizer)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [lru-memoizer@3.0.0](https://registry.npmjs.org/lru-memoizer/3.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0` / **devDependencies**: `@types/lodash.clonedeep ^4.5.9`
  - 조사 당시 인기: 주간 다운로드 [14,363,989회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/lru-memoizer) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l013"></a>

- [ ] **[L013] `quill-delta`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [quilljs/delta](https://github.com/quilljs/delta)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [quill-delta@5.1.0](https://registry.npmjs.org/quill-delta/5.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0`, `lodash.clonedeep ^4.5.0` / **devDependencies**: `@types/lodash.isequal ^4.5.5`, `@types/lodash.clonedeep ^4.5.6`
  - 조사 당시 인기: 주간 다운로드 [9,189,123회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/quill-delta) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l014"></a>

- [ ] **[L014] `quill`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [slab/quill](https://github.com/slab/quill)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [quill@2.0.3](https://registry.npmjs.org/quill/2.0.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [8,045,817회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/quill) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l015"></a>

- [ ] **[L015] `command-line-args`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [75lb/command-line-args](https://github.com/75lb/command-line-args)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [command-line-args@6.0.2](https://registry.npmjs.org/command-line-args/6.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [7,950,139회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/command-line-args) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l016"></a>

- [ ] **[L016] `cypress`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [cypress-io/cypress](https://github.com/cypress-io/cypress)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [cypress@16.0.0](https://registry.npmjs.org/cypress/16.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.23`
  - 조사 당시 인기: 주간 다운로드 [7,643,697회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/cypress) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l017"></a>

- [ ] **[L017] `babel-core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-core@6.26.3](https://registry.npmjs.org/babel-core/6.26.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [7,265,591회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-core) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l018"></a>

- [ ] **[L018] `usehooks-ts`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [juliencrn/usehooks-ts](https://github.com/juliencrn/usehooks-ts)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [usehooks-ts@3.1.1](https://registry.npmjs.org/usehooks-ts/3.1.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8` / **devDependencies**: `@types/lodash.debounce ^4.0.9`
  - 조사 당시 인기: 주간 다운로드 [5,634,894회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/usehooks-ts) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l019"></a>

- [ ] **[L019] `knex`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [knex/knex](https://github.com/knex/knex)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [knex@3.3.0](https://registry.npmjs.org/knex/3.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [5,474,840회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/knex) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l020"></a>

- [ ] **[L020] `graphlib`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [dagrejs/graphlib](https://github.com/dagrejs/graphlib)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [graphlib@2.1.8](https://registry.npmjs.org/graphlib/2.1.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [4,689,797회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/graphlib) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l021"></a>

- [ ] **[L021] `formik`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jaredpalmer/formik](https://github.com/jaredpalmer/formik)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [formik@2.4.9](https://registry.npmjs.org/formik/2.4.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.14.119`
  - 조사 당시 인기: 주간 다운로드 [4,588,551회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/formik) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l022"></a>

- [ ] **[L022] `request-promise-core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [request/promise-core](https://github.com/request/promise-core)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [request-promise-core@1.1.4](https://registry.npmjs.org/request-promise-core/1.1.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.19`
  - 조사 당시 인기: 주간 다운로드 [4,467,636회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/request-promise-core) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l023"></a>

- [ ] **[L023] `lighthouse`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [GoogleChrome/lighthouse](https://github.com/GoogleChrome/lighthouse)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [lighthouse@13.4.1](https://registry.npmjs.org/lighthouse/13.4.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [4,360,393회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/lighthouse) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l024"></a>

- [ ] **[L024] `@metamask/utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [MetaMask/utils](https://github.com/MetaMask/utils)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@metamask/utils@11.12.1](https://registry.npmjs.org/%40metamask%2Futils/11.12.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `@types/lodash ^4.17.20`
  - 조사 당시 인기: 주간 다운로드 [4,286,300회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40metamask%2Futils) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l025"></a>

- [ ] **[L025] `chevrotain-allstar`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [langium/chevrotain-allstar](https://github.com/langium/chevrotain-allstar)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [chevrotain-allstar@0.5.0](https://registry.npmjs.org/chevrotain-allstar/0.5.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.18.1` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [4,272,628회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/chevrotain-allstar) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l026"></a>

- [ ] **[L026] `eslint-plugin-flowtype`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [gajus/eslint-plugin-flowtype](https://github.com/gajus/eslint-plugin-flowtype)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [eslint-plugin-flowtype@8.0.3](https://registry.npmjs.org/eslint-plugin-flowtype/8.0.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [4,266,655회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-plugin-flowtype) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l027"></a>

- [ ] **[L027] `postcss-modules`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [css-modules/postcss-modules](https://github.com/css-modules/postcss-modules)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [postcss-modules@9.0.1](https://registry.npmjs.org/postcss-modules/9.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [4,259,844회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/postcss-modules) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l028"></a>

- [ ] **[L028] `eslint-plugin-sonarjs`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [SonarSource/SonarJS](https://github.com/SonarSource/SonarJS)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [eslint-plugin-sonarjs@4.2.0](https://registry.npmjs.org/eslint-plugin-sonarjs/4.2.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [4,115,741회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-plugin-sonarjs) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l029"></a>

- [ ] **[L029] `babel-types`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-types@6.26.0](https://registry.npmjs.org/babel-types/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [3,767,006회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-types) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l030"></a>

- [ ] **[L030] `issue-parser`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [semantic-release/issue-parser](https://github.com/semantic-release/issue-parser)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [issue-parser@7.0.2](https://registry.npmjs.org/issue-parser/7.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.uniqby ^4.7.0`, `lodash.isstring ^4.0.1`, `lodash.capitalize ^4.2.1`, `lodash.escaperegexp ^4.1.2`, `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [3,705,230회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/issue-parser) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l031"></a>

- [ ] **[L031] `json-schema-to-typescript`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bcherny/json-schema-to-typescript](https://github.com/bcherny/json-schema-to-typescript)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [json-schema-to-typescript@16.0.0](https://registry.npmjs.org/json-schema-to-typescript/16.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`, `@types/lodash ^4.17.25`
  - 조사 당시 인기: 주간 다운로드 [3,464,191회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/json-schema-to-typescript) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l032"></a>

- [ ] **[L032] `probe-image-size`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nodeca/probe-image-size](https://github.com/nodeca/probe-image-size)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [probe-image-size@7.4.0](https://registry.npmjs.org/probe-image-size/7.4.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [3,433,483회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/probe-image-size) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l033"></a>

- [ ] **[L033] `react-base16-styling`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [reduxjs/redux-devtools](https://github.com/reduxjs/redux-devtools)
  - 같은 저장소 항목: [L095 · `react-json-tree`](#l095), [L237 · `react-dock`](#l237), [L253 · `redux-devtools-log-monitor`](#l253), [L291 · `@redux-devtools/log-monitor`](#l291)
  - 조사 당시 배포본: [react-base16-styling@0.10.0](https://registry.npmjs.org/react-base16-styling/0.10.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash ^4.17.0` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [3,313,329회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-base16-styling) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l034"></a>

- [ ] **[L034] `@semantic-release/github`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [semantic-release/github](https://github.com/semantic-release/github)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@semantic-release/github@12.0.9](https://registry.npmjs.org/%40semantic-release%2Fgithub/12.0.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,200,870회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40semantic-release%2Fgithub) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l035"></a>

- [ ] **[L035] `@semantic-release/npm`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [semantic-release/npm](https://github.com/semantic-release/npm)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@semantic-release/npm@13.1.5](https://registry.npmjs.org/%40semantic-release%2Fnpm/13.1.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,128,414회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40semantic-release%2Fnpm) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l036"></a>

- [ ] **[L036] `@semantic-release/release-notes-generator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [semantic-release/release-notes-generator](https://github.com/semantic-release/release-notes-generator)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@semantic-release/release-notes-generator@14.1.1](https://registry.npmjs.org/%40semantic-release%2Frelease-notes-generator/14.1.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,120,310회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40semantic-release%2Frelease-notes-generator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l037"></a>

- [ ] **[L037] `semantic-release`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [semantic-release/semantic-release](https://github.com/semantic-release/semantic-release)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [semantic-release@25.0.9](https://registry.npmjs.org/semantic-release/25.0.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,066,602회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/semantic-release) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l038"></a>

- [ ] **[L038] `@semantic-release/commit-analyzer`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [semantic-release/commit-analyzer](https://github.com/semantic-release/commit-analyzer)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@semantic-release/commit-analyzer@13.0.1](https://registry.npmjs.org/%40semantic-release%2Fcommit-analyzer/13.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,065,267회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40semantic-release%2Fcommit-analyzer) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l039"></a>

- [ ] **[L039] `babel-traverse`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-traverse@6.26.0](https://registry.npmjs.org/babel-traverse/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [3,020,400회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-traverse) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l040"></a>

- [ ] **[L040] `webdriverio`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [webdriverio/webdriverio](https://github.com/webdriverio/webdriverio)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [webdriverio@9.31.5](https://registry.npmjs.org/webdriverio/9.31.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.zip ^4.2.0`, `lodash.clonedeep ^4.5.0` / **devDependencies**: `@types/lodash.zip ^4.2.9`, `@types/lodash.clonedeep ^4.5.9`
  - 조사 당시 인기: 주간 다운로드 [2,970,660회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/webdriverio) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l041"></a>

- [ ] **[L041] `electron-winstaller`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [electron/windows-installer](https://github.com/electron/windows-installer)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [electron-winstaller@5.4.4](https://registry.npmjs.org/electron-winstaller/5.4.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.0`
  - 조사 당시 인기: 주간 다운로드 [2,956,844회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/electron-winstaller) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l042"></a>

- [ ] **[L042] `sequelize`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sequelize/sequelize](https://github.com/sequelize/sequelize)
  - 같은 저장소 항목: [L279 · `@sequelize/utils`](#l279)
  - 조사 당시 배포본: [sequelize@6.37.8](https://registry.npmjs.org/sequelize/6.37.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash 4.14.197`
  - 조사 당시 인기: 주간 다운로드 [2,869,021회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/sequelize) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l043"></a>

- [ ] **[L043] `dagre`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [dagrejs/dagre](https://github.com/dagrejs/dagre)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [dagre@0.8.5](https://registry.npmjs.org/dagre/0.8.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [2,858,682회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/dagre) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l044"></a>

- [ ] **[L044] `slate-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ianstormtaylor/slate](https://github.com/ianstormtaylor/slate)
  - 같은 저장소 항목: [L324 · `slate`](#l324)
  - 조사 당시 배포본: [slate-react@0.126.4](https://registry.npmjs.org/slate-react/0.126.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.14.200`
  - 조사 당시 인기: 주간 다운로드 [2,820,518회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/slate-react) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l045"></a>

- [ ] **[L045] `babel-template`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-template@6.26.0](https://registry.npmjs.org/babel-template/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [2,775,505회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-template) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l046"></a>

- [ ] **[L046] `catharsis`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [hegemonic/catharsis](https://github.com/hegemonic/catharsis)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [catharsis@0.11.0](https://registry.npmjs.org/catharsis/0.11.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [2,735,409회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/catharsis) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l047"></a>

- [ ] **[L047] `@trivago/prettier-plugin-sort-imports`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [trivago/prettier-plugin-sort-imports](https://github.com/trivago/prettier-plugin-sort-imports)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@trivago/prettier-plugin-sort-imports@6.0.2](https://registry.npmjs.org/%40trivago%2Fprettier-plugin-sort-imports/6.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [2,710,019회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40trivago%2Fprettier-plugin-sort-imports) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l048"></a>

- [ ] **[L048] `requizzle`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [hegemonic/requizzle](https://github.com/hegemonic/requizzle)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [requizzle@0.2.4](https://registry.npmjs.org/requizzle/0.2.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [2,686,387회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/requizzle) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l049"></a>

- [ ] **[L049] `electron-updater`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [electron-userland/electron-builder](https://github.com/electron-userland/electron-builder)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [electron-updater@6.8.9](https://registry.npmjs.org/electron-updater/6.8.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0`, `lodash.escaperegexp ^4.1.2` / **devDependencies**: `@types/lodash.isequal 4.5.5`, `@types/lodash.escaperegexp 4.1.6`
  - 조사 당시 인기: 주간 다운로드 [2,583,245회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/electron-updater) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l050"></a>

- [ ] **[L050] `globule`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [cowboy/node-globule](https://github.com/cowboy/node-globule)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [globule@1.3.4](https://registry.npmjs.org/globule/1.3.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [2,428,154회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/globule) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l051"></a>

- [ ] **[L051] `@jsdoc/salty`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jsdoc/jsdoc](https://github.com/jsdoc/jsdoc)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@jsdoc/salty@0.2.12](https://registry.npmjs.org/%40jsdoc%2Fsalty/0.2.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [2,421,989회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40jsdoc%2Fsalty) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l052"></a>

- [ ] **[L052] `json2csv`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [zemirco/json2csv](https://github.com/zemirco/json2csv)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [json2csv@6.0.0-alpha.2](https://registry.npmjs.org/json2csv/6.0.0-alpha.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`
  - 조사 당시 인기: 주간 다운로드 [2,419,293회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/json2csv) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l053"></a>

- [ ] **[L053] `json-schema-compare`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [mokkabonna/json-schema-compare](https://github.com/mokkabonna/json-schema-compare)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [json-schema-compare@0.2.2](https://registry.npmjs.org/json-schema-compare/0.2.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [2,403,027회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/json-schema-compare) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l054"></a>

- [ ] **[L054] `babel-generator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-generator@6.26.1](https://registry.npmjs.org/babel-generator/6.26.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [2,396,719회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-generator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l055"></a>

- [ ] **[L055] `reactcss`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [casesandberg/reactcss](https://github.com/casesandberg/reactcss)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [reactcss@1.2.3](https://registry.npmjs.org/reactcss/1.2.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.0.1`
  - 조사 당시 인기: 주간 다운로드 [2,333,715회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/reactcss) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l056"></a>

- [ ] **[L056] `jest-mock-extended`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [marchaos/jest-mock-extended](https://github.com/marchaos/jest-mock-extended)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [jest-mock-extended@4.0.1](https://registry.npmjs.org/jest-mock-extended/4.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0` / **devDependencies**: `@types/lodash.isequal ^4.5.8`
  - 조사 당시 인기: 주간 다운로드 [2,307,981회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/jest-mock-extended) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l057"></a>

- [ ] **[L057] `react-color`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [casesandberg/react-color](https://github.com/casesandberg/react-color)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-color@2.19.3](https://registry.npmjs.org/react-color/2.19.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`, `lodash-es ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [2,248,000회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-color) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l058"></a>

- [ ] **[L058] `babel-register`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-register@6.26.0](https://registry.npmjs.org/babel-register/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [1,877,384회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-register) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l059"></a>

- [ ] **[L059] `yeoman-environment`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [yeoman/environment](https://github.com/yeoman/environment)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [yeoman-environment@6.3.0](https://registry.npmjs.org/yeoman-environment/6.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.18.1` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [1,859,320회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/yeoman-environment) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l060"></a>

- [ ] **[L060] `swagger-jsdoc`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Surnet/swagger-jsdoc](https://github.com/Surnet/swagger-jsdoc)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [swagger-jsdoc@6.3.0](https://registry.npmjs.org/swagger-jsdoc/6.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.mergewith ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [1,841,151회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/swagger-jsdoc) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l061"></a>

- [ ] **[L061] `gradle-to-js`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ninetwozero/gradle-to-js](https://github.com/ninetwozero/gradle-to-js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gradle-to-js@2.0.1](https://registry.npmjs.org/gradle-to-js/2.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [1,830,785회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gradle-to-js) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l062"></a>

- [ ] **[L062] `cz-conventional-changelog`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [commitizen/cz-conventional-changelog](https://github.com/commitizen/cz-conventional-changelog)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [cz-conventional-changelog@3.3.0](https://registry.npmjs.org/cz-conventional-changelog/3.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.map ^4.5.1`
  - 조사 당시 인기: 주간 다운로드 [1,739,982회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/cz-conventional-changelog) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l063"></a>

- [ ] **[L063] `redux-mock-store`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [arnaudbenard/redux-mock-store](https://github.com/arnaudbenard/redux-mock-store)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [redux-mock-store@1.5.5](https://registry.npmjs.org/redux-mock-store/1.5.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [1,713,449회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/redux-mock-store) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l064"></a>

- [ ] **[L064] `contentful-sdk-core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [contentful/contentful-sdk-core](https://github.com/contentful/contentful-sdk-core)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [contentful-sdk-core@10.0.0](https://registry.npmjs.org/contentful-sdk-core/10.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.23` / **devDependencies**: `@types/lodash ^4.17.6`
  - 조사 당시 인기: 주간 다운로드 [1,696,865회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/contentful-sdk-core) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l065"></a>

- [ ] **[L065] `express-validator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [express-validator/express-validator](https://github.com/express-validator/express-validator)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [express-validator@7.3.2](https://registry.npmjs.org/express-validator/7.3.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1` / **devDependencies**: `@types/lodash ^4.14.168`
  - 조사 당시 인기: 주간 다운로드 [1,688,074회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/express-validator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l066"></a>

- [ ] **[L066] `react-slick`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [akiran/react-slick](https://github.com/akiran/react-slick)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-slick@0.31.0](https://registry.npmjs.org/react-slick/0.31.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 [1,680,378회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-slick) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l067"></a>

- [ ] **[L067] `commitizen`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [commitizen/cz-cli](https://github.com/commitizen/cz-cli)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [commitizen@4.3.2](https://registry.npmjs.org/commitizen/4.3.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash 4.18.1`
  - 조사 당시 인기: 주간 다운로드 [1,678,836회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/commitizen) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l068"></a>

- [ ] **[L068] `tus-js-client`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [tus/tus-js-client](https://github.com/tus/tus-js-client)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [tus-js-client@4.3.1](https://registry.npmjs.org/tus-js-client/4.3.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [1,673,063회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/tus-js-client) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l069"></a>

- [ ] **[L069] `@nivo/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [plouc/nivo](https://github.com/plouc/nivo)
  - 같은 저장소 항목: [L263 · `nivo`](#l263)
  - 조사 당시 배포본: [@nivo/core@0.99.0](https://registry.npmjs.org/%40nivo%2Fcore/0.99.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [1,662,861회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nivo%2Fcore) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l070"></a>

- [ ] **[L070] `launchdarkly-react-client-sdk`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [launchdarkly/react-client-sdk](https://github.com/launchdarkly/react-client-sdk)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [launchdarkly-react-client-sdk@3.9.4](https://registry.npmjs.org/launchdarkly-react-client-sdk/3.9.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0` / **devDependencies**: `@types/lodash.camelcase ^4.3.6`
  - 조사 당시 인기: 주간 다운로드 [1,628,083회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/launchdarkly-react-client-sdk) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l071"></a>

- [ ] **[L071] `yeoman-generator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [yeoman/generator](https://github.com/yeoman/generator)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [yeoman-generator@8.3.0](https://registry.npmjs.org/yeoman-generator/8.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.18.1`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [1,556,957회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/yeoman-generator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l072"></a>

- [ ] **[L072] `babel-plugin-transform-es2015-block-scoping`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-plugin-transform-es2015-block-scoping@6.26.0](https://registry.npmjs.org/babel-plugin-transform-es2015-block-scoping/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [1,488,449회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-plugin-transform-es2015-block-scoping) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l073"></a>

- [ ] **[L073] `mochawesome-report-generator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [adamgruber/mochawesome-report-generator](https://github.com/adamgruber/mochawesome-report-generator)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [mochawesome-report-generator@6.3.2](https://registry.npmjs.org/mochawesome-report-generator/6.3.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isfunction ^3.0.9` / **devDependencies**: `lodash ^4.16.4`
  - 조사 당시 인기: 주간 다운로드 [1,477,345회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/mochawesome-report-generator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l074"></a>

- [ ] **[L074] `babel-helper-define-map`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-helper-define-map@6.26.0](https://registry.npmjs.org/babel-helper-define-map/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [1,466,476회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-helper-define-map) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l075"></a>

- [ ] **[L075] `babel-helper-regex`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L094 · `@babel/helper-regex`](#l094), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [babel-helper-regex@6.26.0](https://registry.npmjs.org/babel-helper-regex/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [1,433,564회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-helper-regex) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l076"></a>

- [ ] **[L076] `csvtojson`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Keyang/node-csvtojson](https://github.com/Keyang/node-csvtojson)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [csvtojson@2.0.14](https://registry.npmjs.org/csvtojson/2.0.14) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash.set ^4.3.6`
  - 조사 당시 인기: 주간 다운로드 [1,409,752회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/csvtojson) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l077"></a>

- [ ] **[L077] `@chakra-ui/utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [chakra-ui/chakra-ui](https://github.com/chakra-ui/chakra-ui)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@chakra-ui/utils@2.2.2](https://registry.npmjs.org/%40chakra-ui%2Futils/2.2.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.mergewith 4.6.2`, `@types/lodash.mergewith 4.6.9`
  - 조사 당시 인기: 주간 다운로드 [1,370,098회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40chakra-ui%2Futils) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l078"></a>

- [ ] **[L078] `enzyme`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [airbnb/enzyme](https://github.com/airbnb/enzyme)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [enzyme@3.11.0](https://registry.npmjs.org/enzyme/3.11.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.escape ^4.0.1`, `lodash.isequal ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [1,344,364회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/enzyme) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l079"></a>

- [ ] **[L079] `kapsule`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vasturiano/kapsule](https://github.com/vasturiano/kapsule)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [kapsule@1.16.3](https://registry.npmjs.org/kapsule/1.16.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es 4`
  - 조사 당시 인기: 주간 다운로드 [1,328,441회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/kapsule) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l080"></a>

- [ ] **[L080] `get-package-info`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rahatarmanahmed/get-package-info](https://github.com/rahatarmanahmed/get-package-info)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [get-package-info@1.0.0](https://registry.npmjs.org/get-package-info/1.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.0.0`
  - 조사 당시 인기: 주간 다운로드 [1,306,304회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/get-package-info) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l081"></a>

- [ ] **[L081] `@rjsf/utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rjsf-team/react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form)
  - 같은 저장소 항목: [L086 · `@rjsf/core`](#l086), [L093 · `@rjsf/validator-ajv8`](#l093)
  - 조사 당시 배포본: [@rjsf/utils@6.8.0](https://registry.npmjs.org/%40rjsf%2Futils/6.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`, `lodash-es ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [1,287,975회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40rjsf%2Futils) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - 기존 참고 분석: [react-jsonschema-form · 2026-08-09 · 78점/권장 의견](examples/react-jsonschema-form-ko.md) — 예시 결과이며 현재 검토와 별개

<a id="l082"></a>

- [ ] **[L082] `convict`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [mozilla/node-convict](https://github.com/mozilla/node-convict)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [convict@6.2.5](https://registry.npmjs.org/convict/6.2.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [1,282,577회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/convict) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l083"></a>

- [ ] **[L083] `eslint-plugin-compat`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [amilajack/eslint-plugin-compat](https://github.com/amilajack/eslint-plugin-compat)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [eslint-plugin-compat@7.0.2](https://registry.npmjs.org/eslint-plugin-compat/7.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.memoize ^4.1.2` / **devDependencies**: `@types/lodash.memoize ^4.1.9`
  - 조사 당시 인기: 주간 다운로드 [1,264,942회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-plugin-compat) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l084"></a>

- [ ] **[L084] `danger`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [danger/danger-js](https://github.com/danger/danger-js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [danger@14.0.7](https://registry.npmjs.org/danger/14.0.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.memoize ^4.1.2`, `lodash.includes ^4.3.0`, `lodash.isobject ^3.0.2`, `lodash.mapvalues ^4.6.0` / **devDependencies**: `@types/lodash.memoize ^4.1.3`, `@types/lodash.includes ^4.3.4`, `@types/lodash.mapvalues ^4.6.6`
  - 조사 당시 인기: 주간 다운로드 [1,259,322회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/danger) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l085"></a>

- [ ] **[L085] `grunt-legacy-util`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [gruntjs/grunt-legacy-util](https://github.com/gruntjs/grunt-legacy-util)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [grunt-legacy-util@2.0.2](https://registry.npmjs.org/grunt-legacy-util/2.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.0`
  - 조사 당시 인기: 주간 다운로드 [1,256,766회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/grunt-legacy-util) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l086"></a>

- [ ] **[L086] `@rjsf/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rjsf-team/react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form)
  - 같은 저장소 항목: [L081 · `@rjsf/utils`](#l081), [L093 · `@rjsf/validator-ajv8`](#l093)
  - 조사 당시 배포본: [@rjsf/core@6.8.0](https://registry.npmjs.org/%40rjsf%2Fcore/6.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`, `lodash-es ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [1,220,936회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40rjsf%2Fcore) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - 기존 참고 분석: [react-jsonschema-form · 2026-08-09 · 78점/권장 의견](examples/react-jsonschema-form-ko.md) — 예시 결과이며 현재 검토와 별개

<a id="l087"></a>

- [ ] **[L087] `@sapphire/shapeshift`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sapphiredev/shapeshift](https://github.com/sapphiredev/shapeshift)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@sapphire/shapeshift@5.0.0](https://registry.npmjs.org/%40sapphire%2Fshapeshift/5.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1` / **devDependencies**: `@types/lodash ^4.17.23`
  - 조사 당시 인기: 주간 다운로드 [1,215,284회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40sapphire%2Fshapeshift) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l088"></a>

- [ ] **[L088] `react-big-calendar`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bigcalendar/react-big-calendar](https://github.com/bigcalendar/react-big-calendar)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-big-calendar@1.20.0](https://registry.npmjs.org/react-big-calendar/1.20.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`, `lodash-es ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [1,202,542회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-big-calendar) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l089"></a>

- [ ] **[L089] `node-jose`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [cisco/node-jose](https://github.com/cisco/node-jose)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [node-jose@2.2.0](https://registry.npmjs.org/node-jose/2.2.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [1,187,287회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/node-jose) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l090"></a>

- [ ] **[L090] `eslint-import-resolver-webpack`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [import-js/eslint-plugin-import](https://github.com/import-js/eslint-plugin-import)
  - 같은 저장소 항목: [L309 · `eslint-plugin-import`](#l309)
  - 조사 당시 배포본: [eslint-import-resolver-webpack@0.13.11](https://registry.npmjs.org/eslint-import-resolver-webpack/0.13.11) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [1,181,008회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-import-resolver-webpack) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l091"></a>

- [ ] **[L091] `last-call-webpack-plugin`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [NMFR/last-call-webpack-plugin](https://github.com/NMFR/last-call-webpack-plugin)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [last-call-webpack-plugin@3.0.0](https://registry.npmjs.org/last-call-webpack-plugin/3.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.5`
  - 조사 당시 인기: 주간 다운로드 [1,130,643회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/last-call-webpack-plugin) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l092"></a>

- [ ] **[L092] `graphql-query-complexity`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [slicknode/graphql-query-complexity](https://github.com/slicknode/graphql-query-complexity)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [graphql-query-complexity@2.0.0](https://registry.npmjs.org/graphql-query-complexity/2.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2` / **devDependencies**: `@types/lodash.get ^4.4.6`
  - 조사 당시 인기: 주간 다운로드 [1,098,519회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/graphql-query-complexity) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l093"></a>

- [ ] **[L093] `@rjsf/validator-ajv8`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rjsf-team/react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form)
  - 같은 저장소 항목: [L081 · `@rjsf/utils`](#l081), [L086 · `@rjsf/core`](#l086)
  - 조사 당시 배포본: [@rjsf/validator-ajv8@6.8.0](https://registry.npmjs.org/%40rjsf%2Fvalidator-ajv8/6.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`, `lodash-es ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [1,052,684회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40rjsf%2Fvalidator-ajv8) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - 기존 참고 분석: [react-jsonschema-form · 2026-08-09 · 78점/권장 의견](examples/react-jsonschema-form-ko.md) — 예시 결과이며 현재 검토와 별개

<a id="l094"></a>

- [ ] **[L094] `@babel/helper-regex`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L138 · `babel-cli`](#l138)
  - 조사 당시 배포본: [@babel/helper-regex@7.10.5](https://registry.npmjs.org/%40babel%2Fhelper-regex/7.10.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.19`
  - 조사 당시 인기: 주간 다운로드 [1,049,478회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40babel%2Fhelper-regex) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l095"></a>

- [ ] **[L095] `react-json-tree`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [reduxjs/redux-devtools](https://github.com/reduxjs/redux-devtools)
  - 같은 저장소 항목: [L033 · `react-base16-styling`](#l033), [L237 · `react-dock`](#l237), [L253 · `redux-devtools-log-monitor`](#l253), [L291 · `@redux-devtools/log-monitor`](#l291)
  - 조사 당시 배포본: [react-json-tree@0.20.0](https://registry.npmjs.org/react-json-tree/0.20.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `@types/lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [1,029,961회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-json-tree) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l096"></a>

- [ ] **[L096] `fishery`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [thoughtbot/fishery](https://github.com/thoughtbot/fishery)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [fishery@2.4.0](https://registry.npmjs.org/fishery/2.4.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.mergewith ^4.6.2` / **devDependencies**: `@types/lodash.mergewith 4.6.9`
  - 조사 당시 인기: 주간 다운로드 [1,023,236회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/fishery) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l097"></a>

- [ ] **[L097] `ahooks`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [alibaba/hooks](https://github.com/alibaba/hooks)
  - 같은 저장소 항목: [L290 · `@ahooksjs/use-request`](#l290)
  - 조사 당시 배포본: [ahooks@3.9.7](https://registry.npmjs.org/ahooks/3.9.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [1,000,020회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ahooks) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l098"></a>

- [ ] **[L098] `react-debounce-input`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nkbt/react-debounce-input](https://github.com/nkbt/react-debounce-input)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-debounce-input@3.3.0](https://registry.npmjs.org/react-debounce-input/3.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4`
  - 조사 당시 인기: 주간 다운로드 [993,694회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-debounce-input) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l099"></a>

- [ ] **[L099] `node-sass`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sass/node-sass](https://github.com/sass/node-sass)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [node-sass@9.0.0](https://registry.npmjs.org/node-sass/9.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [984,347회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/node-sass) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - npm 배포 중단 안내: Node Sass is no longer supported. Please use `sass` or `sass-embedded` instead.

<a id="l100"></a>

- [ ] **[L100] `sass-graph`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [xzyfer/sass-graph](https://github.com/xzyfer/sass-graph)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [sass-graph@4.0.1](https://registry.npmjs.org/sass-graph/4.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.11`
  - 조사 당시 인기: 주간 다운로드 [945,812회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/sass-graph) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l101"></a>

- [ ] **[L101] `release-it`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [release-it/release-it](https://github.com/release-it/release-it)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [release-it@21.0.2](https://registry.npmjs.org/release-it/21.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge 4.6.2`
  - 조사 당시 인기: 주간 다운로드 [908,032회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/release-it) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l102"></a>

- [ ] **[L102] `recyclerlistview`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Flipkart/recyclerlistview](https://github.com/Flipkart/recyclerlistview)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [recyclerlistview@4.2.3](https://registry.npmjs.org/recyclerlistview/4.2.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce 4.0.8` / **devDependencies**: `@types/lodash.debounce 4.0.8`
  - 조사 당시 인기: 주간 다운로드 [900,966회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/recyclerlistview) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l103"></a>

- [ ] **[L103] `cli-ux`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [oclif/cli-ux](https://github.com/oclif/cli-ux)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [cli-ux@6.0.9](https://registry.npmjs.org/cli-ux/6.0.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.14.117`
  - 조사 당시 인기: 주간 다운로드 [899,777회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/cli-ux) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - npm 배포 중단 안내: Package no longer supported. Contact Support at https://www.npmjs.com/support for more info.

<a id="l104"></a>

- [ ] **[L104] `benchmark`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bestiejs/benchmark.js](https://github.com/bestiejs/benchmark.js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [benchmark@2.1.4](https://registry.npmjs.org/benchmark/2.1.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [879,438회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/benchmark) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l105"></a>

- [ ] **[L105] `chokidar-cli`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [open-npm-tools/chokidar-cli](https://github.com/open-npm-tools/chokidar-cli)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [chokidar-cli@3.0.0](https://registry.npmjs.org/chokidar-cli/3.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [874,816회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/chokidar-cli) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l106"></a>

- [ ] **[L106] `date-holidays`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [commenthol/date-holidays](https://github.com/commenthol/date-holidays)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [date-holidays@3.36.0](https://registry.npmjs.org/date-holidays/3.36.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [849,045회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/date-holidays) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l107"></a>

- [ ] **[L107] `@oclif/help`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [oclif/help](https://github.com/oclif/help)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@oclif/help@1.0.15](https://registry.npmjs.org/%40oclif%2Fhelp/1.0.15) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.14.192`
  - 조사 당시 인기: 주간 다운로드 [842,910회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40oclif%2Fhelp) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - npm 배포 중단 안내: Package no longer supported. Contact Support at https://www.npmjs.com/support for more info.

<a id="l108"></a>

- [ ] **[L108] `react-scroll`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [fisshy/react-scroll](https://github.com/fisshy/react-scroll)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-scroll@1.9.3](https://registry.npmjs.org/react-scroll/1.9.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [835,046회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-scroll) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l109"></a>

- [ ] **[L109] `force-graph`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vasturiano/force-graph](https://github.com/vasturiano/force-graph)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [force-graph@1.51.4](https://registry.npmjs.org/force-graph/1.51.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es 4`
  - 조사 당시 인기: 주간 다운로드 [827,482회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/force-graph) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l110"></a>

- [ ] **[L110] `typescript-plugin-css-modules`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [mrmckeb/typescript-plugin-css-modules](https://github.com/mrmckeb/typescript-plugin-css-modules)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [typescript-plugin-css-modules@5.2.0](https://registry.npmjs.org/typescript-plugin-css-modules/5.2.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0` / **devDependencies**: `@types/lodash.camelcase ^4.3.9`
  - 조사 당시 인기: 주간 다운로드 [822,728회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/typescript-plugin-css-modules) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l111"></a>

- [ ] **[L111] `@serverless/event-mocks`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [.](.)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@serverless/event-mocks@1.1.1](https://registry.npmjs.org/%40serverless%2Fevent-mocks/1.1.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.11`, `@types/lodash ^4.14.123`
  - 조사 당시 인기: 주간 다운로드 [819,119회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40serverless%2Fevent-mocks) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l112"></a>

- [ ] **[L112] `react-phone-input-2`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bl00mber/react-phone-input-2](https://github.com/bl00mber/react-phone-input-2)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-phone-input-2@2.15.1](https://registry.npmjs.org/react-phone-input-2/2.15.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.reduce ^4.6.0`, `lodash.memoize ^4.1.2`, `lodash.debounce ^4.0.8`, `lodash.startswith ^4.2.1`
  - 조사 당시 인기: 주간 다운로드 [778,997회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-phone-input-2) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l113"></a>

- [ ] **[L113] `easy-extender`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [shakyshane/easy-extender](https://github.com/shakyshane/easy-extender)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [easy-extender@2.3.4](https://registry.npmjs.org/easy-extender/2.3.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.10`
  - 조사 당시 인기: 주간 다운로드 [731,815회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/easy-extender) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l114"></a>

- [ ] **[L114] `simplebar-core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [grsmto/simplebar](https://github.com/grsmto/simplebar)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [simplebar-core@1.3.2](https://registry.npmjs.org/simplebar-core/1.3.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [691,156회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/simplebar-core) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l115"></a>

- [ ] **[L115] `element-plus`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [element-plus/element-plus](https://github.com/element-plus/element-plus)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [element-plus@2.14.5](https://registry.npmjs.org/element-plus/2.14.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`, `lodash-es ^4.18.1`, `@types/lodash ^4.17.24`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [688,796회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/element-plus) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l116"></a>

- [ ] **[L116] `sourcemap-validator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ben-ng/sourcemap-validator](https://github.com/ben-ng/sourcemap-validator)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [sourcemap-validator@2.1.0](https://registry.npmjs.org/sourcemap-validator/2.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.foreach ^4.5.0`, `lodash.template ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [622,020회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/sourcemap-validator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l117"></a>

- [ ] **[L117] `react-dates`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [airbnb/react-dates](https://github.com/airbnb/react-dates)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-dates@21.8.0](https://registry.npmjs.org/react-dates/21.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [615,102회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-dates) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l118"></a>

- [ ] **[L118] `enzyme-to-json`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [adriantoine/enzyme-to-json](https://github.com/adriantoine/enzyme-to-json)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [enzyme-to-json@3.6.2](https://registry.npmjs.org/enzyme-to-json/3.6.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [609,020회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/enzyme-to-json) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l119"></a>

- [ ] **[L119] `react-quill-new`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [VaguelySerious/react-quill](https://github.com/VaguelySerious/react-quill)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-quill-new@3.8.3](https://registry.npmjs.org/react-quill-new/3.8.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [606,030회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-quill-new) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l120"></a>

- [ ] **[L120] `babel-plugin-lodash`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [lodash/babel-plugin-lodash](https://github.com/lodash/babel-plugin-lodash)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [babel-plugin-lodash@3.3.4](https://registry.npmjs.org/babel-plugin-lodash/3.3.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.10` / **devDependencies**: `lodash-es ^4.17.10`
  - 조사 당시 인기: 주간 다운로드 [601,528회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-plugin-lodash) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l121"></a>

- [ ] **[L121] `openapi-schema-validator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [kogosoftwarellc/open-api](https://github.com/kogosoftwarellc/open-api)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [openapi-schema-validator@12.1.3](https://registry.npmjs.org/openapi-schema-validator/12.1.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.1`
  - 조사 당시 인기: 주간 다운로드 [586,886회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/openapi-schema-validator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l122"></a>

- [ ] **[L122] `eslint-plugin-filenames`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [selaux/eslint-plugin-filenames](https://github.com/selaux/eslint-plugin-filenames)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [eslint-plugin-filenames@1.3.2](https://registry.npmjs.org/eslint-plugin-filenames/1.3.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase 4.3.0`, `lodash.kebabcase 4.1.1`, `lodash.snakecase 4.1.1`, `lodash.upperfirst 4.3.1`
  - 조사 당시 인기: 주간 다운로드 [575,413회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-plugin-filenames) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l123"></a>

- [ ] **[L123] `iovalkey`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [valkey-io/iovalkey](https://github.com/valkey-io/iovalkey)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [iovalkey@0.4.0](https://registry.npmjs.org/iovalkey/0.4.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.defaults ^4.2.0`, `lodash.isarguments ^3.1.0` / **devDependencies**: `@types/lodash.defaults ^4.2.7`, `@types/lodash.isarguments ^3.1.7`
  - 조사 당시 인기: 주간 다운로드 [570,199회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/iovalkey) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l124"></a>

- [ ] **[L124] `victory-core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [FormidableLabs/victory](https://github.com/FormidableLabs/victory)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [victory-core@37.3.6](https://registry.npmjs.org/victory-core/37.3.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [558,889회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/victory-core) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l125"></a>

- [ ] **[L125] `css-modules-require-hook`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [css-modules/css-modules-require-hook](https://github.com/css-modules/css-modules-require-hook)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [css-modules-require-hook@4.2.3](https://registry.npmjs.org/css-modules-require-hook/4.2.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [556,626회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/css-modules-require-hook) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l126"></a>

- [ ] **[L126] `express-openapi-validator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [cdimascio/express-openapi-validator](https://github.com/cdimascio/express-openapi-validator)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [express-openapi-validator@5.6.2](https://registry.npmjs.org/express-openapi-validator/5.6.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`, `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [542,125회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/express-openapi-validator) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l127"></a>

- [ ] **[L127] `react-lazy-load-image-component`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Aljullu/react-lazy-load-image-component](https://github.com/Aljullu/react-lazy-load-image-component)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-lazy-load-image-component@1.6.3](https://registry.npmjs.org/react-lazy-load-image-component/1.6.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [530,437회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-lazy-load-image-component) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l128"></a>

- [ ] **[L128] `apollo-graphql`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: 미확인 — 작업 시작 시 공식 저장소 확인
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [apollo-graphql@0.9.7](https://registry.npmjs.org/apollo-graphql/0.9.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.sortby ^4.7.0`
  - 조사 당시 인기: 주간 다운로드 [525,684회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/apollo-graphql) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l129"></a>

- [ ] **[L129] `promise-props-recursive`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rexxars/promise-props-recursive](https://github.com/rexxars/promise-props-recursive)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [promise-props-recursive@2.0.2](https://registry.npmjs.org/promise-props-recursive/2.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isplainobject ^4.0.0`
  - 조사 당시 인기: 주간 다운로드 [524,961회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/promise-props-recursive) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l130"></a>

- [ ] **[L130] `redux-form`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [redux-form/redux-form](https://github.com/redux-form/redux-form)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [redux-form@8.3.10](https://registry.npmjs.org/redux-form/8.3.10) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [520,403회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/redux-form) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l131"></a>

- [ ] **[L131] `ipull`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ido-pluto/ipull](https://github.com/ido-pluto/ipull)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [ipull@4.0.3](https://registry.npmjs.org/ipull/4.0.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8` / **devDependencies**: `@types/lodash.debounce ^4.0.9`
  - 조사 당시 인기: 주간 다운로드 [499,672회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ipull) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l132"></a>

- [ ] **[L132] `babel-preset-minify`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/minify](https://github.com/babel/minify)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [babel-preset-minify@0.5.2](https://registry.npmjs.org/babel-preset-minify/0.5.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.11`
  - 조사 당시 인기: 주간 다운로드 [495,065회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-preset-minify) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l133"></a>

- [ ] **[L133] `persona`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: 미확인 — 작업 시작 시 공식 저장소 확인
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [persona@5.8.0](https://registry.npmjs.org/persona/5.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.kebabcase ^4.1.1` / **devDependencies**: `@types/lodash.kebabcase ^4.1.9`
  - 조사 당시 인기: 주간 다운로드 [479,675회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/persona) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l134"></a>

- [ ] **[L134] `gulp-sass`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [dlmanning/gulp-sass](https://github.com/dlmanning/gulp-sass)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gulp-sass@6.0.1](https://registry.npmjs.org/gulp-sass/6.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [456,116회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gulp-sass) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l135"></a>

- [ ] **[L135] `clean-deep`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nunofgs/clean-deep](https://github.com/nunofgs/clean-deep)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [clean-deep@3.4.0](https://registry.npmjs.org/clean-deep/3.4.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isempty ^4.4.0`, `lodash.transform ^4.6.0`, `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [448,554회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/clean-deep) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l136"></a>

- [ ] **[L136] `html-to-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [aknuds1/html-to-react](https://github.com/aknuds1/html-to-react)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [html-to-react@1.7.0](https://registry.npmjs.org/html-to-react/1.7.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [431,451회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/html-to-react) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l137"></a>

- [ ] **[L137] `react-google-autocomplete`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ErrorPro/react-google-autocomplete](https://github.com/ErrorPro/react-google-autocomplete)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-google-autocomplete@2.7.5](https://registry.npmjs.org/react-google-autocomplete/2.7.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 [413,235회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-google-autocomplete) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l138"></a>

- [ ] **[L138] `babel-cli`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel/babel](https://github.com/babel/babel)
  - 같은 저장소 항목: [L017 · `babel-core`](#l017), [L029 · `babel-types`](#l029), [L039 · `babel-traverse`](#l039), [L045 · `babel-template`](#l045), [L054 · `babel-generator`](#l054), [L058 · `babel-register`](#l058), [L072 · `babel-plugin-transform-es2015-block-scoping`](#l072), [L074 · `babel-helper-define-map`](#l074), [L075 · `babel-helper-regex`](#l075), [L094 · `@babel/helper-regex`](#l094)
  - 조사 당시 배포본: [babel-cli@6.26.0](https://registry.npmjs.org/babel-cli/6.26.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [408,726회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-cli) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l139"></a>

- [ ] **[L139] `callsite-record`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [inikulin/source-frame](https://github.com/inikulin/source-frame)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [callsite-record@4.1.5](https://registry.npmjs.org/callsite-record/4.1.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash 4.6.1 || ^4.16.1`, `@types/lodash ^4.14.72`
  - 조사 당시 인기: 주간 다운로드 [407,451회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/callsite-record) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l140"></a>

- [ ] **[L140] `gulp-header`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [gulp-community/gulp-header](https://github.com/gulp-community/gulp-header)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gulp-header@2.0.12](https://registry.npmjs.org/gulp-header/2.0.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [400,342회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gulp-header) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l141"></a>

- [ ] **[L141] `n8n-workflow`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [n8n-io/n8n](https://github.com/n8n-io/n8n)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [n8n-workflow@2.16.0](https://registry.npmjs.org/n8n-workflow/2.16.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash 4.17.23` / **devDependencies**: `@types/lodash 4.17.17`
  - 조사 당시 인기: 주간 다운로드 [399,056회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/n8n-workflow) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l142"></a>

- [ ] **[L142] `semantic-ui-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Semantic-Org/Semantic-UI-React](https://github.com/Semantic-Org/Semantic-UI-React)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [semantic-ui-react@2.1.5](https://registry.npmjs.org/semantic-ui-react/2.1.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [379,770회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/semantic-ui-react) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l143"></a>

- [ ] **[L143] `miragejs`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [miragejs/miragejs](https://github.com/miragejs/miragejs)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [miragejs@0.1.48](https://registry.npmjs.org/miragejs/0.1.48) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.0.0`
  - 조사 당시 인기: 주간 다운로드 [377,642회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/miragejs) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l144"></a>

- [ ] **[L144] `@milkdown/plugin-listener`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Milkdown/milkdown](https://github.com/Milkdown/milkdown)
  - 같은 저장소 항목: [L147 · `@milkdown/plugin-slash`](#l147), [L148 · `@milkdown/plugin-tooltip`](#l148), [L149 · `@milkdown/components`](#l149), [L150 · `@milkdown/plugin-block`](#l150), [L294 · `@milkdown/crepe`](#l294)
  - 조사 당시 배포본: [@milkdown/plugin-listener@7.22.1](https://registry.npmjs.org/%40milkdown%2Fplugin-listener/7.22.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [372,766회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40milkdown%2Fplugin-listener) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l145"></a>

- [ ] **[L145] `@univerjs/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [dream-num/univer](https://github.com/dream-num/univer)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@univerjs/core@0.25.1](https://registry.npmjs.org/%40univerjs%2Fcore/0.25.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.18.1` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [366,913회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40univerjs%2Fcore) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l146"></a>

- [ ] **[L146] `devcert`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [davewasmer/devcert](https://github.com/davewasmer/devcert)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [devcert@1.2.3](https://registry.npmjs.org/devcert/1.2.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`, `@types/lodash ^4.14.92`
  - 조사 당시 인기: 주간 다운로드 [364,457회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/devcert) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l147"></a>

- [ ] **[L147] `@milkdown/plugin-slash`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Milkdown/milkdown](https://github.com/Milkdown/milkdown)
  - 같은 저장소 항목: [L144 · `@milkdown/plugin-listener`](#l144), [L148 · `@milkdown/plugin-tooltip`](#l148), [L149 · `@milkdown/components`](#l149), [L150 · `@milkdown/plugin-block`](#l150), [L294 · `@milkdown/crepe`](#l294)
  - 조사 당시 배포본: [@milkdown/plugin-slash@7.22.1](https://registry.npmjs.org/%40milkdown%2Fplugin-slash/7.22.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [363,618회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40milkdown%2Fplugin-slash) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l148"></a>

- [ ] **[L148] `@milkdown/plugin-tooltip`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Milkdown/milkdown](https://github.com/Milkdown/milkdown)
  - 같은 저장소 항목: [L144 · `@milkdown/plugin-listener`](#l144), [L147 · `@milkdown/plugin-slash`](#l147), [L149 · `@milkdown/components`](#l149), [L150 · `@milkdown/plugin-block`](#l150), [L294 · `@milkdown/crepe`](#l294)
  - 조사 당시 배포본: [@milkdown/plugin-tooltip@7.22.1](https://registry.npmjs.org/%40milkdown%2Fplugin-tooltip/7.22.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [356,109회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40milkdown%2Fplugin-tooltip) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l149"></a>

- [ ] **[L149] `@milkdown/components`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Milkdown/milkdown](https://github.com/Milkdown/milkdown)
  - 같은 저장소 항목: [L144 · `@milkdown/plugin-listener`](#l144), [L147 · `@milkdown/plugin-slash`](#l147), [L148 · `@milkdown/plugin-tooltip`](#l148), [L150 · `@milkdown/plugin-block`](#l150), [L294 · `@milkdown/crepe`](#l294)
  - 조사 당시 배포본: [@milkdown/components@7.22.1](https://registry.npmjs.org/%40milkdown%2Fcomponents/7.22.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [354,032회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40milkdown%2Fcomponents) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l150"></a>

- [ ] **[L150] `@milkdown/plugin-block`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Milkdown/milkdown](https://github.com/Milkdown/milkdown)
  - 같은 저장소 항목: [L144 · `@milkdown/plugin-listener`](#l144), [L147 · `@milkdown/plugin-slash`](#l147), [L148 · `@milkdown/plugin-tooltip`](#l148), [L149 · `@milkdown/components`](#l149), [L294 · `@milkdown/crepe`](#l294)
  - 조사 당시 배포본: [@milkdown/plugin-block@7.22.1](https://registry.npmjs.org/%40milkdown%2Fplugin-block/7.22.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [352,914회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40milkdown%2Fplugin-block) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l151"></a>

- [ ] **[L151] `apollo-language-server`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [apollographql/apollo-tooling](https://github.com/apollographql/apollo-tooling)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [apollo-language-server@1.26.9](https://registry.npmjs.org/apollo-language-server/1.26.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.1`, `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 [346,291회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/apollo-language-server) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l152"></a>

- [ ] **[L152] `graphql-jit`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [zalando-incubator/graphql-jit](https://github.com/zalando-incubator/graphql-jit)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [graphql-jit@0.8.9](https://registry.npmjs.org/graphql-jit/0.8.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge 4.6.2`, `lodash.memoize ^4.1.2`, `lodash.mergewith 4.6.2` / **devDependencies**: `@types/lodash.merge ^4.6.7`, `@types/lodash.memoize ^4.1.7`, `@types/lodash.mergewith ^4.6.7`
  - 조사 당시 인기: 주간 다운로드 [329,369회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/graphql-jit) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l153"></a>

- [ ] **[L153] `eslint-ast-utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jfmengels/eslint-ast-utils](https://github.com/jfmengels/eslint-ast-utils)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [eslint-ast-utils@1.1.0](https://registry.npmjs.org/eslint-ast-utils/1.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`, `lodash.zip ^4.2.0`
  - 조사 당시 인기: 주간 다운로드 [327,178회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-ast-utils) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l154"></a>

- [ ] **[L154] `deep-for-each`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [moxystudio/js-deep-for-each](https://github.com/moxystudio/js-deep-for-each)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [deep-for-each@3.0.0](https://registry.npmjs.org/deep-for-each/3.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [322,963회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/deep-for-each) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l155"></a>

- [ ] **[L155] `@antv/path-util`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [antvis/util](https://github.com/antvis/util)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@antv/path-util@3.0.1](https://registry.npmjs.org/%40antv%2Fpath-util/3.0.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.6`
  - 조사 당시 인기: 주간 다운로드 [306,660회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40antv%2Fpath-util) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l156"></a>

- [ ] **[L156] `broccoli-concat`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [broccolijs/broccoli-concat](https://github.com/broccolijs/broccoli-concat)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [broccoli-concat@4.2.7](https://registry.npmjs.org/broccoli-concat/4.2.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.23`
  - 조사 당시 인기: 주간 다운로드 [301,781회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/broccoli-concat) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l157"></a>

- [ ] **[L157] `ember-cli`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ember-cli/ember-cli](https://github.com/ember-cli/ember-cli)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [ember-cli@7.2.0](https://registry.npmjs.org/ember-cli/7.2.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [291,424회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ember-cli) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l158"></a>

- [ ] **[L158] `filestack-js`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [filestack/filestack-js](https://github.com/filestack/filestack-js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [filestack-js@3.51.6](https://registry.npmjs.org/filestack-js/3.51.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0` / **devDependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [291,040회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/filestack-js) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l159"></a>

- [ ] **[L159] `testem`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [testem/testem](https://github.com/testem/testem)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [testem@3.20.2](https://registry.npmjs.org/testem/3.20.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 [290,076회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/testem) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l160"></a>

- [ ] **[L160] `v-calendar`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nathanreyes/v-calendar](https://github.com/nathanreyes/v-calendar)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [v-calendar@2.4.2](https://registry.npmjs.org/v-calendar/2.4.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [271,347회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/v-calendar) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l161"></a>

- [ ] **[L161] `aos`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [michalsnik/aos](https://github.com/michalsnik/aos)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [aos@2.3.4](https://registry.npmjs.org/aos/2.3.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.6`, `lodash.throttle ^4.0.1`
  - 조사 당시 인기: 주간 다운로드 [267,730회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/aos) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l162"></a>

- [ ] **[L162] `stream-chat-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [GetStream/stream-chat-react](https://github.com/GetStream/stream-chat-react)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [stream-chat-react@14.12.0](https://registry.npmjs.org/stream-chat-react/14.12.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.uniqby ^4.7.0`, `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1`, `lodash.mergewith ^4.6.2` / **devDependencies**: `@types/lodash.uniqby ^4.7.9`, `@types/lodash.debounce ^4.0.9`, `@types/lodash.throttle ^4.1.9`, `@types/lodash.mergewith ^4.6.9`
  - 조사 당시 인기: 주간 다운로드 [261,581회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/stream-chat-react) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l163"></a>

- [ ] **[L163] `@ant-design/pro-utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/pro-components](https://github.com/ant-design/pro-components)
  - 같은 저장소 항목: [L166 · `@ant-design/pro-layout`](#l166), [L200 · `@ant-design/pro-form`](#l200), [L201 · `@ant-design/pro-field`](#l201), [L202 · `@ant-design/pro-table`](#l202)
  - 조사 당시 배포본: [@ant-design/pro-utils@2.18.0](https://registry.npmjs.org/%40ant-design%2Fpro-utils/2.18.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.10`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [258,927회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fpro-utils) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l164"></a>

- [ ] **[L164] `eslint-plugin-ember`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ember-cli/eslint-plugin-ember](https://github.com/ember-cli/eslint-plugin-ember)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [eslint-plugin-ember@13.5.0](https://registry.npmjs.org/eslint-plugin-ember/13.5.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0`, `lodash.kebabcase ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [257,037회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-plugin-ember) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l165"></a>

- [ ] **[L165] `@ant-design/plots`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/ant-design-charts](https://github.com/ant-design/ant-design-charts)
  - 같은 저장소 항목: [L205 · `@ant-design/charts`](#l205)
  - 조사 당시 배포본: [@ant-design/plots@2.6.8](https://registry.npmjs.org/%40ant-design%2Fplots/2.6.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [254,898회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fplots) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l166"></a>

- [ ] **[L166] `@ant-design/pro-layout`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/pro-components](https://github.com/ant-design/pro-components)
  - 같은 저장소 항목: [L163 · `@ant-design/pro-utils`](#l163), [L200 · `@ant-design/pro-form`](#l200), [L201 · `@ant-design/pro-field`](#l201), [L202 · `@ant-design/pro-table`](#l202)
  - 조사 당시 배포본: [@ant-design/pro-layout@7.22.7](https://registry.npmjs.org/%40ant-design%2Fpro-layout/7.22.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.10`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [250,293회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fpro-layout) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l167"></a>

- [ ] **[L167] `allotment`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [johnwalley/allotment](https://github.com/johnwalley/allotment)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [allotment@1.20.5](https://registry.npmjs.org/allotment/1.20.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clamp ^4.0.0`, `lodash.debounce ^4.0.0` / **devDependencies**: `@types/lodash.clamp 4.0.9`, `@types/lodash.debounce 4.0.9`
  - 조사 당시 인기: 주간 다운로드 [249,158회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/allotment) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l168"></a>

- [ ] **[L168] `vue-server-renderer`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vuejs/vue](https://github.com/vuejs/vue)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [vue-server-renderer@2.7.16](https://registry.npmjs.org/vue-server-renderer/2.7.16) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.uniq ^4.5.0`, `lodash.template ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [248,636회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/vue-server-renderer) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l169"></a>

- [ ] **[L169] `markdown-it-terminal`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [trabus/markdown-it-terminal](https://github.com/trabus/markdown-it-terminal)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [markdown-it-terminal@0.4.0](https://registry.npmjs.org/markdown-it-terminal/0.4.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [242,310회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/markdown-it-terminal) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l170"></a>

- [ ] **[L170] `react-proxy`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [gaearon/react-proxy](https://github.com/gaearon/react-proxy)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-proxy@1.1.8](https://registry.npmjs.org/react-proxy/1.1.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.6.1`
  - 조사 당시 인기: 주간 다운로드 [240,944회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-proxy) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l171"></a>

- [ ] **[L171] `yam`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [twokul/yam](https://github.com/twokul/yam)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [yam@1.0.0](https://registry.npmjs.org/yam/1.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.0`
  - 조사 당시 인기: 주간 다운로드 [236,507회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/yam) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l172"></a>

- [ ] **[L172] `winston-cloudwatch`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [lazywithclass/winston-cloudwatch](https://github.com/lazywithclass/winston-cloudwatch)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [winston-cloudwatch@6.3.0](https://registry.npmjs.org/winston-cloudwatch/6.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.find ^4.6.0`, `lodash.assign ^4.2.0`, `lodash.isempty ^4.4.0`, `lodash.iserror ^3.1.1`
  - 조사 당시 인기: 주간 다운로드 [236,339회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/winston-cloudwatch) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l173"></a>

- [ ] **[L173] `elasticsearch`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [elastic/elasticsearch-js-legacy](https://github.com/elastic/elasticsearch-js-legacy)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [elasticsearch@16.7.3](https://registry.npmjs.org/elasticsearch/16.7.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.10`
  - 조사 당시 인기: 주간 다운로드 [235,750회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/elasticsearch) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - npm 배포 중단 안내: Package no longer supported. Contact Support at https://www.npmjs.com/support for more info.

<a id="l174"></a>

- [ ] **[L174] `svg-sprite`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [svg-sprite/svg-sprite](https://github.com/svg-sprite/svg-sprite)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [svg-sprite@2.0.4](https://registry.npmjs.org/svg-sprite/2.0.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`, `lodash.escape ^4.0.1`
  - 조사 당시 인기: 주간 다운로드 [227,322회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/svg-sprite) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l175"></a>

- [ ] **[L175] `snyk-nodejs-lockfile-parser`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [snyk/nodejs-lockfile-parser](https://github.com/snyk/nodejs-lockfile-parser)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [snyk-nodejs-lockfile-parser@2.10.4](https://registry.npmjs.org/snyk-nodejs-lockfile-parser/2.10.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.flatmap ^4.5.0`, `lodash.isempty ^4.4.0`, `lodash.topairs ^4.3.0`, `lodash.clonedeep ^4.5.0` / **devDependencies**: `@types/lodash ^4.17.20`
  - 조사 당시 인기: 주간 다운로드 [227,031회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/snyk-nodejs-lockfile-parser) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l176"></a>

- [ ] **[L176] `koa-ip`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nswbmw/koa-ip](https://github.com/nswbmw/koa-ip)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [koa-ip@2.1.4](https://registry.npmjs.org/koa-ip/2.1.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isplainobject 4.0.6`
  - 조사 당시 인기: 주간 다운로드 [226,130회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/koa-ip) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l177"></a>

- [ ] **[L177] `rest-facade`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ngonzalvez/rest-facade](https://github.com/ngonzalvez/rest-facade)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rest-facade@1.16.4](https://registry.npmjs.org/rest-facade/1.16.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`
  - 조사 당시 인기: 주간 다운로드 [220,056회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rest-facade) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l178"></a>

- [ ] **[L178] `react-bootstrap-typeahead`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ericgio/react-bootstrap-typeahead](https://github.com/ericgio/react-bootstrap-typeahead)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-bootstrap-typeahead@6.4.1](https://registry.npmjs.org/react-bootstrap-typeahead/6.4.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8` / **devDependencies**: `lodash ^4.17.11`, `@types/lodash.debounce ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [213,167회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-bootstrap-typeahead) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l179"></a>

- [ ] **[L179] `qase-javascript-commons`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [qase-tms/qase-javascript](https://github.com/qase-tms/qase-javascript)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [qase-javascript-commons@2.9.2](https://registry.npmjs.org/qase-javascript-commons/2.9.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`, `lodash.mergewith ^4.6.2` / **devDependencies**: `@types/lodash.merge ^4.6.9`, `@types/lodash.mergewith ^4.6.9`
  - 조사 당시 인기: 주간 다운로드 [210,681회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/qase-javascript-commons) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l180"></a>

- [ ] **[L180] `devextreme-quill`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [DevExpress/devextreme-quill](https://github.com/DevExpress/devextreme-quill)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [devextreme-quill@1.8.0](https://registry.npmjs.org/devextreme-quill/1.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`, `lodash.clonedeep ^4.5.0` / **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [209,710회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/devextreme-quill) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l181"></a>

- [ ] **[L181] `@refinedev/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [refinedev/refine](https://github.com/refinedev/refine)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@refinedev/core@5.0.12](https://registry.npmjs.org/%40refinedev%2Fcore/5.0.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.14.171`
  - 조사 당시 인기: 주간 다운로드 [209,558회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40refinedev%2Fcore) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l182"></a>

- [ ] **[L182] `react-places-autocomplete`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [kenny-hibino/react-places-autocomplete](https://github.com/kenny-hibino/react-places-autocomplete)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-places-autocomplete@7.3.0](https://registry.npmjs.org/react-places-autocomplete/7.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 [209,503회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-places-autocomplete) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l183"></a>

- [ ] **[L183] `parse-prefer-header`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ppaskaris/node-parse-prefer-header](https://github.com/ppaskaris/node-parse-prefer-header)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [parse-prefer-header@1.0.0](https://registry.npmjs.org/parse-prefer-header/1.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.camelcase ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [204,585회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/parse-prefer-header) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l184"></a>

- [ ] **[L184] `rc-form`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [react-component/form](https://github.com/react-component/form)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rc-form@2.4.12](https://registry.npmjs.org/rc-form/2.4.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [202,857회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rc-form) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l185"></a>

- [ ] **[L185] `ant-design-vue`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vueComponent/ant-design-vue](https://github.com/vueComponent/ant-design-vue)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [ant-design-vue@4.2.6](https://registry.npmjs.org/ant-design-vue/4.2.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.15` / **devDependencies**: `@types/lodash-es ^4.17.3`
  - 조사 당시 인기: 주간 다운로드 [199,332회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ant-design-vue) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l186"></a>

- [ ] **[L186] `rooks`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [imbhargav5/rooks](https://github.com/imbhargav5/rooks)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rooks@9.9.0](https://registry.npmjs.org/rooks/9.9.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8` / **devDependencies**: `@types/lodash ^4.17.24`, `lodash.sortby ^4.7.0`, `lodash.truncate ^4.4.2`, `lodash.capitalize 4.2.1`, `@types/lodash.debounce ^4.0.9`
  - 조사 당시 인기: 주간 다운로드 [194,816회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rooks) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l187"></a>

- [ ] **[L187] `rsuite`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rsuite/rsuite](https://github.com/rsuite/rsuite)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rsuite@6.2.4](https://registry.npmjs.org/rsuite/6.2.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `@types/lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [190,577회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rsuite) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l188"></a>

- [ ] **[L188] `to-json-schema`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ruzicka/to-json-schema](https://github.com/ruzicka/to-json-schema)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [to-json-schema@0.2.5](https://registry.npmjs.org/to-json-schema/0.2.5) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.xor ^4.5.0`, `lodash.keys ^4.2.0`, `lodash.omit ^4.5.0`, `lodash.merge ^4.6.2`, `lodash.isequal ^4.5.0`, `lodash.without ^4.4.0` / **devDependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [190,302회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/to-json-schema) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l189"></a>

- [ ] **[L189] `insight`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sindresorhus/insight](https://github.com/sindresorhus/insight)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [insight@0.12.0](https://registry.npmjs.org/insight/0.12.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 [188,453회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/insight) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l190"></a>

- [ ] **[L190] `create-eslint-index`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jfmengels/create-eslint-index](https://github.com/jfmengels/create-eslint-index)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [create-eslint-index@1.0.0](https://registry.npmjs.org/create-eslint-index/1.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [184,903회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/create-eslint-index) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l191"></a>

- [ ] **[L191] `hard-source-webpack-plugin`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [mzgoddard/hard-source-webpack-plugin](https://github.com/mzgoddard/hard-source-webpack-plugin)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [hard-source-webpack-plugin@0.13.1](https://registry.npmjs.org/hard-source-webpack-plugin/0.13.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.15.0`
  - 조사 당시 인기: 주간 다운로드 [180,205회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/hard-source-webpack-plugin) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l192"></a>

- [ ] **[L192] `gulp-shell`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sun-zheng-an/gulp-shell](https://github.com/sun-zheng-an/gulp-shell)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gulp-shell@0.8.0](https://registry.npmjs.org/gulp-shell/0.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.template ^4.5.0` / **devDependencies**: `@types/lodash.template ^4.4.6`
  - 조사 당시 인기: 주간 다운로드 [177,975회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gulp-shell) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l193"></a>

- [ ] **[L193] `powerbi-client-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [microsoft/powerbi-client-react](https://github.com/microsoft/powerbi-client-react)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [powerbi-client-react@2.0.2](https://registry.npmjs.org/powerbi-client-react/2.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0` / **devDependencies**: `@types/lodash.isequal ^4.5.8`
  - 조사 당시 인기: 주간 다운로드 [171,829회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/powerbi-client-react) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l194"></a>

- [ ] **[L194] `ngrok`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bubenshchykov/ngrok](https://github.com/bubenshchykov/ngrok)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [ngrok@5.0.0-beta.2](https://registry.npmjs.org/ngrok/5.0.0-beta.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [167,238회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ngrok) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l195"></a>

- [ ] **[L195] `react-native-picker-select`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [lawnstarter/react-native-picker-select](https://github.com/lawnstarter/react-native-picker-select)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-native-picker-select@9.3.1](https://registry.npmjs.org/react-native-picker-select/9.3.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0`, `lodash.isobject ^3.0.2`
  - 조사 당시 인기: 주간 다운로드 [166,693회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-native-picker-select) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l196"></a>

- [ ] **[L196] `gulp-svgmin`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ben-eb/gulp-svgmin](https://github.com/ben-eb/gulp-svgmin)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gulp-svgmin@4.1.0](https://registry.npmjs.org/gulp-svgmin/4.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [166,111회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gulp-svgmin) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l197"></a>

- [ ] **[L197] `class-validator-jsonschema`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [epiphone/class-validator-jsonschema](https://github.com/epiphone/class-validator-jsonschema)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [class-validator-jsonschema@5.1.0](https://registry.npmjs.org/class-validator-jsonschema/5.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`, `lodash.groupby ^4.6.0` / **devDependencies**: `lodash.get ^4.4.2`, `@types/lodash.get ^4.4.7`, `@types/lodash.merge ^4.6.7`, `@types/lodash.groupby ^4.6.7`
  - 조사 당시 인기: 주간 다운로드 [165,963회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/class-validator-jsonschema) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l198"></a>

- [ ] **[L198] `naive-ui`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [tusen-ai/naive-ui](https://github.com/tusen-ai/naive-ui)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [naive-ui@2.45.3](https://registry.npmjs.org/naive-ui/2.45.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21`, `@types/lodash ^4.17.20`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [158,165회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/naive-ui) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l199"></a>

- [ ] **[L199] `npm-name`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sindresorhus/npm-name](https://github.com/sindresorhus/npm-name)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [npm-name@8.1.1](https://registry.npmjs.org/npm-name/8.1.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.zip ^4.2.0`
  - 조사 당시 인기: 주간 다운로드 [155,946회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/npm-name) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l200"></a>

- [ ] **[L200] `@ant-design/pro-form`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/pro-components](https://github.com/ant-design/pro-components)
  - 같은 저장소 항목: [L163 · `@ant-design/pro-utils`](#l163), [L166 · `@ant-design/pro-layout`](#l166), [L201 · `@ant-design/pro-field`](#l201), [L202 · `@ant-design/pro-table`](#l202)
  - 조사 당시 배포본: [@ant-design/pro-form@2.32.0](https://registry.npmjs.org/%40ant-design%2Fpro-form/2.32.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.10`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [154,710회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fpro-form) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l201"></a>

- [ ] **[L201] `@ant-design/pro-field`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/pro-components](https://github.com/ant-design/pro-components)
  - 같은 저장소 항목: [L163 · `@ant-design/pro-utils`](#l163), [L166 · `@ant-design/pro-layout`](#l166), [L200 · `@ant-design/pro-form`](#l200), [L202 · `@ant-design/pro-table`](#l202)
  - 조사 당시 배포본: [@ant-design/pro-field@3.1.0](https://registry.npmjs.org/%40ant-design%2Fpro-field/3.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.10`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [152,746회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fpro-field) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l202"></a>

- [ ] **[L202] `@ant-design/pro-table`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/pro-components](https://github.com/ant-design/pro-components)
  - 같은 저장소 항목: [L163 · `@ant-design/pro-utils`](#l163), [L166 · `@ant-design/pro-layout`](#l166), [L200 · `@ant-design/pro-form`](#l200), [L201 · `@ant-design/pro-field`](#l201)
  - 조사 당시 배포본: [@ant-design/pro-table@3.21.0](https://registry.npmjs.org/%40ant-design%2Fpro-table/3.21.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.10`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [150,900회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fpro-table) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l203"></a>

- [ ] **[L203] `video-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [video-react/video-react](https://github.com/video-react/video-react)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [video-react@0.16.0](https://registry.npmjs.org/video-react/0.16.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [148,021회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/video-react) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l204"></a>

- [ ] **[L204] `archetype`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [boosterfuels/archetype](https://github.com/boosterfuels/archetype)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [archetype@0.13.1](https://registry.npmjs.org/archetype/0.13.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash 4.x`
  - 조사 당시 인기: 주간 다운로드 [145,714회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/archetype) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l205"></a>

- [ ] **[L205] `@ant-design/charts`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/ant-design-charts](https://github.com/ant-design/ant-design-charts)
  - 같은 저장소 항목: [L165 · `@ant-design/plots`](#l165)
  - 조사 당시 배포본: [@ant-design/charts@2.6.7](https://registry.npmjs.org/%40ant-design%2Fcharts/2.6.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [142,430회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Fcharts) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l206"></a>

- [ ] **[L206] `babel-plugin-inline-react-svg`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [kesne/babel-plugin-inline-react-svg](https://github.com/kesne/babel-plugin-inline-react-svg)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [babel-plugin-inline-react-svg@2.0.2](https://registry.npmjs.org/babel-plugin-inline-react-svg/2.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [141,424회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-plugin-inline-react-svg) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l207"></a>

- [ ] **[L207] `bhttp`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [http://git.cryto.net/joepie91/node-bhttp.git](http://git.cryto.net/joepie91/node-bhttp.git)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [bhttp@1.2.8](https://registry.npmjs.org/bhttp/1.2.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`, `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [140,680회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/bhttp) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l208"></a>

- [ ] **[L208] `@nuxt/utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L213 · `@nuxt/config`](#l213), [L214 · `@nuxt/vue-renderer`](#l214), [L215 · `@nuxt/core`](#l215), [L216 · `@nuxt/webpack`](#l216), [L217 · `@nuxt/builder`](#l217), [L336 · `@nuxt/kit-edge`](#l336)
  - 조사 당시 배포본: [@nuxt/utils@2.18.1](https://registry.npmjs.org/%40nuxt%2Futils/2.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [140,572회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nuxt%2Futils) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l209"></a>

- [ ] **[L209] `microbundle`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [developit/microbundle](https://github.com/developit/microbundle)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [microbundle@0.15.1](https://registry.npmjs.org/microbundle/0.15.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [139,067회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/microbundle) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l210"></a>

- [ ] **[L210] `flux-standard-action`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [redux-utilities/flux-standard-action](https://github.com/redux-utilities/flux-standard-action)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [flux-standard-action@2.1.2](https://registry.npmjs.org/flux-standard-action/2.1.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isstring ^4.0.1`, `lodash.isplainobject ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [135,096회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/flux-standard-action) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l211"></a>

- [ ] **[L211] `babel-plugin-tester`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [babel-utils/babel-plugin-tester](https://github.com/babel-utils/babel-plugin-tester)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [babel-plugin-tester@12.0.0](https://registry.npmjs.org/babel-plugin-tester/12.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.mergewith ^4.6.2` / **devDependencies**: `@types/lodash.mergewith ^4.6.9`
  - 조사 당시 인기: 주간 다운로드 [134,900회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/babel-plugin-tester) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l212"></a>

- [ ] **[L212] `api`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [readmeio/api](https://github.com/readmeio/api)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [api@7.0.2](https://registry.npmjs.org/api/7.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.18.1` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [133,431회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/api) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l213"></a>

- [ ] **[L213] `@nuxt/config`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L208 · `@nuxt/utils`](#l208), [L214 · `@nuxt/vue-renderer`](#l214), [L215 · `@nuxt/core`](#l215), [L216 · `@nuxt/webpack`](#l216), [L217 · `@nuxt/builder`](#l217), [L336 · `@nuxt/kit-edge`](#l336)
  - 조사 당시 배포본: [@nuxt/config@2.18.1](https://registry.npmjs.org/%40nuxt%2Fconfig/2.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [128,670회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nuxt%2Fconfig) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l214"></a>

- [ ] **[L214] `@nuxt/vue-renderer`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L208 · `@nuxt/utils`](#l208), [L213 · `@nuxt/config`](#l213), [L215 · `@nuxt/core`](#l215), [L216 · `@nuxt/webpack`](#l216), [L217 · `@nuxt/builder`](#l217), [L336 · `@nuxt/kit-edge`](#l336)
  - 조사 당시 배포본: [@nuxt/vue-renderer@2.18.1](https://registry.npmjs.org/%40nuxt%2Fvue-renderer/2.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [127,415회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nuxt%2Fvue-renderer) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l215"></a>

- [ ] **[L215] `@nuxt/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L208 · `@nuxt/utils`](#l208), [L213 · `@nuxt/config`](#l213), [L214 · `@nuxt/vue-renderer`](#l214), [L216 · `@nuxt/webpack`](#l216), [L217 · `@nuxt/builder`](#l217), [L336 · `@nuxt/kit-edge`](#l336)
  - 조사 당시 배포본: [@nuxt/core@2.18.1](https://registry.npmjs.org/%40nuxt%2Fcore/2.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [127,319회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nuxt%2Fcore) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l216"></a>

- [ ] **[L216] `@nuxt/webpack`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L208 · `@nuxt/utils`](#l208), [L213 · `@nuxt/config`](#l213), [L214 · `@nuxt/vue-renderer`](#l214), [L215 · `@nuxt/core`](#l215), [L217 · `@nuxt/builder`](#l217), [L336 · `@nuxt/kit-edge`](#l336)
  - 조사 당시 배포본: [@nuxt/webpack@2.18.1](https://registry.npmjs.org/%40nuxt%2Fwebpack/2.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [126,764회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nuxt%2Fwebpack) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l217"></a>

- [ ] **[L217] `@nuxt/builder`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L208 · `@nuxt/utils`](#l208), [L213 · `@nuxt/config`](#l213), [L214 · `@nuxt/vue-renderer`](#l214), [L215 · `@nuxt/core`](#l215), [L216 · `@nuxt/webpack`](#l216), [L336 · `@nuxt/kit-edge`](#l336)
  - 조사 당시 배포본: [@nuxt/builder@2.18.1](https://registry.npmjs.org/%40nuxt%2Fbuilder/2.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [126,503회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nuxt%2Fbuilder) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l218"></a>

- [ ] **[L218] `stream-log-stats`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [75lb/stream-log-stats](https://github.com/75lb/stream-log-stats)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [stream-log-stats@3.0.2](https://registry.npmjs.org/stream-log-stats/3.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [126,223회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/stream-log-stats) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l219"></a>

- [ ] **[L219] `quill-delta-to-html`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nozer/quill-delta-to-html](https://github.com/nozer/quill-delta-to-html)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [quill-delta-to-html@0.12.1](https://registry.npmjs.org/quill-delta-to-html/0.12.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0` / **devDependencies**: `@types/lodash.isequal ^4.5.5`
  - 조사 당시 인기: 주간 다운로드 [125,583회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/quill-delta-to-html) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l220"></a>

- [ ] **[L220] `llamaindex`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [run-llama/LlamaIndexTS](https://github.com/run-llama/LlamaIndexTS)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [llamaindex@0.12.1](https://registry.npmjs.org/llamaindex/0.12.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `@types/lodash ^4.17.7`
  - 조사 당시 인기: 주간 다운로드 [125,330회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/llamaindex) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l221"></a>

- [ ] **[L221] `@daml/types`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [digital-asset/daml](https://github.com/digital-asset/daml)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@daml/types@2.10.6](https://registry.npmjs.org/%40daml%2Ftypes/2.10.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.5`, `@types/lodash ^4.5` / **devDependencies**: `lodash ^4.5`, `@types/lodash ^4.5`
  - 조사 당시 인기: 주간 다운로드 [122,665회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40daml%2Ftypes) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l222"></a>

- [ ] **[L222] `excel4node`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [advisr-io/excel4node](https://github.com/advisr-io/excel4node)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [excel4node@1.8.2](https://registry.npmjs.org/excel4node/1.8.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`, `lodash.reduce ^4.6.0`, `lodash.isequal ^4.5.0`, `lodash.uniqueid ^4.0.1`, `lodash.isundefined ^3.0.1`
  - 조사 당시 인기: 주간 다운로드 [120,998회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/excel4node) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l223"></a>

- [ ] **[L223] `selenium-standalone`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [webdriverio/selenium-standalone](https://github.com/webdriverio/selenium-standalone)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [selenium-standalone@10.0.2](https://registry.npmjs.org/selenium-standalone/10.0.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`, `lodash.mapvalues ^4.6.0` / **devDependencies**: `@types/lodash.merge ^4.6.9`, `@types/lodash.mapvalues ^4.6.9`
  - 조사 당시 인기: 주간 다운로드 [120,573회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/selenium-standalone) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l224"></a>

- [ ] **[L224] `gulp-merge-json`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [joshswan/gulp-merge-json](https://github.com/joshswan/gulp-merge-json)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gulp-merge-json@2.2.1](https://registry.npmjs.org/gulp-merge-json/2.2.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`, `lodash.mergewith ^4.6.1`
  - 조사 당시 인기: 주간 다운로드 [119,410회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gulp-merge-json) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l225"></a>

- [ ] **[L225] `nightwatch`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nightwatchjs/nightwatch](https://github.com/nightwatchjs/nightwatch)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [nightwatch@3.16.0](https://registry.npmjs.org/nightwatch/3.16.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [116,811회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/nightwatch) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l226"></a>

- [ ] **[L226] `progressbar.js`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [kimmobrunfeldt/progressbar.js](https://github.com/kimmobrunfeldt/progressbar.js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [progressbar.js@1.1.1](https://registry.npmjs.org/progressbar.js/1.1.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2` / **devDependencies**: `lodash ^2.4.1`
  - 조사 당시 인기: 주간 다운로드 [116,757회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/progressbar.js) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l227"></a>

- [ ] **[L227] `hanji`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [drizzle-team/hanji](https://github.com/drizzle-team/hanji)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [hanji@0.0.8](https://registry.npmjs.org/hanji/0.0.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1` / **devDependencies**: `@types/lodash.throttle ^4.1.7`
  - 조사 당시 인기: 주간 다운로드 [116,687회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/hanji) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l228"></a>

- [ ] **[L228] `sass-lint`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sasstools/sass-lint](https://github.com/sasstools/sass-lint)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [sass-lint@1.13.1](https://registry.npmjs.org/sass-lint/1.13.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.kebabcase ^4.0.0`, `lodash.capitalize ^4.1.0`
  - 조사 당시 인기: 주간 다운로드 [115,953회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/sass-lint) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l229"></a>

- [ ] **[L229] `throng`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [hunterloftis/throng](https://github.com/hunterloftis/throng)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [throng@5.0.0](https://registry.npmjs.org/throng/5.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.20`
  - 조사 당시 인기: 주간 다운로드 [114,171회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/throng) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l230"></a>

- [ ] **[L230] `react-masonry-component`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [eiriklv/react-masonry-component](https://github.com/eiriklv/react-masonry-component)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-masonry-component@6.3.0](https://registry.npmjs.org/react-masonry-component/6.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [113,916회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-masonry-component) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l231"></a>

- [ ] **[L231] `rcfinder`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [spenceralger/rcfinder](https://github.com/spenceralger/rcfinder)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rcfinder@0.1.9](https://registry.npmjs.org/rcfinder/0.1.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.3.2`
  - 조사 당시 인기: 주간 다운로드 [113,129회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rcfinder) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l232"></a>

- [ ] **[L232] `winston-elasticsearch`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vanthome/winston-elasticsearch](https://github.com/vanthome/winston-elasticsearch)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [winston-elasticsearch@0.19.0](https://registry.npmjs.org/winston-elasticsearch/0.19.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.omit ^4.5.0`, `lodash.defaults ^4.2.0`
  - 조사 당시 인기: 주간 다운로드 [111,297회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/winston-elasticsearch) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l233"></a>

- [ ] **[L233] `grpc`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [grpc/grpc-node](https://github.com/grpc/grpc-node)
  - 같은 저장소 항목: [L001 · `@grpc/proto-loader`](#l001)
  - 조사 당시 배포본: [grpc@1.24.11](https://registry.npmjs.org/grpc/1.24.11) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clone ^4.5.0`, `lodash.camelcase ^4.3.0` / **devDependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [111,036회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/grpc) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - npm 배포 중단 안내: This library will not receive further updates other than security fixes. We recommend using @grpc/grpc-js instead.

<a id="l234"></a>

- [ ] **[L234] `auto-config-loader`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jaywcjlove/auto-config-loader](https://github.com/jaywcjlove/auto-config-loader)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [auto-config-loader@3.0.4](https://registry.npmjs.org/auto-config-loader/3.0.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2` / **devDependencies**: `@types/lodash.merge ^4.6.9`
  - 조사 당시 인기: 주간 다운로드 [109,785회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/auto-config-loader) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l235"></a>

- [ ] **[L235] `lodash-webpack-plugin`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [lodash/lodash-webpack-plugin](https://github.com/lodash/lodash-webpack-plugin)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [lodash-webpack-plugin@0.11.6](https://registry.npmjs.org/lodash-webpack-plugin/0.11.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.20`
  - 조사 당시 인기: 주간 다운로드 [108,170회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/lodash-webpack-plugin) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l236"></a>

- [ ] **[L236] `rcloader`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [spenceralger/rcloader](https://github.com/spenceralger/rcloader)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rcloader@0.2.2](https://registry.npmjs.org/rcloader/0.2.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.0`, `lodash.assign ^4.2.0`, `lodash.isobject ^3.0.2`
  - 조사 당시 인기: 주간 다운로드 [107,791회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rcloader) / 저장소 스타 미조회 · 통과 기준: 다운로드
  - npm 배포 중단 안내: Package no longer supported. Contact Support at https://www.npmjs.com/support for more info.

<a id="l237"></a>

- [ ] **[L237] `react-dock`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [reduxjs/redux-devtools](https://github.com/reduxjs/redux-devtools)
  - 같은 저장소 항목: [L033 · `react-base16-styling`](#l033), [L095 · `react-json-tree`](#l095), [L253 · `redux-devtools-log-monitor`](#l253), [L291 · `@redux-devtools/log-monitor`](#l291)
  - 조사 당시 배포본: [react-dock@0.8.0](https://registry.npmjs.org/react-dock/0.8.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [106,321회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-dock) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l238"></a>

- [ ] **[L238] `@antv/x6`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [antvis/x6](https://github.com/antvis/x6)
  - 같은 저장소 항목: [L254 · `@antv/x6-common`](#l254)
  - 조사 당시 배포본: [@antv/x6@3.1.8](https://registry.npmjs.org/%40antv%2Fx6/3.1.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.15` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 [100,066회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40antv%2Fx6) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l239"></a>

- [ ] **[L239] `bookshelf`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bookshelf/bookshelf](https://github.com/bookshelf/bookshelf)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [bookshelf@1.2.0](https://registry.npmjs.org/bookshelf/1.2.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [74,995회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/bookshelf) / 저장소 스타 [6,347개](https://api.github.com/repos/bookshelf/bookshelf) · 통과 기준: 스타

<a id="l240"></a>

- [ ] **[L240] `material-ui`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [callemall/material-ui](https://github.com/callemall/material-ui)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [material-ui@0.20.2](https://registry.npmjs.org/material-ui/0.20.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.0`, `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [68,901회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/material-ui) / 저장소 스타 [98,957개](https://deps.dev/_/s/npm/p/material-ui) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T05:56:12+00:00
  - npm 배포 중단 안내: You can now upgrade to @material-ui/core

<a id="l241"></a>

- [ ] **[L241] `reactour`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [elrumordelaluz/reactour](https://github.com/elrumordelaluz/reactour)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [reactour@1.19.4](https://registry.npmjs.org/reactour/1.19.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce 4.0.8`
  - 조사 당시 인기: 주간 다운로드 [66,436회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/reactour) / 저장소 스타 [4,086개](https://deps.dev/_/s/npm/p/reactour) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T08:19:41+00:00

<a id="l242"></a>

- [ ] **[L242] `twin.macro`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ben-rogerson/twin.macro](https://github.com/ben-rogerson/twin.macro)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [twin.macro@3.4.1](https://registry.npmjs.org/twin.macro/3.4.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`, `lodash.merge ^4.6.2` / **devDependencies**: `@types/lodash.get ^4.4.7`, `@types/lodash.merge ^4.6.7`, `@types/lodash.flatmap ^4.5.7`
  - 조사 당시 인기: 주간 다운로드 [66,398회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/twin.macro) / 저장소 스타 [8,027개](https://deps.dev/_/s/npm/p/twin.macro) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-21T15:51:47+00:00

<a id="l243"></a>

- [ ] **[L243] `caporal`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [mattallty/Caporal.js](https://github.com/mattallty/Caporal.js)
  - 같은 저장소 항목: [L255 · `@caporal/core`](#l255)
  - 조사 당시 배포본: [caporal@1.4.0](https://registry.npmjs.org/caporal/1.4.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.14`
  - 조사 당시 인기: 주간 다운로드 [63,120회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/caporal) / 저장소 스타 [3,450개](https://deps.dev/_/s/npm/p/caporal) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-14T22:59:53+00:00

<a id="l244"></a>

- [ ] **[L244] `@vx/responsive`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [hshoff/vx](https://github.com/hshoff/vx)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@vx/responsive@0.0.199](https://registry.npmjs.org/%40vx%2Fresponsive/0.0.199) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.10`, `@types/lodash ^4.14.146`
  - 조사 당시 인기: 주간 다운로드 [62,643회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40vx%2Fresponsive) / 저장소 스타 [21,028개](https://deps.dev/_/s/npm/p/%40vx%2Fresponsive) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T23:52:27+00:00

<a id="l245"></a>

- [ ] **[L245] `carbon-components`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [carbon-design-system/carbon](https://github.com/carbon-design-system/carbon)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [carbon-components@10.58.15](https://registry.npmjs.org/carbon-components/10.58.15) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 [62,035회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/carbon-components) / 저장소 스타 [9,392개](https://deps.dev/_/s/npm/p/carbon-components) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T06:32:31+00:00
  - npm 배포 중단 안내: This package is no longer supported. More info at https://carbondesignsystem.com/deprecations/

<a id="l246"></a>

- [ ] **[L246] `dumi`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [umijs/dumi](https://github.com/umijs/dumi)
  - 같은 저장소 항목: [L260 · `dumi-theme-default`](#l260), [L303 · `@umijs/preset-dumi`](#l303)
  - 조사 당시 배포본: [dumi@2.4.49](https://registry.npmjs.org/dumi/2.4.49) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1` / **devDependencies**: `@types/lodash.throttle ^4.1.7`
  - 조사 당시 인기: 주간 다운로드 [57,242회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/dumi) / 저장소 스타 [3,795개](https://deps.dev/_/s/npm/p/dumi) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-03T11:06:56+00:00

<a id="l247"></a>

- [ ] **[L247] `generator-jhipster`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jhipster/generator-jhipster](https://github.com/jhipster/generator-jhipster)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [generator-jhipster@9.3.0](https://registry.npmjs.org/generator-jhipster/9.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es 4.18.1`, `@types/lodash-es 4.17.12`
  - 조사 당시 인기: 주간 다운로드 [56,956회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/generator-jhipster) / 저장소 스타 [22,449개](https://deps.dev/_/s/npm/p/generator-jhipster) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T05:40:06+00:00

<a id="l248"></a>

- [ ] **[L248] `native-base`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [GeekyAnts/NativeBase](https://github.com/GeekyAnts/NativeBase)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [native-base@3.4.28](https://registry.npmjs.org/native-base/3.4.28) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`, `lodash.has ^4.5.2`, `lodash.omit ^4.5.0`, `lodash.pick ^4.4.0`, `lodash.isnil ^4.0.0`, `lodash.merge ^4.6.2`, `lodash.omitby ^4.6.0`, `lodash.isempty ^4.4.0`, `lodash.isequal ^4.5.0`, `lodash.uniqueid ^4.0.1`, `lodash.clonedeep ^4.5.0`, `lodash.mergewith ^4.6.2` / **devDependencies**: `@types/lodash.get ^4.4.6`, `@types/lodash.has ^4.5.6`, `@types/lodash.omit ^4.5.6`, `@types/lodash.pick ^4.4.6`, `@types/lodash.isnil ^4.0.6`, `@types/lodash.merge ^4.6.6`, `@types/lodash.omitby ^4.6.6`, `@types/lodash.isempty ^4.4.6`, `@types/lodash.isequal ^4.5.5`, `@types/lodash.uniqueid ^4.0.7`, `@types/lodash.clonedeep ^4.5.6`, `@types/lodash.mergewith ^4.6.6`
  - 조사 당시 인기: 주간 다운로드 [54,471회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/native-base) / 저장소 스타 [20,383개](https://deps.dev/_/s/npm/p/native-base) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T19:35:05+00:00
  - npm 배포 중단 안내: NativeBase has evolved into gluestack-ui! Visit https://gluestack.io to use our next-generation component library.

<a id="l249"></a>

- [ ] **[L249] `@loopback/repository`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [loopbackio/loopback-next](https://github.com/loopbackio/loopback-next)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@loopback/repository@8.0.15](https://registry.npmjs.org/@loopback/repository/8.0.15) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1` / **devDependencies**: `@types/lodash ^4.17.25`
  - 조사 당시 인기: 주간 다운로드 [51,303회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40loopback%2Frepository) / 저장소 스타 [5,107개](https://api.github.com/repos/loopbackio/loopback-next) · 통과 기준: 스타

<a id="l250"></a>

- [ ] **[L250] `jointjs`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [clientIO/joint](https://github.com/clientIO/joint)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [jointjs@3.7.7](https://registry.npmjs.org/jointjs/3.7.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ~4.17.21` / **devDependencies**: `@types/lodash ~4.14.199`
  - 조사 당시 인기: 주간 다운로드 [49,137회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/jointjs) / 저장소 스타 [5,369개](https://api.github.com/repos/clientIO/joint) · 통과 기준: 스타

<a id="l251"></a>

- [ ] **[L251] `@jupyter-widgets/base`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jupyter-widgets/ipywidgets](https://github.com/jupyter-widgets/ipywidgets)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@jupyter-widgets/base@6.0.12](https://registry.npmjs.org/%40jupyter-widgets%2Fbase/6.0.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`, `@types/lodash ^4.14.134`
  - 조사 당시 인기: 주간 다운로드 [43,705회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40jupyter-widgets%2Fbase) / 저장소 스타 [3,326개](https://deps.dev/_/s/npm/p/%40jupyter-widgets%2Fbase) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-21T02:28:09+00:00

<a id="l252"></a>

- [ ] **[L252] `waterline`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [balderdashy/waterline](https://github.com/balderdashy/waterline)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [waterline@0.15.2](https://registry.npmjs.org/waterline/0.15.2) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.issafeinteger 4.0.4`
  - 조사 당시 인기: 주간 다운로드 [37,323회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/waterline) / 저장소 스타 [5,386개](https://api.github.com/repos/balderdashy/waterline) · 통과 기준: 스타

<a id="l253"></a>

- [ ] **[L253] `redux-devtools-log-monitor`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [reduxjs/redux-devtools](https://github.com/reduxjs/redux-devtools)
  - 같은 저장소 항목: [L033 · `react-base16-styling`](#l033), [L095 · `react-json-tree`](#l095), [L237 · `react-dock`](#l237), [L291 · `@redux-devtools/log-monitor`](#l291)
  - 조사 당시 배포본: [redux-devtools-log-monitor@2.1.0](https://registry.npmjs.org/redux-devtools-log-monitor/2.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`, `@types/lodash.debounce ^4.0.6`
  - 조사 당시 인기: 주간 다운로드 [28,223회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/redux-devtools-log-monitor) / 저장소 스타 [14,367개](https://deps.dev/_/s/npm/p/redux-devtools-log-monitor) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T16:42:23+00:00
  - npm 배포 중단 안내: Package moved to @redux-devtools/log-monitor.

<a id="l254"></a>

- [ ] **[L254] `@antv/x6-common`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [antvis/x6](https://github.com/antvis/x6)
  - 같은 저장소 항목: [L238 · `@antv/x6`](#l238)
  - 조사 당시 배포본: [@antv/x6-common@2.0.17](https://registry.npmjs.org/%40antv%2Fx6-common/2.0.17) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.15` / **devDependencies**: `@types/lodash-es ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [22,359회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40antv%2Fx6-common) / 저장소 스타 [6,685개](https://deps.dev/_/s/npm/p/%40antv%2Fx6-common) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T08:35:36+00:00

<a id="l255"></a>

- [ ] **[L255] `@caporal/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [mattallty/Caporal.js](https://github.com/mattallty/Caporal.js)
  - 같은 저장소 항목: [L243 · `caporal`](#l243)
  - 조사 당시 배포본: [@caporal/core@2.0.7](https://registry.npmjs.org/%40caporal%2Fcore/2.0.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `@types/lodash ^4.14.149`
  - 조사 당시 인기: 주간 다운로드 [17,913회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40caporal%2Fcore) / 저장소 스타 [3,450개](https://deps.dev/_/s/npm/p/%40caporal%2Fcore) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-14T22:59:53+00:00

<a id="l256"></a>

- [ ] **[L256] `@logicflow/extension`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [didi/LogicFlow](https://github.com/didi/LogicFlow)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@logicflow/extension@2.3.1](https://registry.npmjs.org/%40logicflow%2Fextension/2.3.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [16,141회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40logicflow%2Fextension) / 저장소 스타 [11,673개](https://deps.dev/_/s/npm/p/%40logicflow%2Fextension) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T00:54:14+00:00

<a id="l257"></a>

- [ ] **[L257] `gatsby-plugin-feed`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [gatsbyjs/gatsby](https://github.com/gatsbyjs/gatsby)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [gatsby-plugin-feed@5.16.0](https://registry.npmjs.org/gatsby-plugin-feed/5.16.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [14,906회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/gatsby-plugin-feed) / 저장소 스타 [55,944개](https://deps.dev/_/s/npm/p/gatsby-plugin-feed) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T18:53:13+00:00

<a id="l258"></a>

- [ ] **[L258] `evergreen-ui`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [segmentio/evergreen](https://github.com/segmentio/evergreen)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [evergreen-ui@7.1.9](https://registry.npmjs.org/evergreen-ui/7.1.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.omit ^4.5.0`, `lodash.merge ^4.6.2`, `lodash.uniqby ^4.7.0`, `lodash.isempty ^4.4.0`, `lodash.debounce ^4.0.8`, `lodash.differencewith ^4.5.0` / **devDependencies**: `@types/lodash.merge ^4.6.6`, `@types/lodash.uniqby ^4.7.6`, `@types/lodash.isempty ^4.4.6`, `@types/lodash.debounce ^4.0.6`, `@types/lodash.differencewith ^4.5.6`
  - 조사 당시 인기: 주간 다운로드 [14,775회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/evergreen-ui) / 저장소 스타 [12,422개](https://deps.dev/_/s/npm/p/evergreen-ui) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T22:15:48+00:00

<a id="l259"></a>

- [ ] **[L259] `iview`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [iview/iview](https://github.com/iview/iview)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [iview@3.5.4](https://registry.npmjs.org/iview/3.5.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [7,102회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/iview) / 저장소 스타 [23,769개](https://api.github.com/repos/iview/iview) · 통과 기준: 스타

<a id="l260"></a>

- [ ] **[L260] `dumi-theme-default`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [umijs/dumi](https://github.com/umijs/dumi)
  - 같은 저장소 항목: [L246 · `dumi`](#l246), [L303 · `@umijs/preset-dumi`](#l303)
  - 조사 당시 배포본: [dumi-theme-default@1.1.24](https://registry.npmjs.org/dumi-theme-default/1.1.24) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 [6,321회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/dumi-theme-default) / 저장소 스타 [3,795개](https://deps.dev/_/s/npm/p/dumi-theme-default) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-03T11:06:56+00:00

<a id="l261"></a>

- [ ] **[L261] `pageres`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sindresorhus/pageres](https://github.com/sindresorhus/pageres)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [pageres@9.0.0](https://registry.npmjs.org/pageres/9.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.20`
  - 조사 당시 인기: 주간 다운로드 [4,527회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/pageres) / 저장소 스타 [9,734개](https://deps.dev/_/s/npm/p/pageres) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-03T00:50:06+00:00

<a id="l262"></a>

- [ ] **[L262] `vux`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [airyland/vux](https://github.com/airyland/vux)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [vux@2.11.1](https://registry.npmjs.org/vux/2.11.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1` / **devDependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [4,110회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/vux) / 저장소 스타 [17,462개](https://deps.dev/_/s/npm/p/vux) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-27T22:47:41+00:00

<a id="l263"></a>

- [ ] **[L263] `nivo`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [plouc/nivo](https://github.com/plouc/nivo)
  - 같은 저장소 항목: [L069 · `@nivo/core`](#l069)
  - 조사 당시 배포본: [nivo@0.31.0](https://registry.npmjs.org/nivo/0.31.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.4`
  - 조사 당시 인기: 주간 다운로드 [2,831회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/nivo) / 저장소 스타 [14,091개](https://api.github.com/repos/plouc/nivo) · 통과 기준: 스타

<a id="l264"></a>

- [ ] **[L264] `johnny-five`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rwaldron/johnny-five](https://github.com/rwaldron/johnny-five)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [johnny-five@2.1.0](https://registry.npmjs.org/johnny-five/2.1.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.3`, `lodash.clonedeep ^4.3.0`
  - 조사 당시 인기: 주간 다운로드 [2,719회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/johnny-five) / 저장소 스타 [13,413개](https://deps.dev/_/s/npm/p/johnny-five) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T22:39:31+00:00

<a id="l265"></a>

- [ ] **[L265] `electron-forge`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [electron-userland/electron-forge](https://github.com/electron-userland/electron-forge)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [electron-forge@5.2.4](https://registry.npmjs.org/electron-forge/5.2.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.0`, `lodash.template ^4.4.0`
  - 조사 당시 인기: 주간 다운로드 [2,401회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/electron-forge) / 저장소 스타 [7,134개](https://deps.dev/_/s/npm/p/electron-forge) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T07:54:47+00:00
  - npm 배포 중단 안내: Electron Forge has a new home at @electron-forge/cli and a new major version. See https://www.electronjs.org/blog/forge-v6-release

<a id="l266"></a>

- [ ] **[L266] `think-helper`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [thinkjs/thinkjs](https://github.com/thinkjs/thinkjs)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [think-helper@1.3.0](https://registry.npmjs.org/think-helper/1.3.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 [1,930회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/think-helper) / 저장소 스타 [5,268개](https://deps.dev/_/s/npm/p/think-helper) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-23T11:44:12+00:00

<a id="l267"></a>

- [ ] **[L267] `guess-webpack`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [guess-js/guess](https://github.com/guess-js/guess)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [guess-webpack@0.4.22](https://registry.npmjs.org/guess-webpack/0.4.22) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.template ^4.4.0`
  - 조사 당시 인기: 주간 다운로드 [879회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/guess-webpack) / 저장소 스타 [7,119개](https://deps.dev/_/s/npm/p/guess-webpack) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-31T00:58:37+00:00

<a id="l268"></a>

- [ ] **[L268] `@alilc/lowcode-code-generator`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [alibaba/lowcode-engine](https://github.com/alibaba/lowcode-engine)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@alilc/lowcode-code-generator@1.1.7](https://registry.npmjs.org/%40alilc%2Flowcode-code-generator/1.1.7) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21`, `lodash-es ^4.17.21`, `@types/lodash ^4.14.162` / **devDependencies**: `@types/lodash ^4.14.162`
  - 조사 당시 인기: 주간 다운로드 [329회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40alilc%2Flowcode-code-generator) / 저장소 스타 [15,883개](https://deps.dev/_/s/npm/p/%40alilc%2Flowcode-code-generator) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T02:17:58+00:00

<a id="l269"></a>

- [ ] **[L269] `@excalidraw/excalidraw`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@excalidraw/excalidraw@0.18.1](https://registry.npmjs.org/%40excalidraw%2Fexcalidraw/0.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce 4.0.8`, `lodash.throttle 4.1.1` / **devDependencies**: `@types/lodash.debounce 4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [130,722개](https://deps.dev/_/s/npm/p/%40excalidraw%2Fexcalidraw) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T03:34:24+00:00

<a id="l270"></a>

- [ ] **[L270] `@superset-ui/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [apache/superset](https://github.com/apache/superset)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@superset-ui/core@0.20.4](https://registry.npmjs.org/%40superset-ui%2Fcore/0.20.4) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.17.7`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [74,504개](https://deps.dev/_/s/npm/p/%40superset-ui%2Fcore) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T08:57:40+00:00

<a id="l271"></a>

- [ ] **[L271] `@novu/stateless`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [novuhq/novu](https://github.com/novuhq/novu)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@novu/stateless@2.6.6](https://registry.npmjs.org/%40novu%2Fstateless/2.6.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.get ^4.4.2`, `lodash.merge ^4.6.2` / **devDependencies**: `@types/lodash.get ^4.4.6`, `@types/lodash.merge ^4.6.6`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [39,706개](https://deps.dev/_/s/npm/p/%40novu%2Fstateless) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-01T21:40:38+00:00

<a id="l272"></a>

- [ ] **[L272] `@pnpm/tarball-fetcher`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [pnpm/pnpm](https://github.com/pnpm/pnpm)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@pnpm/tarball-fetcher@1006.0.6](https://registry.npmjs.org/%40pnpm%2Ftarball-fetcher/1006.0.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle 4.1.1` / **devDependencies**: `@types/lodash.throttle 4.1.7`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [36,320개](https://deps.dev/_/s/npm/p/%40pnpm%2Ftarball-fetcher) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T15:49:11+00:00

<a id="l273"></a>

- [ ] **[L273] `@medusajs/dashboard`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [medusajs/medusa](https://github.com/medusajs/medusa)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@medusajs/dashboard@2.20.1](https://registry.npmjs.org/%40medusajs%2Fdashboard/2.20.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.isequal ^4.5.0`, `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [36,074개](https://deps.dev/_/s/npm/p/%40medusajs%2Fdashboard) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-31T09:53:13+00:00

<a id="l274"></a>

- [ ] **[L274] `@uppy/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [transloadit/uppy](https://github.com/transloadit/uppy)
  - 같은 저장소 항목: [L275 · `@uppy/dashboard`](#l275), [L276 · `@uppy/golden-retriever`](#l276), [L277 · `@uppy/utils`](#l277)
  - 조사 당시 배포본: [@uppy/core@6.0.0](https://registry.npmjs.org/%40uppy%2Fcore/6.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1` / **devDependencies**: `@types/lodash ^4.14.199`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [30,938개](https://deps.dev/_/s/npm/p/%40uppy%2Fcore) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T01:14:23+00:00

<a id="l275"></a>

- [ ] **[L275] `@uppy/dashboard`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [transloadit/uppy](https://github.com/transloadit/uppy)
  - 같은 저장소 항목: [L274 · `@uppy/core`](#l274), [L276 · `@uppy/golden-retriever`](#l276), [L277 · `@uppy/utils`](#l277)
  - 조사 당시 배포본: [@uppy/dashboard@6.0.0](https://registry.npmjs.org/%40uppy%2Fdashboard/6.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [30,938개](https://deps.dev/_/s/npm/p/%40uppy%2Fdashboard) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T01:14:23+00:00

<a id="l276"></a>

- [ ] **[L276] `@uppy/golden-retriever`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [transloadit/uppy](https://github.com/transloadit/uppy)
  - 같은 저장소 항목: [L274 · `@uppy/core`](#l274), [L275 · `@uppy/dashboard`](#l275), [L277 · `@uppy/utils`](#l277)
  - 조사 당시 배포본: [@uppy/golden-retriever@6.0.0](https://registry.npmjs.org/%40uppy%2Fgolden-retriever/6.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [30,938개](https://deps.dev/_/s/npm/p/%40uppy%2Fgolden-retriever) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T01:14:23+00:00

<a id="l277"></a>

- [ ] **[L277] `@uppy/utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [transloadit/uppy](https://github.com/transloadit/uppy)
  - 같은 저장소 항목: [L274 · `@uppy/core`](#l274), [L275 · `@uppy/dashboard`](#l275), [L276 · `@uppy/golden-retriever`](#l276)
  - 조사 당시 배포본: [@uppy/utils@7.2.0](https://registry.npmjs.org/%40uppy%2Futils/7.2.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.23` / **devDependencies**: `@types/lodash ^4.14.199`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [30,938개](https://deps.dev/_/s/npm/p/%40uppy%2Futils) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T01:14:23+00:00

<a id="l278"></a>

- [ ] **[L278] `@nextui-org/calendar`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nextui-org/nextui](https://github.com/nextui-org/nextui)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@nextui-org/calendar@2.2.9](https://registry.npmjs.org/%40nextui-org%2Fcalendar/2.2.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `@types/lodash.debounce ^4.0.7`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [30,481개](https://deps.dev/_/s/npm/p/%40nextui-org%2Fcalendar) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T19:00:56+00:00
  - npm 배포 중단 안내: This package has been deprecated. Please use @heroui/calendar instead.

<a id="l279"></a>

- [ ] **[L279] `@sequelize/utils`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sequelize/sequelize](https://github.com/sequelize/sequelize)
  - 같은 저장소 항목: [L042 · `sequelize`](#l042)
  - 조사 당시 배포본: [@sequelize/utils@7.0.0-alpha.48](https://registry.npmjs.org/%40sequelize%2Futils/7.0.0-alpha.48) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.23`, `@types/lodash ^4.17.23`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [30,375개](https://deps.dev/_/s/npm/p/%40sequelize%2Futils) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-31T04:47:36+00:00

<a id="l280"></a>

- [ ] **[L280] `@vue/cli`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vuejs/vue-cli](https://github.com/vuejs/vue-cli)
  - 같은 저장소 항목: [L281 · `@vue/cli-service`](#l281), [L282 · `@vue/cli-ui`](#l282)
  - 조사 당시 배포본: [@vue/cli@5.0.9](https://registry.npmjs.org/%40vue%2Fcli/5.0.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [29,546개](https://deps.dev/_/s/npm/p/%40vue%2Fcli) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T23:53:04+00:00

<a id="l281"></a>

- [ ] **[L281] `@vue/cli-service`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vuejs/vue-cli](https://github.com/vuejs/vue-cli)
  - 같은 저장소 항목: [L280 · `@vue/cli`](#l280), [L282 · `@vue/cli-ui`](#l282)
  - 조사 당시 배포본: [@vue/cli-service@5.0.9](https://registry.npmjs.org/%40vue%2Fcli-service/5.0.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.mapvalues ^4.6.0`, `lodash.defaultsdeep ^4.6.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [29,546개](https://deps.dev/_/s/npm/p/%40vue%2Fcli-service) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T23:53:04+00:00

<a id="l282"></a>

- [ ] **[L282] `@vue/cli-ui`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vuejs/vue-cli](https://github.com/vuejs/vue-cli)
  - 같은 저장소 항목: [L280 · `@vue/cli`](#l280), [L281 · `@vue/cli-service`](#l281)
  - 조사 당시 배포본: [@vue/cli-ui@5.0.9](https://registry.npmjs.org/%40vue%2Fcli-ui/5.0.9) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.1` / **devDependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [29,546개](https://deps.dev/_/s/npm/p/%40vue%2Fcli-ui) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T23:53:04+00:00

<a id="l283"></a>

- [ ] **[L283] `@crawlee/browser-pool`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [apify/crawlee](https://github.com/apify/crawlee)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@crawlee/browser-pool@3.18.1](https://registry.npmjs.org/%40crawlee%2Fbrowser-pool/3.18.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [25,532개](https://deps.dev/_/s/npm/p/%40crawlee%2Fbrowser-pool) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T09:35:15+00:00

<a id="l284"></a>

- [ ] **[L284] `@node-red/util`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [node-red/node-red](https://github.com/node-red/node-red)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@node-red/util@5.0.6](https://registry.npmjs.org/%40node-red%2Futil/5.0.6) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [23,596개](https://deps.dev/_/s/npm/p/%40node-red%2Futil) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T02:17:46+00:00

<a id="l285"></a>

- [ ] **[L285] `@vuepress/plugin-active-header-links`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vuejs/vuepress](https://github.com/vuejs/vuepress)
  - 같은 저장소 항목: [L286 · `@vuepress/plugin-back-to-top`](#l286)
  - 조사 당시 배포본: [@vuepress/plugin-active-header-links@1.9.10](https://registry.npmjs.org/%40vuepress%2Fplugin-active-header-links/1.9.10) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [22,742개](https://deps.dev/_/s/npm/p/%40vuepress%2Fplugin-active-header-links) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T18:55:32+00:00

<a id="l286"></a>

- [ ] **[L286] `@vuepress/plugin-back-to-top`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [vuejs/vuepress](https://github.com/vuejs/vuepress)
  - 같은 저장소 항목: [L285 · `@vuepress/plugin-active-header-links`](#l285)
  - 조사 당시 배포본: [@vuepress/plugin-back-to-top@1.9.10](https://registry.npmjs.org/%40vuepress%2Fplugin-back-to-top/1.9.10) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [22,742개](https://deps.dev/_/s/npm/p/%40vuepress%2Fplugin-back-to-top) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T18:55:32+00:00

<a id="l287"></a>

- [ ] **[L287] `@wangeditor/editor`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [wangeditor-team/wangEditor](https://github.com/wangeditor-team/wangEditor)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@wangeditor/editor@5.1.23](https://registry.npmjs.org/%40wangeditor%2Feditor/5.1.23) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.foreach ^4.5.0`, `lodash.isequal ^4.5.0`, `lodash.toarray ^4.4.0`, `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1`, `lodash.camelcase ^4.3.0`, `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [18,363개](https://deps.dev/_/s/npm/p/%40wangeditor%2Feditor) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-03T03:22:26+00:00

<a id="l288"></a>

- [ ] **[L288] `@feathersjs/authentication`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [feathersjs/feathers](https://github.com/feathersjs/feathers)
  - 같은 저장소 항목: [L289 · `@feathersjs/authentication-jwt`](#l289)
  - 조사 당시 배포본: [@feathersjs/authentication@5.0.49](https://registry.npmjs.org/%40feathersjs%2Fauthentication/5.0.49) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.18.1` / **devDependencies**: `@types/lodash ^4.17.24`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [15,265개](https://deps.dev/_/s/npm/p/%40feathersjs%2Fauthentication) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T13:37:13+00:00

<a id="l289"></a>

- [ ] **[L289] `@feathersjs/authentication-jwt`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [feathersjs/feathers](https://github.com/feathersjs/feathers)
  - 같은 저장소 항목: [L288 · `@feathersjs/authentication`](#l288)
  - 조사 당시 배포본: [@feathersjs/authentication-jwt@2.0.10](https://registry.npmjs.org/%40feathersjs%2Fauthentication-jwt/2.0.10) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.omit ^4.5.0`, `lodash.pick ^4.4.0`, `lodash.merge ^4.6.0`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [15,265개](https://deps.dev/_/s/npm/p/%40feathersjs%2Fauthentication-jwt) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T13:37:13+00:00

<a id="l290"></a>

- [ ] **[L290] `@ahooksjs/use-request`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [alibaba/hooks](https://github.com/alibaba/hooks)
  - 같은 저장소 항목: [L097 · `ahooks`](#l097)
  - 조사 당시 배포본: [@ahooksjs/use-request@2.8.15](https://registry.npmjs.org/%40ahooksjs%2Fuse-request/2.8.15) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [14,983개](https://deps.dev/_/s/npm/p/%40ahooksjs%2Fuse-request) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T02:00:42+00:00

<a id="l291"></a>

- [ ] **[L291] `@redux-devtools/log-monitor`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [reduxjs/redux-devtools](https://github.com/reduxjs/redux-devtools)
  - 같은 저장소 항목: [L033 · `react-base16-styling`](#l033), [L095 · `react-json-tree`](#l095), [L237 · `react-dock`](#l237), [L253 · `redux-devtools-log-monitor`](#l253)
  - 조사 당시 배포본: [@redux-devtools/log-monitor@6.0.0](https://registry.npmjs.org/%40redux-devtools%2Flog-monitor/6.0.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.debounce ^4.0.8`, `@types/lodash.debounce ^4.0.9`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [14,367개](https://deps.dev/_/s/npm/p/%40redux-devtools%2Flog-monitor) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T16:42:23+00:00

<a id="l292"></a>

- [ ] **[L292] `@truffle/codec`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [trufflesuite/truffle](https://github.com/trufflesuite/truffle)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@truffle/codec@0.17.3](https://registry.npmjs.org/%40truffle%2Fcodec/0.17.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.21` / **devDependencies**: `@types/lodash ^4.14.179`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [13,915개](https://deps.dev/_/s/npm/p/%40truffle%2Fcodec) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-31T10:32:01+00:00
  - npm 배포 중단 안내: Package no longer supported. Contact Support at https://www.npmjs.com/support for more info.

<a id="l293"></a>

- [ ] **[L293] `@rspack/plugin-html`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [web-infra-dev/rspack](https://github.com/web-infra-dev/rspack)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@rspack/plugin-html@0.5.8](https://registry.npmjs.org/%40rspack%2Fplugin-html/0.5.8) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.template ^4.5.0` / **devDependencies**: `@types/lodash.template ^4.5.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [12,883개](https://deps.dev/_/s/npm/p/%40rspack%2Fplugin-html) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-01T12:06:33+00:00
  - npm 배포 중단 안내: deprecated

<a id="l294"></a>

- [ ] **[L294] `@milkdown/crepe`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Milkdown/milkdown](https://github.com/Milkdown/milkdown)
  - 같은 저장소 항목: [L144 · `@milkdown/plugin-listener`](#l144), [L147 · `@milkdown/plugin-slash`](#l147), [L148 · `@milkdown/plugin-tooltip`](#l148), [L149 · `@milkdown/components`](#l149), [L150 · `@milkdown/plugin-block`](#l150)
  - 조사 당시 배포본: [@milkdown/crepe@7.22.1](https://registry.npmjs.org/%40milkdown%2Fcrepe/7.22.1) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [11,880개](https://deps.dev/_/s/npm/p/%40milkdown%2Fcrepe) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-01T20:35:24+00:00

<a id="l295"></a>

- [ ] **[L295] `@keystone-next/app-admin-ui-legacy`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [keystonejs/keystone](https://github.com/keystonejs/keystone)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@keystone-next/app-admin-ui-legacy@7.4.3](https://registry.npmjs.org/%40keystone-next%2Fapp-admin-ui-legacy/7.4.3) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.set ^4.3.2`, `lodash.debounce ^4.0.8`, `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [9,963개](https://deps.dev/_/s/npm/p/%40keystone-next%2Fapp-admin-ui-legacy) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T23:37:05+00:00

<a id="l296"></a>

- [ ] **[L296] `@apollographql/graphql-playground-react`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [graphcool/graphql-playground](https://github.com/graphcool/graphql-playground)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@apollographql/graphql-playground-react@1.7.42](https://registry.npmjs.org/%40apollographql%2Fgraphql-playground-react/1.7.42) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash ^4.17.11`, `lodash.debounce ^4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [8,829개](https://deps.dev/_/s/npm/p/%40apollographql%2Fgraphql-playground-react) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T00:56:49+00:00

<a id="l297"></a>

- [ ] **[L297] `@imgly/background-removal`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [imgly/background-removal-js](https://github.com/imgly/background-removal-js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@imgly/background-removal@1.7.0](https://registry.npmjs.org/%40imgly%2Fbackground-removal/1.7.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash-es ^4.17.21` / **devDependencies**: `@types/lodash-es ^4.17.12`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [7,293개](https://deps.dev/_/s/npm/p/%40imgly%2Fbackground-removal) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-31T11:40:36+00:00

<a id="l298"></a>

- [ ] **[L298] `@pandacss/core`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [chakra-ui/panda](https://github.com/chakra-ui/panda)
  - 같은 저장소 항목: [L299 · `@pandacss/node`](#l299)
  - 조사 당시 배포본: [@pandacss/core@1.12.0](https://registry.npmjs.org/%40pandacss%2Fcore/1.12.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge 4.6.2` / **devDependencies**: `@types/lodash.merge 4.6.9`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [6,169개](https://deps.dev/_/s/npm/p/%40pandacss%2Fcore) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T08:02:02+00:00

<a id="l299"></a>

- [ ] **[L299] `@pandacss/node`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [chakra-ui/panda](https://github.com/chakra-ui/panda)
  - 같은 저장소 항목: [L298 · `@pandacss/core`](#l298)
  - 조사 당시 배포본: [@pandacss/node@1.12.0](https://registry.npmjs.org/%40pandacss%2Fnode/1.12.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge 4.6.2` / **devDependencies**: `@types/lodash.merge 4.6.9`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [6,169개](https://deps.dev/_/s/npm/p/%40pandacss%2Fnode) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-29T08:02:02+00:00

<a id="l300"></a>

- [ ] **[L300] `@ant-design/x`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/x](https://github.com/ant-design/x)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@ant-design/x@2.9.0](https://registry.npmjs.org/%40ant-design%2Fx/2.9.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1` / **devDependencies**: `lodash ^4.17.21`, `@types/lodash ^4.17.7`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [4,745개](https://deps.dev/_/s/npm/p/%40ant-design%2Fx) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T07:45:38+00:00

<a id="l301"></a>

- [ ] **[L301] `@alifd/next`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [alibaba-fusion/next](https://github.com/alibaba-fusion/next)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@alifd/next@1.27.34](https://registry.npmjs.org/%40alifd%2Fnext/1.27.34) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.clonedeep ^4.5.0` / **devDependencies**: `lodash ^4.17.5`, `@types/lodash ^4.14.202`, `@types/lodash.clonedeep ^4.5.9`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [4,678개](https://deps.dev/_/s/npm/p/%40alifd%2Fnext) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-28T02:23:11+00:00

<a id="l302"></a>

- [ ] **[L302] `@ohif/extension-cornerstone`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [OHIF/Viewers](https://github.com/OHIF/Viewers)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@ohif/extension-cornerstone@3.12.12](https://registry.npmjs.org/%40ohif%2Fextension-cornerstone/3.12.12) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.zip 4.2.0`, `lodash.compact 3.0.1`, `lodash.flatten 4.4.0`, `lodash.debounce 4.0.8`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [4,310개](https://deps.dev/_/s/npm/p/%40ohif%2Fextension-cornerstone) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-27T19:31:19+00:00

<a id="l303"></a>

- [ ] **[L303] `@umijs/preset-dumi`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [umijs/dumi](https://github.com/umijs/dumi)
  - 같은 저장소 항목: [L246 · `dumi`](#l246), [L260 · `dumi-theme-default`](#l260)
  - 조사 당시 배포본: [@umijs/preset-dumi@1.1.54](https://registry.npmjs.org/%40umijs%2Fpreset-dumi/1.1.54) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.throttle ^4.1.1`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [3,795개](https://deps.dev/_/s/npm/p/%40umijs%2Fpreset-dumi) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-03T11:06:56+00:00

<a id="l304"></a>

- [ ] **[L304] `@opentelemetry/metrics`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [open-telemetry/opentelemetry-js](https://github.com/open-telemetry/opentelemetry-js)
  - 같은 저장소 항목: [L305 · `@opentelemetry/sdk-metrics-base`](#l305), [L306 · `@opentelemetry/tracing`](#l306)
  - 조사 당시 배포본: [@opentelemetry/metrics@0.24.0](https://registry.npmjs.org/%40opentelemetry%2Fmetrics/0.24.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2` / **devDependencies**: `@types/lodash.merge 4.6.6`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [3,454개](https://deps.dev/_/s/npm/p/%40opentelemetry%2Fmetrics) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T06:52:18+00:00
  - npm 배포 중단 안내: Package renamed to @opentelemetry/sdk-metrics-base

<a id="l305"></a>

- [ ] **[L305] `@opentelemetry/sdk-metrics-base`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [open-telemetry/opentelemetry-js](https://github.com/open-telemetry/opentelemetry-js)
  - 같은 저장소 항목: [L304 · `@opentelemetry/metrics`](#l304), [L306 · `@opentelemetry/tracing`](#l306)
  - 조사 당시 배포본: [@opentelemetry/sdk-metrics-base@0.31.0](https://registry.npmjs.org/%40opentelemetry%2Fsdk-metrics-base/0.31.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge 4.6.2` / **devDependencies**: `@types/lodash.merge 4.6.6`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [3,454개](https://deps.dev/_/s/npm/p/%40opentelemetry%2Fsdk-metrics-base) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T06:52:18+00:00
  - npm 배포 중단 안내: Please use @opentelemetry/sdk-metrics

<a id="l306"></a>

- [ ] **[L306] `@opentelemetry/tracing`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [open-telemetry/opentelemetry-js](https://github.com/open-telemetry/opentelemetry-js)
  - 같은 저장소 항목: [L304 · `@opentelemetry/metrics`](#l304), [L305 · `@opentelemetry/sdk-metrics-base`](#l305)
  - 조사 당시 배포본: [@opentelemetry/tracing@0.24.0](https://registry.npmjs.org/%40opentelemetry%2Ftracing/0.24.0) · 일반 의존성
  - 조사 당시 직접 선언: **dependencies**: `lodash.merge ^4.6.2` / **devDependencies**: `@types/lodash.merge 4.6.6`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [3,454개](https://deps.dev/_/s/npm/p/%40opentelemetry%2Ftracing) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T06:52:18+00:00
  - npm 배포 중단 안내: Package renamed to @opentelemetry/sdk-trace-base


## 개발 의존성만 선언 — 30개

<a id="l307"></a>

- [ ] **[L307] `jest-util`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [jestjs/jest](https://github.com/jestjs/jest)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [jest-util@30.5.1](https://registry.npmjs.org/jest-util/30.5.1) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.19`
  - 조사 당시 인기: 주간 다운로드 [115,566,766회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/jest-util) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l308"></a>

- [ ] **[L308] `rxjs`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [reactivex/rxjs](https://github.com/reactivex/rxjs)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [rxjs@7.8.2](https://registry.npmjs.org/rxjs/7.8.2) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.15`, `@types/lodash 4.14.102`
  - 조사 당시 인기: 주간 다운로드 [104,558,888회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/rxjs) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l309"></a>

- [ ] **[L309] `eslint-plugin-import`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [import-js/eslint-plugin-import](https://github.com/import-js/eslint-plugin-import)
  - 같은 저장소 항목: [L090 · `eslint-import-resolver-webpack`](#l090)
  - 조사 당시 배포본: [eslint-plugin-import@2.32.0](https://registry.npmjs.org/eslint-plugin-import/2.32.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash.isarray ^4.0.0`
  - 조사 당시 인기: 주간 다운로드 [60,541,256회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/eslint-plugin-import) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l310"></a>

- [ ] **[L310] `immer`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [immerjs/immer](https://github.com/immerjs/immer)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [immer@11.1.18](https://registry.npmjs.org/immer/11.1.18) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.4`, `lodash.clonedeep ^4.5.0`
  - 조사 당시 인기: 주간 다운로드 [59,865,698회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/immer) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l311"></a>

- [ ] **[L311] `webpack`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [webpack/webpack](https://github.com/webpack/webpack)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [webpack@5.110.3](https://registry.npmjs.org/webpack/5.110.3) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.19`, `lodash-es ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [56,430,458회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/webpack) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l312"></a>

- [ ] **[L312] `ts-node`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [TypeStrong/ts-node](https://github.com/TypeStrong/ts-node)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [ts-node@10.9.2](https://registry.npmjs.org/ts-node/10.9.2) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.15`, `@types/lodash ^4.14.151`
  - 조사 당시 인기: 주간 다운로드 [49,423,273회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/ts-node) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l313"></a>

- [ ] **[L313] `cytoscape`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [cytoscape/cytoscape.js](https://github.com/cytoscape/cytoscape.js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [cytoscape@3.34.2](https://registry.npmjs.org/cytoscape/3.34.2) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [15,505,561회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/cytoscape) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l314"></a>

- [ ] **[L314] `@nestjs/config`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nestjs/config](https://github.com/nestjs/config)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@nestjs/config@12.0.0](https://registry.npmjs.org/%40nestjs%2Fconfig/12.0.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `@types/lodash 4.17.25`
  - 조사 당시 인기: 주간 다운로드 [8,252,531회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40nestjs%2Fconfig) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l315"></a>

- [ ] **[L315] `mongoose`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Automattic/mongoose](https://github.com/Automattic/mongoose)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [mongoose@9.9.4](https://registry.npmjs.org/mongoose/9.9.4) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash.isequal 4.5.0`, `lodash.isequalwith 4.4.0`
  - 조사 당시 인기: 주간 다운로드 [6,853,208회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/mongoose) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l316"></a>

- [ ] **[L316] `@storybook/csf`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ComponentDriven/csf](https://github.com/ComponentDriven/csf)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@storybook/csf@0.1.13](https://registry.npmjs.org/%40storybook%2Fcsf/0.1.13) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`, `@types/lodash ^4.14.191`
  - 조사 당시 인기: 주간 다운로드 [6,682,824회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40storybook%2Fcsf) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l317"></a>

- [ ] **[L317] `react-datepicker`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [Hacker0x01/react-datepicker](https://github.com/Hacker0x01/react-datepicker)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-datepicker@9.1.0](https://registry.npmjs.org/react-datepicker/9.1.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [5,342,425회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-datepicker) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l318"></a>

- [ ] **[L318] `@ant-design/icons`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/ant-design-icons](https://github.com/ant-design/ant-design-icons)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@ant-design/icons@6.3.4](https://registry.npmjs.org/%40ant-design%2Ficons/6.3.4) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.18.1`, `@types/lodash ^4.17.24`
  - 조사 당시 인기: 주간 다운로드 [4,486,718회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40ant-design%2Ficons) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l319"></a>

- [ ] **[L319] `react-grid-layout`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [STRML/react-grid-layout](https://github.com/STRML/react-grid-layout)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-grid-layout@2.2.4](https://registry.npmjs.org/react-grid-layout/2.2.4) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,886,695회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-grid-layout) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l320"></a>

- [ ] **[L320] `antd`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ant-design/ant-design](https://github.com/ant-design/ant-design)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [antd@6.6.2](https://registry.npmjs.org/antd/6.6.2) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.18.1`, `@types/lodash ^4.17.24`
  - 조사 당시 인기: 주간 다운로드 [3,750,223회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/antd) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l321"></a>

- [ ] **[L321] `telejson`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [storybookjs/telejson](https://github.com/storybookjs/telejson)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [telejson@8.0.0](https://registry.npmjs.org/telejson/8.0.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash-es ^4.17.21`, `@types/lodash-es ^4.17.6`
  - 조사 당시 인기: 주간 다운로드 [3,401,055회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/telejson) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l322"></a>

- [ ] **[L322] `z-schema`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [zaggino/z-schema](https://github.com/zaggino/z-schema)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [z-schema@12.4.5](https://registry.npmjs.org/z-schema/12.4.5) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash.isequal ^4.5.0`, `@types/lodash.isequal ^4.5.8`
  - 조사 당시 인기: 주간 다운로드 [3,225,186회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/z-schema) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l323"></a>

- [ ] **[L323] `@hello-pangea/dnd`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [hello-pangea/dnd](https://github.com/hello-pangea/dnd)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@hello-pangea/dnd@18.0.1](https://registry.npmjs.org/%40hello-pangea%2Fdnd/18.0.1) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash.isequal 4.5.0`, `@types/lodash.isequal 4.5.8`
  - 조사 당시 인기: 주간 다운로드 [3,197,573회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40hello-pangea%2Fdnd) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l324"></a>

- [ ] **[L324] `slate`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [ianstormtaylor/slate](https://github.com/ianstormtaylor/slate)
  - 같은 저장소 항목: [L044 · `slate-react`](#l044)
  - 조사 당시 배포본: [slate@0.126.2](https://registry.npmjs.org/slate/0.126.2) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [3,152,086회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/slate) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l325"></a>

- [ ] **[L325] `redux-persist`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [rt2zz/redux-persist](https://github.com/rt2zz/redux-persist)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [redux-persist@6.0.0](https://registry.npmjs.org/redux-persist/6.0.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [1,825,071회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/redux-persist) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l326"></a>

- [ ] **[L326] `contentful-management`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [contentful/contentful-management.js](https://github.com/contentful/contentful-management.js)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [contentful-management@12.15.0](https://registry.npmjs.org/contentful-management/12.15.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.20`, `@types/lodash ^4.14.168`
  - 조사 당시 인기: 주간 다운로드 [1,051,157회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/contentful-management) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l327"></a>

- [ ] **[L327] `react-sortable-hoc`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [clauderic/react-sortable-hoc](https://github.com/clauderic/react-sortable-hoc)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-sortable-hoc@2.0.0](https://registry.npmjs.org/react-sortable-hoc/2.0.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.12.0`
  - 조사 당시 인기: 주간 다운로드 [626,551회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-sortable-hoc) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l328"></a>

- [ ] **[L328] `@storybook/mdx1-csf`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [storybookjs/csf-mdx2](https://github.com/storybookjs/csf-mdx2)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@storybook/mdx1-csf@1.0.0](https://registry.npmjs.org/%40storybook%2Fmdx1-csf/1.0.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`, `@types/lodash ^4.14.167`
  - 조사 당시 인기: 주간 다운로드 [433,280회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/%40storybook%2Fmdx1-csf) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l329"></a>

- [ ] **[L329] `netlify`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [netlify/cli](https://github.com/netlify/cli)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [netlify@27.4.2](https://registry.npmjs.org/netlify/27.4.2) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash.shuffle ^4.2.0`, `@types/lodash.shuffle ^4.2.9`
  - 조사 당시 인기: 주간 다운로드 [354,807회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/netlify) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l330"></a>

- [ ] **[L330] `react-hotkeys`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [greena13/react-hotkeys](https://github.com/greena13/react-hotkeys)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-hotkeys@2.0.0](https://registry.npmjs.org/react-hotkeys/2.0.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash.random ^3.2.0`
  - 조사 당시 인기: 주간 다운로드 [288,940회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-hotkeys) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l331"></a>

- [ ] **[L331] `elastic-builder`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [sudo-suhas/elastic-builder](https://github.com/sudo-suhas/elastic-builder)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [elastic-builder@4.1.0](https://registry.npmjs.org/elastic-builder/4.1.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [261,815회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/elastic-builder) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l332"></a>

- [ ] **[L332] `vue-meta`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/vue-meta](https://github.com/nuxt/vue-meta)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [vue-meta@2.4.0](https://registry.npmjs.org/vue-meta/2.4.0) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.15`
  - 조사 당시 인기: 주간 다운로드 [253,621회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/vue-meta) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l333"></a>

- [ ] **[L333] `bootstrap-vue`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [bootstrap-vue/bootstrap-vue](https://github.com/bootstrap-vue/bootstrap-vue)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [bootstrap-vue@2.23.1](https://registry.npmjs.org/bootstrap-vue/2.23.1) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 [212,570회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/bootstrap-vue) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l334"></a>

- [ ] **[L334] `react-lazy-load`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [loktar00/react-lazy-load](https://github.com/loktar00/react-lazy-load)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [react-lazy-load@4.0.1](https://registry.npmjs.org/react-lazy-load/4.0.1) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `@types/lodash ^4.14.184`
  - 조사 당시 인기: 주간 다운로드 [178,752회](https://api.npmjs.org/downloads/point/2026-08-23:2026-08-29/react-lazy-load) / 저장소 스타 미조회 · 통과 기준: 다운로드

<a id="l335"></a>

- [ ] **[L335] `@storybook/ui`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [storybookjs/storybook](https://github.com/storybookjs/storybook)
  - 같은 저장소 항목: 없음
  - 조사 당시 배포본: [@storybook/ui@6.5.16](https://registry.npmjs.org/%40storybook%2Fui/6.5.16) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash ^4.17.21`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [90,963개](https://deps.dev/_/s/npm/p/%40storybook%2Fui) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-08-30T09:37:09+00:00

<a id="l336"></a>

- [ ] **[L336] `@nuxt/kit-edge`**
  - 상태: 미착수
  - 판정: 미정
  - 검증 단계: 미수행
  - 점수: 미정
  - 담당: —
  - 최근 작업일: —
  - 현재 재확인: —
  - 공동 작업: —
  - 결과·이슈·PR: —
  - 실제 이관 결과: 미실행
  - 메모·다음 행동: —
  - 저장소: [nuxt/nuxt](https://github.com/nuxt/nuxt)
  - 같은 저장소 항목: [L208 · `@nuxt/utils`](#l208), [L213 · `@nuxt/config`](#l213), [L214 · `@nuxt/vue-renderer`](#l214), [L215 · `@nuxt/core`](#l215), [L216 · `@nuxt/webpack`](#l216), [L217 · `@nuxt/builder`](#l217)
  - 조사 당시 배포본: [@nuxt/kit-edge@3.8.0-28284309.b3d3d7f4](https://registry.npmjs.org/%40nuxt%2Fkit-edge/3.8.0-28284309.b3d3d7f4) · 개발 의존성만
  - 조사 당시 직접 선언: **devDependencies**: `lodash-es 4.17.21`, `@types/lodash-es 4.17.9`
  - 조사 당시 인기: 주간 다운로드 미조회 / 저장소 스타 [60,806개](https://deps.dev/_/s/npm/p/%40nuxt%2Fkit-edge) · 통과 기준: 스타
  - 스타 출처 관측 시각: 2026-09-02T05:38:42+00:00
