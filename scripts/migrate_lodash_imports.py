#!/usr/bin/env python3
"""
Replace lodash imports with es-toolkit/compat equivalents.

Usage:
    python migrate_lodash_imports.py <directory> [--dry-run | --write]

Modes:
    --dry-run   Preview changes without modifying files (default)
    --write     Apply changes to files in-place

Handles these import patterns:
    ES module imports:
        import _ from 'lodash'              → import _ from 'es-toolkit/compat'
        import { pick, chunk } from 'lodash' → import { pick, chunk } from 'es-toolkit/compat'
        import pick from 'lodash/pick'       → import { pick } from 'es-toolkit/compat'
        import * as _ from 'lodash'          → import * as _ from 'es-toolkit/compat'

    CommonJS requires:
        const _ = require('lodash')          → const _ = require('es-toolkit/compat')
        const { pick } = require('lodash')   → const { pick } = require('es-toolkit/compat')
        const pick = require('lodash/pick')  → const { pick } = require('es-toolkit/compat')

    Per-method packages (all-lowercase on npm, so the export name is recovered
    from a lookup table):
        import throttle from 'lodash.throttle'    → import { throttle } from 'es-toolkit/compat'
        require('lodash.mergewith')               → const { mergeWith } = require('es-toolkit/compat')

    Also handles lodash-es as a source.

    Does NOT handle:
        lodash/fp (functional programming variant — no es-toolkit equivalent)
        Dynamic requires or template-literal imports
"""

import argparse
import os
import re
import sys
from pathlib import Path

EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.mts', '.cts',
              '.vue', '.svelte', '.astro'}

# Functions that es-toolkit/compat explicitly does NOT support.
# Files using these are skipped with a warning.
HARD_BLOCKERS = {'sortedUniq', 'sortedUniqBy', 'mixin', 'noConflict', 'runInContext'}

# ── regex patterns ──────────────────────────────────────────────────────────

# ES module: import <binding> from 'lodash...'
RE_ESM_FULL = re.compile(
    r"""^(\s*import\s+)"""
    r"""(.+?)"""
    r"""(\s+from\s+)(['"])(lodash(?:-es|-unified)?)\4"""
    r"""(\s*;?\s*)$""",
    re.MULTILINE,
)

# ES module: import <default> from 'lodash/<func>'
RE_ESM_SUBPATH = re.compile(
    r"""^(\s*import\s+)"""
    r"""(\w+)"""
    r"""(\s+from\s+)(['"])lodash(?:-es)?/(\w+)\4"""
    r"""(\s*;?\s*)$""",
    re.MULTILINE,
)

# ES module: export { castArray as ensureArray } from 'lodash'
# A re-export is an import for migration purposes, and the `{ … }` block already
# has the shape the target needs, so only the specifier changes.
RE_ESM_REEXPORT = re.compile(
    r"""^(\s*export\s*\{[^}]*\}\s*from\s+)(['"])(lodash(?:-es|-unified)?)\2"""
    r"""(\s*;?\s*)$""",
    re.MULTILINE,
)

# ES module: import * as <name> from 'lodash'
RE_ESM_STAR = re.compile(
    r"""^(\s*import\s+\*\s+as\s+)"""
    r"""(\w+)"""
    r"""(\s+from\s+)(['"])(lodash(?:-es|-unified)?)\4"""
    r"""(\s*;?\s*)$""",
    re.MULTILINE,
)

# CommonJS: const/let/var <binding> = require('lodash')
RE_CJS_FULL = re.compile(
    r"""^(\s*(?:const|let|var)\s+)"""
    r"""(.+?)"""
    r"""(\s*=\s*require\s*\(\s*)(['"])(lodash(?:-es|-unified)?)\4(\s*\)\s*;?\s*)$""",
    re.MULTILINE,
)

# CommonJS: const/let/var <name> = require('lodash/<func>')
RE_CJS_SUBPATH = re.compile(
    r"""^(\s*(?:const|let|var)\s+)"""
    r"""(\w+)"""
    r"""(\s*=\s*require\s*\(\s*)(['"])lodash(?:-es)?/(\w+)\4(\s*\)\s*;?\s*)$""",
    re.MULTILINE,
)

# Per-method packages (`lodash.throttle`, `lodash.mergewith`) are published
# all-lowercase, so the package name alone cannot tell you the export's casing.
# These are every lodash function whose canonical name is not already lowercase.
_CAMEL_NAMES = (
    'assignIn', 'assignInWith', 'assignWith', 'bindAll', 'bindKey',
    'camelCase', 'castArray', 'cloneDeep', 'cloneDeepWith', 'cloneWith',
    'conformsTo', 'countBy', 'curryRight', 'defaultTo', 'defaultsDeep',
    'differenceBy', 'differenceWith', 'dropRight', 'dropRightWhile',
    'dropWhile', 'eachRight', 'endsWith', 'entriesIn', 'escapeRegExp',
    'extendWith', 'findIndex', 'findKey', 'findLast', 'findLastIndex',
    'findLastKey', 'flatMap', 'flatMapDeep', 'flatMapDepth', 'flattenDeep',
    'flattenDepth', 'flowRight', 'forEach', 'forEachRight', 'forIn',
    'forInRight', 'forOwn', 'forOwnRight', 'fromPairs', 'functionsIn',
    'groupBy', 'hasIn', 'inRange', 'indexOf', 'intersectionBy',
    'intersectionWith', 'invertBy', 'invokeMap', 'isArguments', 'isArray',
    'isArrayBuffer', 'isArrayLike', 'isArrayLikeObject', 'isBoolean',
    'isBuffer', 'isDate', 'isElement', 'isEmpty', 'isEqual', 'isEqualWith',
    'isError', 'isFinite', 'isFunction', 'isInteger', 'isLength', 'isMap',
    'isMatch', 'isMatchWith', 'isNaN', 'isNative', 'isNil', 'isNull',
    'isNumber', 'isObject', 'isObjectLike', 'isPlainObject', 'isRegExp',
    'isSafeInteger', 'isSet', 'isString', 'isSymbol', 'isTypedArray',
    'isUndefined', 'isWeakMap', 'isWeakSet', 'kebabCase', 'keyBy', 'keysIn',
    'lastIndexOf', 'lowerCase', 'lowerFirst', 'mapKeys', 'mapValues',
    'matchesProperty', 'maxBy', 'meanBy', 'mergeWith', 'methodOf', 'minBy',
    'nthArg', 'omitBy', 'orderBy', 'overArgs', 'overEvery', 'overSome',
    'padEnd', 'padStart', 'parseInt', 'partialRight', 'pickBy',
    'propertyOf', 'pullAll', 'pullAllBy', 'pullAllWith', 'pullAt',
    'rangeRight', 'reduceRight', 'sampleSize', 'setWith', 'snakeCase',
    'sortBy', 'sortedIndex', 'sortedIndexBy', 'sortedIndexOf',
    'sortedLastIndex', 'sortedLastIndexBy', 'sortedLastIndexOf',
    'sortedUniq', 'sortedUniqBy', 'startCase', 'startsWith', 'stubArray',
    'stubFalse', 'stubObject', 'stubString', 'stubTrue', 'sumBy',
    'takeRight', 'takeRightWhile', 'takeWhile', 'toArray', 'toFinite',
    'toInteger', 'toLength', 'toLower', 'toNumber', 'toPairs', 'toPairsIn',
    'toPath', 'toPlainObject', 'toSafeInteger', 'toString', 'toUpper',
    'trimEnd', 'trimStart', 'unionBy', 'unionWith', 'uniqBy', 'uniqWith',
    'uniqueId', 'unzipWith', 'updateWith', 'upperCase', 'upperFirst',
    'valuesIn', 'xorBy', 'xorWith', 'zipObject', 'zipObjectDeep', 'zipWith'
)
LOWER_TO_CANONICAL = {n.lower(): n for n in _CAMEL_NAMES}

# ES module: import throttle from 'lodash.throttle'
RE_ESM_DOT_PKG = re.compile(
    r"""^(\s*import\s+)"""
    r"""(\w+)"""
    r"""(\s+from\s+)(['"])lodash\.([a-z][a-z0-9]*)\4"""
    r"""(\s*;?\s*)$""",
    re.MULTILINE,
)

# CommonJS: const throttle = require('lodash.throttle')
RE_CJS_DOT_PKG = re.compile(
    r"""^(\s*(?:const|let|var)\s+)"""
    r"""(\w+)"""
    r"""(\s*=\s*require\s*\(\s*)(['"])lodash\.([a-z][a-z0-9]*)\4(\s*\)\s*;?\s*)$""",
    re.MULTILINE,
)

# lodash/fp detection (unsupported)
RE_FP = re.compile(r"""['"]lodash(?:-es)?/fp(?:/\w+)?['"]""")

TARGET = 'es-toolkit/compat'


def canonical(lowercase_name: str) -> str:
    """`throttle` → `throttle`, `mergewith` → `mergeWith`."""
    return LOWER_TO_CANONICAL.get(lowercase_name, lowercase_name)


def has_hard_blocker(content: str) -> list[str]:
    """Return hard-blocker functions that are actually imported from lodash.

    Matching bare word boundaries over the whole file produces false positives —
    `mixin` and `noConflict` are ordinary identifiers in plenty of codebases, and
    a single hit would skip the entire file. Only lodash import sites count.
    """
    found = set()

    for m in RE_ESM_SUBPATH.finditer(content):
        if m.group(5) in HARD_BLOCKERS:
            found.add(m.group(5))
    for m in RE_CJS_SUBPATH.finditer(content):
        if m.group(5) in HARD_BLOCKERS:
            found.add(m.group(5))
    for regex in (RE_ESM_DOT_PKG, RE_CJS_DOT_PKG):
        for m in regex.finditer(content):
            if canonical(m.group(5)) in HARD_BLOCKERS:
                found.add(canonical(m.group(5)))

    for regex, group in ((RE_ESM_FULL, 2), (RE_CJS_FULL, 2)):
        for m in regex.finditer(content):
            binding = m.group(group).strip()
            if binding.startswith('{'):
                names = binding.strip('{} ').split(',')
                for name in names:
                    name = name.split(' as ')[0].strip()
                    if name in HARD_BLOCKERS:
                        found.add(name)
            else:
                # Whole namespace: look for `_.mixin(` style calls.
                for fn in HARD_BLOCKERS:
                    if re.search(rf'\b{re.escape(binding)}\.{fn}\s*\(', content):
                        found.add(fn)

    for m in RE_ESM_STAR.finditer(content):
        for fn in HARD_BLOCKERS:
            if re.search(rf'\b{re.escape(m.group(2))}\.{fn}\s*\(', content):
                found.add(fn)

    return sorted(found)


def migrate_content(content: str) -> tuple[str, list[str]]:
    """
    Replace lodash imports with es-toolkit/compat.
    Returns (new_content, list_of_changes).
    """
    changes: list[str] = []

    # lodash/fp → skip entirely (caller handles)
    if RE_FP.search(content):
        return content, ['SKIP: lodash/fp usage detected (not supported by es-toolkit)']

    def replace_esm_full(m):
        indent, binding, from_kw, quote, _pkg, tail = m.groups()
        changes.append(f'ESM full: {m.group(0).strip()}')
        return f"{indent}{binding}{from_kw}{quote}{TARGET}{quote}{tail}"

    def replace_esm_subpath(m):
        indent, name, from_kw, quote, func, tail = m.groups()
        changes.append(f'ESM subpath: {m.group(0).strip()}')
        # `import _get from 'lodash/get'` keeps its local binding via `as`.
        spec = func if name == func else f'{func} as {name}'
        return f"{indent}{{ {spec} }}{from_kw}{quote}{TARGET}{quote}{tail}"

    def replace_esm_star(m):
        indent, name, from_kw, quote, _pkg, tail = m.groups()
        changes.append(f'ESM star: {m.group(0).strip()}')
        return f"{indent}* as {name}{from_kw}{quote}{TARGET}{quote}{tail}"

    def replace_cjs_full(m):
        indent, binding, eq_require, quote, _pkg, tail = m.groups()
        changes.append(f'CJS full: {m.group(0).strip()}')
        return f"{indent}{binding}{eq_require}{quote}{TARGET}{quote}{tail}"

    def replace_cjs_subpath(m):
        indent, name, eq_require, quote, func, tail = m.groups()
        changes.append(f'CJS subpath: {m.group(0).strip()}')
        # const pick = require('lodash/pick') → const { pick } = require('es-toolkit/compat')
        # const _pick = require('lodash/pick') → const { pick: _pick } = require(…)
        spec = func if name == func else f'{func}: {name}'
        return f"{indent}{{ {spec} }}{eq_require}{quote}{TARGET}{quote}{tail}"

    def replace_esm_dot_pkg(m):
        indent, name, from_kw, quote, lower, tail = m.groups()
        func = canonical(lower)
        changes.append(f'ESM per-method pkg: {m.group(0).strip()}')
        spec = func if name == func else f'{func} as {name}'
        return f"{indent}{{ {spec} }}{from_kw}{quote}{TARGET}{quote}{tail}"

    def replace_cjs_dot_pkg(m):
        indent, name, eq_require, quote, lower, tail = m.groups()
        func = canonical(lower)
        changes.append(f'CJS per-method pkg: {m.group(0).strip()}')
        spec = func if name == func else f'{func}: {name}'
        return f"{indent}{{ {spec} }}{eq_require}{quote}{TARGET}{quote}{tail}"

    def replace_esm_reexport(m):
        head, quote, _pkg, tail = m.groups()
        changes.append(f'ESM re-export: {m.group(0).strip()}')
        return f"{head}{quote}{TARGET}{quote}{tail}"

    content = RE_ESM_REEXPORT.sub(replace_esm_reexport, content)
    content = RE_ESM_DOT_PKG.sub(replace_esm_dot_pkg, content)
    content = RE_CJS_DOT_PKG.sub(replace_cjs_dot_pkg, content)
    content = RE_ESM_STAR.sub(replace_esm_star, content)
    content = RE_ESM_SUBPATH.sub(replace_esm_subpath, content)
    content = RE_ESM_FULL.sub(replace_esm_full, content)
    content = RE_CJS_SUBPATH.sub(replace_cjs_subpath, content)
    content = RE_CJS_FULL.sub(replace_cjs_full, content)

    return content, changes


def collect_files(directory: str) -> list[Path]:
    """Collect all source files under directory."""
    files = []
    skip = {'node_modules', '.git', '.next', '.nuxt',
            'coverage', '.turbo', '.cache', '.nx'}
    # Build-output names that double as source directory names: skipped only
    # outside `src/`, since `src/lib/` and `src/build/` are hand-written.
    ambiguous = {'dist', 'build', 'out', 'lib'}
    root_path = Path(directory)
    for root, dirs, filenames in os.walk(directory):
        under_src = 'src' in Path(root).relative_to(root_path).parts
        # Prune in place — testing only the current basename still descends into
        # node_modules' children and would rewrite dependency source.
        dirs[:] = [
            d for d in dirs
            if d not in skip and not (d in ambiguous and not under_src)
        ]
        for fname in filenames:
            p = Path(root) / fname
            if p.suffix in EXTENSIONS:
                files.append(p)
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description='Migrate lodash imports to es-toolkit/compat'
    )
    parser.add_argument('directory', help='Root directory to scan')
    parser.add_argument(
        '--write', action='store_true',
        help='Apply changes in-place (default: dry-run)'
    )
    parser.add_argument(
        '--dry-run', action='store_true', default=True,
        help='Preview changes without writing (default)'
    )
    args = parser.parse_args()

    if args.write:
        args.dry_run = False

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f'Error: {directory} is not a directory', file=sys.stderr)
        sys.exit(1)

    files = collect_files(directory)
    if not files:
        print('No source files found.')
        return

    total_changes = 0
    skipped_files: list[tuple[str, str]] = []
    changed_files: list[tuple[str, list[str]]] = []

    for fpath in files:
        content = fpath.read_text(encoding='utf-8', errors='replace')

        # Check for hard blockers
        blockers = has_hard_blocker(content)
        if blockers:
            skipped_files.append((str(fpath), f'Hard blocker: {", ".join(blockers)}'))
            continue

        new_content, changes = migrate_content(content)

        if not changes:
            continue

        # Check for skip markers
        if any(c.startswith('SKIP:') for c in changes):
            skipped_files.append((str(fpath), changes[0]))
            continue

        rel = os.path.relpath(fpath, directory)
        changed_files.append((rel, changes))
        total_changes += len(changes)

        if not args.dry_run:
            fpath.write_text(new_content, encoding='utf-8')

    # ── Summary ─────────────────────────────────────────────────────────
    mode = 'DRY RUN' if args.dry_run else 'APPLIED'
    print(f'\n{"=" * 60}')
    print(f'  Migration Report ({mode})')
    print(f'{"=" * 60}\n')

    if changed_files:
        print(f'Files {"to change" if args.dry_run else "changed"}: {len(changed_files)}')
        print(f'Total replacements: {total_changes}\n')
        for rel, changes in changed_files:
            print(f'  {rel}')
            for c in changes:
                print(f'    → {c}')
        print()

    if skipped_files:
        print(f'Skipped files: {len(skipped_files)}')
        for fpath, reason in skipped_files:
            rel = os.path.relpath(fpath, directory)
            print(f'  {rel}: {reason}')
        print()

    if not changed_files and not skipped_files:
        print('No lodash imports found.\n')

    if args.dry_run and changed_files:
        print('Run with --write to apply these changes.\n')


if __name__ == '__main__':
    main()
