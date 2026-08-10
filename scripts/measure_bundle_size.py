#!/usr/bin/env python3
"""
Synthetic bundle-size measurement for a lodash → es-toolkit migration.

Extracts the distinct lodash functions a repository actually uses, then bundles
that exact function set twice — once from lodash-es, once from es-toolkit/compat
— and reports the minified / gzip delta.

Why synthetic: it needs no install of the target repository and no benchmark
script, so it runs in seconds on any repo. Cross-checked against a real
before/after build of react-jsonschema-form, the synthetic delta predicted the
real one to within 2% (-10,463 B vs -10,681 B minified).

Usage:
    python measure_bundle_size.py <repo-directory>
    python measure_bundle_size.py <repo-directory> --include-tests
    python measure_bundle_size.py <repo-directory> --json

Requires: node + npm on PATH. Installs lodash-es, es-toolkit and esbuild into a
reusable scratch directory (~2s on first run, cached afterwards).
"""

import argparse
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.mts', '.cts',
              '.vue', '.svelte', '.astro'}

SKIP_DIRS = {
    'node_modules', '.git', '.next', '.nuxt',
    'coverage', '.turbo', '.cache', '.nx',
}

# Build-output names that are also legitimate source directory names. Skipped
# only outside `src/` — `packages/x/lib/` is compiled output, but
# `packages/x/src/lib/` is hand-written source (cf. metro).
AMBIGUOUS_OUTPUT_DIRS = {'dist', 'build', 'lib', 'out'}

# Paths that do not reach end users. Excluded unless --include-tests.
NON_SHIPPED = re.compile(
    r'(^|/)(test|tests|__tests__|__mocks__|spec|e2e|cypress|examples?|'
    r'docs?|website|playground|scripts|benchmarks?|fixtures)(/|$)'
)
NON_SHIPPED_FILE = re.compile(r'\.(test|spec|stories|bench)\.[jt]sx?$')

# ── lodash usage patterns ───────────────────────────────────────────────────

# import get from 'lodash/get'  |  import get from 'lodash-es/get'
RE_SUBPATH = re.compile(r"""from\s+['"]lodash(?:-es)?/(\w+)(?:\.js)?['"]""")
# const get = require('lodash/get')
RE_REQ_SUBPATH = re.compile(r"""require\s*\(\s*['"]lodash(?:-es)?/(\w+)(?:\.js)?['"]\s*\)""")
# Bare-package specifiers that resolve to lodash. `lodash-unified` is a pure
# conditional re-export (`export * from 'lodash-es'`) that projects adopt only
# to paper over lodash's missing dual ESM/CJS build, so its imports are lodash
# imports for every purpose here.
BARE_PKG = r"lodash(?:-es|-unified)?"

# import { get, has as _has } from 'lodash'
RE_NAMED = re.compile(rf"""import\s*\{{([^}}]+)\}}\s*from\s+['"]{BARE_PKG}['"]""")
# const { get } = require('lodash')
RE_REQ_NAMED = re.compile(rf"""\{{([^}}]+)\}}\s*=\s*require\s*\(\s*['"]{BARE_PKG}['"]\s*\)""")
# import _ from 'lodash'  /  import * as _ from 'lodash'  →  binding name
RE_DEFAULT = re.compile(
    rf"""import\s+(?:\*\s+as\s+)?(\w+)\s+from\s+['"]{BARE_PKG}['"]"""
)
RE_REQ_DEFAULT = re.compile(
    rf"""(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(\s*['"]{BARE_PKG}['"]\s*\)"""
)
# import throttle from 'lodash.throttle'  |  require('lodash.mergewith')
# Per-method packages are published all-lowercase (lodash.mergewith → mergeWith),
# so the captured name is canonicalized against es-toolkit/compat's export list.
RE_DOT_PKG = re.compile(
    r"""(?:from|require\s*\(\s*)\s*['"]lodash\.([a-z][a-z0-9]*)['"]"""
)
# lodash/fp needs a semantic rewrite rather than a direct import substitution.
# Capture the function so the caller can budget each manual conversion.
RE_FP = re.compile(r"""['"]lodash(?:-es)?/fp(?:/(\w+))?['"]""")

# Doc comments routinely contain example import paths (`from 'lodash/xxxx'`),
# which would otherwise be counted as real usage.
RE_BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)
RE_LINE_COMMENT = re.compile(r'^\s*(?://|\*).*$', re.MULTILINE)


def strip_comments(content: str) -> str:
    """Drop comments so example paths in docs aren't counted as imports.

    Only block comments and whole-line comments are removed — trailing `//`
    is left alone so URLs inside string literals stay intact.
    """
    return RE_LINE_COMMENT.sub('', RE_BLOCK_COMMENT.sub('', content))


def is_shipped(rel_path: str) -> bool:
    posix = rel_path.replace(os.sep, '/')
    parts = posix.split('/')

    # A source directory can legitimately contain domain modules named `spec`
    # (for example Swagger UI's `src/core/plugins/spec`).  Treat explicit test
    # directories and test-file suffixes under src as non-shipped, but do not
    # apply the broad repository-level `spec` heuristic to source modules.
    if 'src' in parts:
        src_index = parts.index('src')
        source_dirs = set(parts[src_index + 1:-1])
        test_dirs = {
            'test', 'tests', '__tests__', '__mocks__', 'e2e', 'cypress',
            'fixtures', 'bench', 'benchmark', 'benchmarks',
        }
        return not (source_dirs & test_dirs or NON_SHIPPED_FILE.search(posix))

    return not (NON_SHIPPED.search(posix) or NON_SHIPPED_FILE.search(posix))


def collect_files(directory: Path, include_tests: bool) -> list[Path]:
    files = []
    for root, dirs, filenames in os.walk(directory):
        under_src = 'src' in Path(root).relative_to(directory).parts
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_DIRS
            and not (d in AMBIGUOUS_OUTPUT_DIRS and not under_src)
        ]
        for fname in filenames:
            p = Path(root) / fname
            if p.suffix not in EXTENSIONS:
                continue
            rel = str(p.relative_to(directory))
            if not include_tests and not is_shipped(rel):
                continue
            files.append(p)
    return sorted(files)


def split_names(block: str) -> list[str]:
    """'get, has as _has' → ['get', 'has']  (source name, not local binding)."""
    out = []
    for part in block.split(','):
        part = part.strip()
        if not part:
            continue
        name = part.split(' as ')[0].strip()
        if re.fullmatch(r'\w+', name):
            out.append(name)
    return out


def extract_functions(
    files: list[Path],
) -> tuple[dict[str, int], dict[str, str], list[str]]:
    """Return ({function: usage_count}, {function: per-method package}, [warnings])."""
    counts: dict[str, int] = {}
    dot_pkgs: dict[str, str] = {}
    warnings: list[str] = []

    def bump(name: str, n: int = 1):
        counts[name] = counts.get(name, 0) + n

    for p in files:
        try:
            content = p.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        if 'lodash' not in content:
            continue
        content = strip_comments(content)
        if 'lodash' not in content:
            continue

        fp_functions = sorted({m.group(1) or '*' for m in RE_FP.finditer(content)})
        if fp_functions:
            warnings.append(
                f'{p}: uses lodash/fp ({", ".join(fp_functions)}) — manual semantic '
                'rewrite required; this warning alone is not a Condition C blocker'
            )

        for m in RE_SUBPATH.finditer(content):
            bump(m.group(1))
        for m in RE_REQ_SUBPATH.finditer(content):
            bump(m.group(1))
        for m in RE_NAMED.finditer(content):
            for n in split_names(m.group(1)):
                bump(n)
        for m in RE_REQ_NAMED.finditer(content):
            for n in split_names(m.group(1)):
                bump(n)
        for m in RE_DOT_PKG.finditer(content):
            name = m.group(1)
            bump(name)
            dot_pkgs[name] = f'lodash.{name}'

        # Whole-namespace imports: recover functions from member access.
        bindings = set(RE_DEFAULT.findall(content)) | set(RE_REQ_DEFAULT.findall(content))
        for binding in bindings:
            member = re.compile(rf'\b{re.escape(binding)}\.(\w+)\s*\(')
            hits = set(member.findall(content))
            if not hits:
                warnings.append(
                    f'{p}: imports the whole lodash namespace as `{binding}` '
                    f'but no `{binding}.fn()` calls found — usage may be undercounted'
                )
            for n in hits:
                bump(n)

    return counts, dot_pkgs, warnings


def ensure_env(workdir: Path, lodash_version: str, fresh: bool,
               extra_pkgs: list[str]) -> None:
    """Install lodash-es, es-toolkit and esbuild into a reusable scratch dir.

    `extra_pkgs` holds any per-method lodash packages the repo actually uses
    (`lodash.throttle`, …) so the lodash side of the comparison measures the
    real published artifact rather than a lodash-es stand-in.
    """
    if fresh and workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    stamp = ' '.join([lodash_version, *sorted(extra_pkgs)])
    marker = workdir / 'node_modules' / '.measure-ready'
    if marker.exists() and marker.read_text().strip() == stamp:
        return

    (workdir / 'package.json').write_text(
        json.dumps({'name': 'measure-env', 'private': True, 'type': 'module'}, indent=2)
    )
    print(f'Installing measurement environment in {workdir} …', file=sys.stderr)
    subprocess.run(
        ['npm', 'install', '--silent', '--no-audit', '--no-fund',
         f'lodash-es@{lodash_version}', 'es-toolkit', 'esbuild', *extra_pkgs],
        cwd=workdir, check=True, stdout=subprocess.DEVNULL,
    )
    marker.write_text(stamp)


def check_compat(workdir: Path, functions: list[str]) -> tuple[dict[str, str], list[str]]:
    """Resolve each detected name to its es-toolkit/compat export.

    Returns ({detected: canonical}, [missing]). Exact match wins; otherwise a
    case-insensitive match, which is what recovers the all-lowercase names that
    per-method packages force (`lodash.mergewith` → `mergeWith`).
    """
    script = (
        "import * as compat from 'es-toolkit/compat';"
        f"const fns = {json.dumps(functions)};"
        "const exported = Object.keys(compat)"
        ".filter((k) => typeof compat[k] === 'function');"
        "const lower = new Map(exported.map((k) => [k.toLowerCase(), k]));"
        "const out = {};"
        "for (const f of fns) {"
        "  if (typeof compat[f] === 'function') { out[f] = f; continue; }"
        "  const hit = lower.get(f.toLowerCase());"
        "  out[f] = hit ?? null;"
        "}"
        "console.log(JSON.stringify(out));"
    )
    check_file = workdir / 'compat-check.mjs'
    check_file.write_text(script)
    res = subprocess.run(
        ['node', str(check_file)], cwd=workdir,
        capture_output=True, text=True, check=True,
    )
    raw = json.loads(res.stdout.strip())
    resolved = {k: v for k, v in raw.items() if v}
    missing = sorted(k for k, v in raw.items() if not v)
    return resolved, missing


def dir_bytes(path: Path) -> int:
    """Apparent size of a directory tree, in bytes."""
    total = 0
    for root, _, filenames in os.walk(path):
        for fname in filenames:
            fp = Path(root) / fname
            try:
                total += fp.stat().st_size
            except OSError:
                continue
    return total


def install_footprint(workdir: Path, lodash_pkgs: list[str]) -> dict:
    """Unpacked install size of the lodash packages vs es-toolkit.

    For a Node-only project (CLI, bundler, server) nothing is shipped to a
    browser, so this — not the bundle delta — is the size metric that applies.
    es-toolkit ships every build format, so it is routinely the larger install.
    """
    nm = workdir / 'node_modules'
    before = {p: dir_bytes(nm / p) for p in lodash_pkgs if (nm / p).is_dir()}
    after = dir_bytes(nm / 'es-toolkit')
    return {
        'lodash_packages': before,
        'lodash_total': sum(before.values()),
        'es_toolkit': after,
        'delta': after - sum(before.values()),
    }


def bundle(workdir: Path, entry_name: str, source: str) -> tuple[int, int]:
    """Bundle+minify an entry, return (minified_bytes, gzip_bytes)."""
    entry = workdir / entry_name
    entry.write_text(source)
    out = workdir / f'{entry_name}.out.js'
    subprocess.run(
        [str(workdir / 'node_modules' / '.bin' / 'esbuild'), str(entry),
         '--bundle', '--minify', '--format=esm', f'--outfile={out}'],
        cwd=workdir, check=True, capture_output=True, text=True,
    )
    raw = out.read_bytes()
    return len(raw), len(gzip.compress(raw, 9))


def build_entries(functions: list[str], dot_pkgs: dict[str, str]) -> tuple[str, str]:
    """Two entry files importing the same function set from each library.

    A function sourced from a per-method package is imported from that package,
    since its published bundle differs from the lodash-es module of the same name.
    """
    use = 'console.log(' + ','.join(functions) + ');\n'
    lodash_src = ''.join(
        f"import {f} from '{dot_pkgs[f]}';\n" if f in dot_pkgs
        else f"import {f} from 'lodash-es/{f}.js';\n"
        for f in functions
    ) + use
    est_src = (
        'import { ' + ', '.join(functions) + " } from 'es-toolkit/compat';\n" + use
    )
    return lodash_src, est_src


def fmt(n: int) -> str:
    return f'{n:,} B'


def pct(before: int, after: int) -> str:
    if before == 0:
        return 'n/a'
    return f'{(after - before) / before * 100:+.1f}%'


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Measure the bundle-size impact of migrating lodash to es-toolkit'
    )
    parser.add_argument('directory', help='Repository root to analyze')
    parser.add_argument('--include-tests', action='store_true',
                        help='Also count lodash usage in test/docs/example paths')
    parser.add_argument('--lodash-version', default='4',
                        help='lodash-es version to compare against (default: 4)')
    parser.add_argument('--workdir', default=None,
                        help='Scratch dir for the measurement env (default: reusable temp dir)')
    parser.add_argument('--fresh', action='store_true',
                        help='Reinstall the measurement env from scratch')
    parser.add_argument('--json', action='store_true',
                        help='Emit machine-readable JSON instead of a table')
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        print(f'Error: {directory} is not a directory', file=sys.stderr)
        return 1

    files = collect_files(directory, args.include_tests)
    raw_counts, raw_dot_pkgs, warnings = extract_functions(files)

    if not raw_counts:
        msg = 'No lodash usage found in shipped source.'
        print(json.dumps({'error': msg}) if args.json else msg)
        return 1

    detected = sorted(raw_counts)
    workdir = Path(args.workdir) if args.workdir else (
        Path(tempfile.gettempdir()) / 'can-migrate-es-toolkit-measure'
    )

    try:
        ensure_env(workdir, args.lodash_version, args.fresh,
                   sorted(set(raw_dot_pkgs.values())))
        resolved, missing = check_compat(workdir, detected)

        # Re-key everything by the canonical es-toolkit/compat export name.
        counts: dict[str, int] = {}
        for name, canonical in resolved.items():
            counts[canonical] = counts.get(canonical, 0) + raw_counts[name]
        dot_pkgs = {resolved[n]: p for n, p in raw_dot_pkgs.items() if n in resolved}

        measurable = sorted(counts)
        if not measurable:
            msg = 'None of the detected functions exist in es-toolkit/compat.'
            print(json.dumps({'error': msg, 'missing': missing}) if args.json else msg)
            return 1
        lodash_src, est_src = build_entries(measurable, dot_pkgs)
        before_min, before_gz = bundle(workdir, 'entry-lodash.js', lodash_src)
        after_min, after_gz = bundle(workdir, 'entry-est.js', est_src)
        # Compare against every lodash package the repo actually draws from:
        # the per-method ones, plus lodash-es whenever any function came from a
        # regular `lodash` import. Counting only the per-method packages would
        # understate the baseline in a mixed codebase.
        baseline_pkgs = sorted(set(raw_dot_pkgs.values()))
        if any(n not in raw_dot_pkgs for n in raw_counts):
            baseline_pkgs.append('lodash-es')
        footprint = install_footprint(workdir, baseline_pkgs)
    except FileNotFoundError as e:
        print(f'Error: required tool not found ({e}). node and npm must be on PATH.',
              file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f'Error: command failed — {e.stderr or e}', file=sys.stderr)
        return 1

    result = {
        'files_scanned': len(files),
        'functions': dict(sorted(counts.items())),
        'per_method_packages': sorted(set(raw_dot_pkgs.values())),
        'missing_from_compat': missing,
        'warnings': warnings,
        'minified': {'lodash_es': before_min, 'es_toolkit': after_min,
                     'delta': after_min - before_min},
        'gzip': {'lodash_es': before_gz, 'es_toolkit': after_gz,
                 'delta': after_gz - before_gz},
        'install_footprint': footprint,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    print(f'\n{"=" * 62}')
    print('  Synthetic bundle-size measurement')
    print(f'{"=" * 62}\n')
    print(f'Files scanned:      {len(files)}')
    print(f'Distinct functions: {len(detected)} ({len(measurable)} measurable)')
    print('Top by usage:       ' + ', '.join(f'{n} ({c})' for n, c in top))
    if result['per_method_packages']:
        print('Per-method pkgs:    ' + ', '.join(result['per_method_packages']))
    print()

    if missing:
        print(f'⚠  Not in es-toolkit/compat ({len(missing)}): {", ".join(missing)}')
        print('   These are hard blockers — excluded from the measurement below.\n')
    for w in warnings:
        print(f'⚠  {w}')
    if warnings:
        print()

    print(f'{"":<20}{"minified":>14}{"gzip":>14}')
    print(f'{"-" * 48}')
    print(f'{"lodash-es":<20}{fmt(before_min):>14}{fmt(before_gz):>14}')
    print(f'{"es-toolkit/compat":<20}{fmt(after_min):>14}{fmt(after_gz):>14}')
    print(f'{"delta":<20}{fmt(after_min - before_min):>14}{fmt(after_gz - before_gz):>14}')
    print(f'{"":<20}{pct(before_min, after_min):>14}{pct(before_gz, after_gz):>14}')
    print()
    print('Measures the lodash slice only — the delta is what disappears from a')
    print("consumer's bundle, not the consumer's total bundle size.\n")

    fp = result['install_footprint']
    print('Install footprint (unpacked, apparent):')
    for pkg, size in sorted(fp['lodash_packages'].items()):
        print(f'  {pkg:<28}{fmt(size):>14}')
    print(f'  {"es-toolkit":<28}{fmt(fp["es_toolkit"]):>14}')
    print(f'  {"delta":<28}{fmt(fp["delta"]):>14}'
          f'  ({pct(fp["lodash_total"], fp["es_toolkit"])})')
    print()
    if fp['delta'] > 0:
        print('⚠  es-toolkit is the LARGER install. For a Node-only project — a CLI,')
        print('   bundler, or server that is never bundled for a browser — install size')
        print('   is the only size metric that applies, and this migration regresses it.')
        print('   Confirm the project actually ships code into a consumer bundle before')
        print('   citing the byte delta above as a benefit.\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
