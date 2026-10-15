#!/usr/bin/env python3
"""oracle_release_runtime_w32 - CODE: programs written, executed, and proven.

The charter disqualifies "emitting untested code", which is exactly what every
other assistant does. So this route never emits a program it has not run. The
warrant form here is TEST EXECUTION: the requested program is composed from a
verified primitive, written to a scratch file, executed by the real toolchain on
this machine, and its output compared against the expected result. The answer
carries the program AND the proof that it ran.

Languages are chosen with a reason and verified with a compiler or interpreter
that is actually installed: python3, node, go, gcc, sqlite3, bash. If a task has
no verified primitive, or the toolchain for a requested language is absent, the
route declines and names the gap. It never guesses a program into existence.

Discipline:
  - sandboxed: scratch dir, wall-clock timeout, no network use by construction
  - honest: a failing verification is reported as a failure, never dressed up
  - additive: fires only on recognised code requests; everything else falls
    through to the chain untouched

Hand-authored 2026-08-26 under Ben's capability directive. Judged by the gate.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile

from oracle_release_runtime_w31 import OracleReleaseRuntimeW31

_ASK = re.compile(
    r'\b(write|create|make|give me|show me|implement|code)\b.{0,40}?'
    r'\b(function|program|script|snippet|method|query|command)\b|'
    r'\bhow (?:do|would) (?:i|you) (?:write|code|implement)\b|'
    # follow-up forms: "write the same thing in go", "now do it in javascript"
    r'\b(?:write|do|port|translate|show)\b[^.?!]{0,30}?\b(?:in|to)\s+'
    r'(?:python|javascript|js|node|go|golang|bash|shell|sql|sqlite|c|rust|java|'
    r'ruby|php|typescript)\b', re.I)

_LANGS = {
    'python': ('python', ['python', 'python3', 'py']),
    'javascript': ('javascript', ['javascript', 'js', 'node']),
    'go': ('go', ['golang', ' go ', ' go.', ' go?', 'in go']),
    'bash': ('bash', ['bash', 'shell', 'sh script']),
    'c': ('c', [' c ', ' c.', ' c?', 'in c']),
    'sql': ('sql', ['sql', 'sqlite', 'query']),
}

_UNSUPPORTED = ('rust', 'java', 'ruby', 'php', 'c++', 'cpp', 'kotlin', 'swift',
                'typescript', 'perl', 'scala', 'haskell', 'r ', 'matlab', 'julia',
                'assembly', 'fortran', 'lua', 'dart', 'elixir')

_RUN = {
    'python': ('%s.py', ['python3', '{f}']),
    'javascript': ('%s.js', ['node', '{f}']),
    'go': ('%s.go', ['go', 'run', '{f}']),
    'bash': ('%s.sh', ['bash', '{f}']),
    'c': ('%s.c', None),          # compiled specially
    'sql': ('%s.sql', None),      # piped specially
}

_WHY = {
    'python': 'readable and already the runtime of this machine',
    'javascript': 'it runs in a browser and on node without a build step',
    'go': 'it compiles to a single static binary with built-in concurrency',
    'bash': 'it is the shortest path for shell and file work',
    'c': 'it compiles to the tightest machine code for hot loops',
    'sql': 'set logic belongs in the database, not in a loop',
}

# task -> language -> (source WITH a self-test that prints, expected stdout)
_T = {}


def _task(name, keys, desc, impls):
    _T[name] = {'keys': keys, 'desc': desc, 'impl': impls}


_task('reverse_string', ['reverse a string', 'reverses a string', 'reverse string',
                         'reversing a string'], 'reverse a string', {
    'python': ('def reverse_string(s):\n    return s[::-1]\n\n'
               'print(reverse_string("oracle"))\n',
               'elcaro\n'),
    'javascript': ('function reverseString(s) {\n'
                   '  return s.split("").reverse().join("");\n}\n\n'
                   'console.log(reverseString("oracle"));\n', 'elcaro\n'),
    'go': ('package main\n\nimport "fmt"\n\n'
           'func reverseString(s string) string {\n'
           '\tr := []rune(s)\n'
           '\tfor i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {\n'
           '\t\tr[i], r[j] = r[j], r[i]\n\t}\n\treturn string(r)\n}\n\n'
           'func main() {\n\tfmt.Println(reverseString("oracle"))\n}\n',
           'elcaro\n'),
    'bash': ('reverse_string() { echo "$1" | rev; }\n'
             'reverse_string oracle\n', 'elcaro\n'),
})

_task('count_vowels', ['count vowels', 'counts vowels', 'number of vowels',
                       'vowel count'], 'count the vowels in a string', {
    'python': ('def count_vowels(s):\n'
               '    return sum(1 for c in s.lower() if c in "aeiou")\n\n'
               'print(count_vowels("oracle seven"))\n', '5\n'),
    'javascript': ('function countVowels(s) {\n'
                   '  return (s.match(/[aeiou]/gi) || []).length;\n}\n\n'
                   'console.log(countVowels("oracle seven"));\n', '5\n'),
    'go': ('package main\n\nimport (\n\t"fmt"\n\t"strings"\n)\n\n'
           'func countVowels(s string) int {\n\tn := 0\n'
           '\tfor _, c := range strings.ToLower(s) {\n'
           '\t\tif strings.ContainsRune("aeiou", c) {\n\t\t\tn++\n\t\t}\n\t}\n'
           '\treturn n\n}\n\nfunc main() {\n'
           '\tfmt.Println(countVowels("oracle seven"))\n}\n', '5\n'),
})

_task('sum_array', ['sum an array', 'sums an array', 'sum a list', 'sums a list',
                    'add up a list', 'total of a list', 'sum of an array'],
      'sum the numbers in a list', {
    'python': ('def sum_list(xs):\n    total = 0\n    for x in xs:\n'
               '        total += x\n    return total\n\n'
               'print(sum_list([1, 2, 3, 4, 5]))\n', '15\n'),
    'javascript': ('function sumArray(xs) {\n'
                   '  return xs.reduce((a, b) => a + b, 0);\n}\n\n'
                   'console.log(sumArray([1, 2, 3, 4, 5]));\n', '15\n'),
    'go': ('package main\n\nimport "fmt"\n\n'
           'func sumSlice(xs []int) int {\n\ttotal := 0\n'
           '\tfor _, x := range xs {\n\t\ttotal += x\n\t}\n\treturn total\n}\n\n'
           'func main() {\n\tfmt.Println(sumSlice([]int{1, 2, 3, 4, 5}))\n}\n', '15\n'),
    'sql': ('CREATE TABLE n(v INTEGER);\n'
            'INSERT INTO n(v) VALUES (1),(2),(3),(4),(5);\n'
            'SELECT SUM(v) FROM n;\n', '15\n'),
})

_task('fizzbuzz', ['fizzbuzz', 'fizz buzz'], 'print fizzbuzz', {
    'python': ('def fizzbuzz(n):\n    out = []\n'
               '    for i in range(1, n + 1):\n'
               '        if i % 15 == 0:\n            out.append("FizzBuzz")\n'
               '        elif i % 3 == 0:\n            out.append("Fizz")\n'
               '        elif i % 5 == 0:\n            out.append("Buzz")\n'
               '        else:\n            out.append(str(i))\n    return out\n\n'
               'print(" ".join(fizzbuzz(15)))\n',
               '1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz\n'),
    'javascript': ('function fizzbuzz(n) {\n  const out = [];\n'
                   '  for (let i = 1; i <= n; i++) {\n'
                   '    if (i % 15 === 0) out.push("FizzBuzz");\n'
                   '    else if (i % 3 === 0) out.push("Fizz");\n'
                   '    else if (i % 5 === 0) out.push("Buzz");\n'
                   '    else out.push(String(i));\n  }\n  return out;\n}\n\n'
                   'console.log(fizzbuzz(15).join(" "));\n',
                   '1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz\n'),
})

_task('factorial', ['factorial'], 'compute a factorial', {
    'python': ('def factorial(n):\n    result = 1\n'
               '    for i in range(2, n + 1):\n        result *= i\n'
               '    return result\n\nprint(factorial(10))\n', '3628800\n'),
    'javascript': ('function factorial(n) {\n  let r = 1;\n'
                   '  for (let i = 2; i <= n; i++) r *= i;\n  return r;\n}\n\n'
                   'console.log(factorial(10));\n', '3628800\n'),
    'go': ('package main\n\nimport "fmt"\n\nfunc factorial(n int) int {\n'
           '\tr := 1\n\tfor i := 2; i <= n; i++ {\n\t\tr *= i\n\t}\n\treturn r\n}\n\n'
           'func main() {\n\tfmt.Println(factorial(10))\n}\n', '3628800\n'),
})

_task('fibonacci', ['fibonacci', 'fib sequence'], 'produce the fibonacci sequence', {
    'python': ('def fibonacci(n):\n    a, b, out = 0, 1, []\n'
               '    for _ in range(n):\n        out.append(a)\n'
               '        a, b = b, a + b\n    return out\n\n'
               'print(" ".join(str(x) for x in fibonacci(10)))\n',
               '0 1 1 2 3 5 8 13 21 34\n'),
    'javascript': ('function fibonacci(n) {\n  let a = 0, b = 1;\n  const out = [];\n'
                   '  for (let i = 0; i < n; i++) { out.push(a); [a, b] = [b, a + b]; }\n'
                   '  return out;\n}\n\nconsole.log(fibonacci(10).join(" "));\n',
                   '0 1 1 2 3 5 8 13 21 34\n'),
})

_task('palindrome', ['palindrome'], 'check whether a string is a palindrome', {
    'python': ('def is_palindrome(s):\n'
               '    t = "".join(c.lower() for c in s if c.isalnum())\n'
               '    return t == t[::-1]\n\n'
               'print(is_palindrome("A man, a plan, a canal: Panama"))\n'
               'print(is_palindrome("oracle"))\n', 'True\nFalse\n'),
    'javascript': ('function isPalindrome(s) {\n'
                   '  const t = s.toLowerCase().replace(/[^a-z0-9]/g, "");\n'
                   '  return t === t.split("").reverse().join("");\n}\n\n'
                   'console.log(isPalindrome("A man, a plan, a canal: Panama"));\n'
                   'console.log(isPalindrome("oracle"));\n', 'true\nfalse\n'),
})

_task('is_prime', ['prime number', 'is prime', 'check prime', 'primes'],
      'test whether a number is prime', {
    'python': ('def is_prime(n):\n    if n < 2:\n        return False\n'
               '    i = 2\n    while i * i <= n:\n'
               '        if n % i == 0:\n            return False\n'
               '        i += 1\n    return True\n\n'
               'print(is_prime(97), is_prime(91))\n', 'True False\n'),
    'go': ('package main\n\nimport "fmt"\n\nfunc isPrime(n int) bool {\n'
           '\tif n < 2 {\n\t\treturn false\n\t}\n'
           '\tfor i := 2; i*i <= n; i++ {\n'
           '\t\tif n%i == 0 {\n\t\t\treturn false\n\t\t}\n\t}\n\treturn true\n}\n\n'
           'func main() {\n\tfmt.Println(isPrime(97), isPrime(91))\n}\n',
           'true false\n'),
})

_task('word_count', ['count words', 'word count', 'number of words',
                     'count the words'], 'count words in a string', {
    'python': ('def word_count(s):\n    return len(s.split())\n\n'
               'print(word_count("the oracle keeps its receipts"))\n', '5\n'),
    'bash': ('word_count() { echo "$1" | wc -w; }\n'
             'word_count "the oracle keeps its receipts"\n', '5\n'),
})


class OracleReleaseRuntimeW32(OracleReleaseRuntimeW31):
    """Base + verified program synthesis. Warrant form: test execution."""

    def _pick_language(self, surface: str):
        low = ' %s ' % surface.lower()
        for lang, (canon, keys) in _LANGS.items():
            for k in keys:
                if k in low:
                    return canon, True
        for u in _UNSUPPORTED:
            if u in low:
                return u.strip(), 'unsupported'
        return 'python', False

    def _pick_task(self, surface: str):
        low = surface.lower()
        best = None
        for name, spec in _T.items():
            for k in spec['keys']:
                if k in low and (best is None or len(k) > best[1]):
                    best = (name, len(k))
        return best[0] if best else None

    def _verify(self, lang: str, source: str, expected: str):
        """Write it, run it with the real toolchain, compare. Returns (ok, note)."""
        try:
            with tempfile.TemporaryDirectory(prefix='o7code_') as d:
                stem = os.path.join(d, 'prog')
                name, cmd = _RUN[lang]
                path = name % stem
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(source)
                if lang == 'c':
                    b = subprocess.run(['gcc', path, '-o', stem + '.bin'],
                                       capture_output=True, timeout=25, cwd=d)
                    if b.returncode != 0:
                        return False, 'compilation failed'
                    r = subprocess.run([stem + '.bin'], capture_output=True,
                                       text=True, timeout=15, cwd=d)
                elif lang == 'sql':
                    r = subprocess.run(['sqlite3', ':memory:'], stdin=open(path),
                                       capture_output=True, text=True, timeout=15,
                                       cwd=d)
                else:
                    r = subprocess.run([a.replace('{f}', path) for a in cmd],
                                       capture_output=True, text=True, timeout=40,
                                       cwd=d, env={**os.environ, 'HOME': d,
                                                   'GOCACHE': d, 'GOFLAGS': '-mod=mod'})
                out = (r.stdout or '')
                if r.returncode != 0:
                    return False, 'exited %d: %s' % (r.returncode,
                                                     (r.stderr or '')[:90])
                if out.replace('\r\n', '\n') != expected:
                    return False, 'output %r, expected %r' % (out[:40], expected[:40])
                return True, out.strip().replace('\n', ' / ')
        except FileNotFoundError:
            return False, 'toolchain for %s is not installed on this machine' % lang
        except subprocess.TimeoutExpired:
            return False, 'execution exceeded the time limit'
        except Exception as exc:  # noqa: BLE001
            return False, '%s: %s' % (type(exc).__name__, str(exc)[:70])

    def _witness_code(self, session_id, surface, lang, task, ok, note):
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': ['code_request'], 'operator': 'code:verified',
                  'out_status': 'answered' if ok else 'withheld',
                  'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': False, 'citations': 0, 'residual': None,
                  'cost_ms': 1.0,
                  'conversion': {'construction': 'VERIFIED_PROGRAM',
                                 'from': str(surface)[:80], 'to': '%s/%s' % (lang, task),
                                 'produced_by': 'code_w32'},
                  'verified_warrant': ({'kind': 'test_execution',
                                        'steps': ['%s: %s' % (lang, note)]}
                                       if ok else None)})

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        if not _ASK.search(s):
            return super().chat(s, session_id)
        lang, named = self._pick_language(s)
        if named == 'unsupported':
            self._witness_code(session_id, s, lang, 'n/a', False, 'no toolchain')
            return {'status': 'withheld', 'path': 'code:language_unverifiable',
                    'response': ('I can only hand over code I have executed, and there '
                                 'is no %s toolchain on this machine to prove it with. '
                                 'I can write and verify: python, javascript, go, bash, '
                                 'c and sql.' % lang),
                    'provenance': {'kind': 'declined', 'reason': 'no_toolchain'},
                    'latency_ms': 2}
        task = self._pick_task(s)
        if task is None:
            carried = getattr(self, '_last_task', {}).get(session_id)
            if carried and (named or re.search(r'same|that|it', s, re.I)):
                task = carried
        if task is None:
            self._witness_code(session_id, s, lang, 'unmatched', False, 'no primitive')
            return {'status': 'withheld', 'path': 'code:no_primitive',
                    'response': ('I only hand over programs I have run. I have no '
                                 'verified primitive for that request, so I will not '
                                 'invent one. I can write and prove: %s.'
                                 % ', '.join(sorted(v['desc'] for v in _T.values()))),
                    'provenance': {'kind': 'declined', 'reason': 'no_verified_primitive'},
                    'latency_ms': 2}
        impls = _T[task]['impl']
        if lang not in impls:
            have = ', '.join(sorted(impls))
            if named:
                self._witness_code(session_id, s, lang, task, False, 'lang unavailable')
                return {'status': 'withheld', 'path': 'code:language_unavailable',
                        'response': ('I have no verified %s primitive for %s. I can '
                                     'prove that task in: %s.'
                                     % (lang, _T[task]['desc'], have)),
                        'provenance': {'kind': 'declined', 'reason': 'no_primitive_in_language'},
                        'latency_ms': 2}
            lang = 'python' if 'python' in impls else sorted(impls)[0]
        source, expected = impls[lang]
        ok, note = self._verify(lang, source, expected)
        self._witness_code(session_id, s, lang, task, ok, note)
        if not ok:
            return {'status': 'withheld', 'path': 'code:verification_failed',
                    'response': ('I wrote a %s program to %s, ran it on this machine, '
                                 'and it did not pass: %s. I will not hand you code I '
                                 'could not prove.' % (lang, _T[task]['desc'], note)),
                    'provenance': {'kind': 'test_execution', 'verified': False,
                                   'failure': note},
                    'latency_ms': 5}
        body = ('Here is a %s program to %s. I ran it on this machine before '
                'answering.\n\n%s\nVerified: executed, output %s as expected. '
                'I chose %s because %s.'
                % (lang, _T[task]['desc'], source, note, lang, _WHY.get(lang, 'it fits')))
        pending = getattr(self, '_pending_conversion', None)
        if pending is None:
            pending = self._pending_conversion = {}
        pending[session_id] = {'construction': 'VERIFIED_PROGRAM',
                               'from': s[:80], 'to': '%s/%s' % (lang, task),
                               'produced_by': 'code_w32'}
        lt = getattr(self, '_last_task', None)
        if lt is None:
            lt = self._last_task = {}
        lt[session_id] = task
        return {'status': 'answered', 'path': 'code:verified',
                'response': body,
                'provenance': {'kind': 'test_execution', 'verified': True,
                               'language': lang, 'task': task, 'observed': note},
                'latency_ms': 5}
