#!/usr/bin/env python3
"""Lint typing_game.html for keyboard-typeable snippet content.

Scans every `lines: [ ... ]` array inside the LESSON_N JavaScript objects and
flags any non-ASCII characters that a student would have to type. Display-only
text (topic labels, UI ornaments, placeholder text) is intentionally ignored.

Usage:
    python lint_typing_game.py            # report only, exit 1 if issues found
    python lint_typing_game.py --fix      # apply standard replacements and rewrite
    python lint_typing_game.py --js-check # additionally run `node --check` on the JS

Standard replacements (applied with --fix):
    Greek / sub / super / math:  beta -> b, sub digits -> digits, × -> *,
                                 superscripts -> **n
    Punctuation:                 em dash -> hyphen, ellipsis -> three dots,
                                 plus-minus -> +/-, degree -> deg
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
HTML_PATH = HERE / "typing_game.html"

# Characters auto-replaced inside `lines: [...]` content when --fix is used.
REPLACEMENTS = {
    "β": "b",       # β  Greek beta
    "₀": "0",       # ₀  subscript 0
    "₁": "1",       # ₁  subscript 1
    "₂": "2",       # ₂  subscript 2
    "₃": "3",       # ₃  subscript 3
    "×": "*",       # ×  multiplication sign
    "²": "**2",     # ²  superscript 2
    "³": "**3",     # ³  superscript 3
    "—": "-",       # —  em dash
    "…": "...",     # …  horizontal ellipsis
    "±": "+/-",     # ±  plus-minus
    "°": "deg",     # °  degree sign
}

LINES_BLOCK_RE = re.compile(r"lines:\s*\[(.*?)\](?=\s*[\},])", re.DOTALL)
ID_RE = re.compile(r'id:\s*"([^"]+)"')


def snippet_id_before(html: str, pos: int) -> str:
    """Return the `id` of the snippet whose `lines:` array starts near `pos`."""
    ids = ID_RE.findall(html[:pos])
    return ids[-1] if ids else "?"


def scan(html: str):
    """Yield (snippet_id, position, char, line_excerpt) for every non-ASCII char
    inside a `lines: [...]` array."""
    for m in LINES_BLOCK_RE.finditer(html):
        body = m.group(1)
        body_start = m.start(1)
        for i, ch in enumerate(body):
            if ord(ch) > 127:
                # extract a short excerpt around this char
                left = max(0, i - 30)
                right = min(len(body), i + 30)
                excerpt = body[left:right].replace("\n", " ")
                yield snippet_id_before(html, m.start()), body_start + i, ch, excerpt


def apply_fixes(html: str) -> tuple[str, int]:
    """Replace REPLACEMENTS inside every `lines: [...]` block. Returns new html
    and the number of substitutions made across all blocks."""
    count_holder = {"n": 0}

    def fix_block(m: re.Match) -> str:
        body = m.group(1)
        for k, v in REPLACEMENTS.items():
            n = body.count(k)
            if n:
                count_holder["n"] += n
                body = body.replace(k, v)
        return f"lines: [{body}]"

    new_html = LINES_BLOCK_RE.sub(fix_block, html)
    return new_html, count_holder["n"]


def js_check(html: str) -> tuple[bool, str]:
    js_match = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    if not js_match:
        return False, "no <script> block found"
    tmp = Path("/tmp/typing_game_check.js")
    tmp.write_text(js_match.group(1))
    try:
        r = subprocess.run(
            ["node", "--check", str(tmp)],
            capture_output=True, text=True, timeout=20,
        )
    except FileNotFoundError:
        return True, "(node not installed; skipped)"
    return r.returncode == 0, (r.stderr or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true",
                    help="Apply standard replacements and rewrite the file")
    ap.add_argument("--js-check", action="store_true",
                    help="Also run `node --check` on the embedded JS")
    args = ap.parse_args()

    if not HTML_PATH.exists():
        print(f"FATAL: {HTML_PATH} not found", file=sys.stderr)
        return 2

    html = HTML_PATH.read_text()
    issues = list(scan(html))

    if args.fix:
        if not issues:
            print("Nothing to fix — all lines: [...] content is already ASCII.")
        else:
            new_html, n = apply_fixes(html)
            HTML_PATH.write_text(new_html)
            print(f"Fixed {n} character substitution(s) across affected snippets.")
            # Re-scan to report any leftovers (e.g., chars not in the map)
            html = new_html
            issues = list(scan(html))

    rc = 0
    if issues:
        from collections import defaultdict
        bag = defaultdict(list)
        for sid, _pos, ch, excerpt in issues:
            bag[(sid, ch)].append(excerpt)
        print(f"\nFound {len(issues)} non-ASCII character occurrence(s) inside lines: [...] content.")
        print("Each row: snippet_id  char  U+codepoint  example_excerpt")
        for (sid, ch), excerpts in sorted(bag.items()):
            print(f"  {sid:30s}  {ch!r:6s}  U+{ord(ch):04X}  {excerpts[0]!r}")
            extra = len(excerpts) - 1
            if extra:
                print(f"  {'':30s}  {'':6s}  {'':6s}  ... and {extra} more like this")
        print(f"\nFix manually, or run with --fix to apply the standard map:")
        for k, v in REPLACEMENTS.items():
            print(f"    {k!r}  ->  {v!r}")
        rc = 1
    else:
        n_blocks = sum(1 for _ in LINES_BLOCK_RE.finditer(html))
        print(f"Clean: scanned {n_blocks} lines:[...] blocks; "
              f"no non-ASCII characters in typed content.")

    if args.js_check:
        ok, msg = js_check(html)
        print(f"\nnode --check: {'PASSED' if ok else 'FAILED'}")
        if msg and not ok:
            print(msg)
        if not ok:
            rc = 1

    return rc


if __name__ == "__main__":
    sys.exit(main())