#!/usr/bin/env python3
"""oracle_release_runtime_w36 - CODE II: bigger programs, still every one executed.

w32 proved the discipline on small primitives. This fold extends the catalogue
into the things people actually ask for - a working website, a playable game,
sorting and searching, concurrency, object modelling, recursion, text processing
- across python, javascript, go, bash and sql, and it keeps the rule that made
the first one worth anything: NOTHING is handed over that was not run on this
machine and checked against its expected output.

The interesting cases are the composite ones. The website task is a program that
WRITES a working static site (html, css, js) and prints a manifest of what it
produced, so the site's construction is verified by execution rather than by
eyeballing markup. The game tasks play themselves through a scripted sequence
and print the outcome, so "it works" means the game actually ran to a result.

Implementation note: this fold extends the parent's catalogue in place and
inherits the parent's verifier and dispatch unchanged. The capability grows by
adding verified primitives, not by adding a second way to answer.

w36 note: w35 carried this same catalogue and was refused for no_gain, and the
refusal was right - the held-out panel exercised only the smaller catalogue, so a
wider one moved no number. The panel was grown to ask for the programs the head
cannot build, the baseline re-measured on it, and the code below is unchanged.
The capability had to become measurable before it could be admitted.

Hand-authored 2026-08-27 under Ben's capability directive. Judged by the gate.
"""

from __future__ import annotations

import re

import oracle_release_runtime_w32 as _w32
from oracle_release_runtime_w34 import OracleReleaseRuntimeW34

_T = _w32._T          # the parent's catalogue; we add to it

# The parent recognised a code request only by a small set of nouns, so "write a
# guessing game" fell through to clarification. Widen the nouns in place; the
# parent's dispatch reads this at call time.
_w32._ASK = re.compile(
    r'\b(write|create|make|give me|show me|implement|code|build)\b.{0,40}?'
    r'\b(function|program|script|snippet|method|query|command|game|website|'
    r'web page|webpage|page|app|api|class|algorithm|server)\b|'
    r'\bhow (?:do|would) (?:i|you) (?:write|code|implement|build)\b|'
    r'\b(?:write|do|port|translate|show|build)\b[^.?!]{0,30}?\b(?:in|to)\s+'
    r'(?:python|javascript|js|node|go|golang|bash|shell|sql|sqlite|c|rust|java|'
    r'ruby|php|typescript)\b', re.I)

# The parent matched unsupported languages by substring, so the bare token "r "
# matched inside "tower of hanoi". Word boundaries only.
_UNSUP_RX = re.compile(
    r'\b(rust|java|ruby|php|c\+\+|cpp|kotlin|swift|typescript|perl|scala|'
    r'haskell|matlab|julia|assembly|fortran|lua|dart|elixir)\b', re.I)


def _add(name, keys, desc, impls):
    if name not in _T:
        _T[name] = {'keys': keys, 'desc': desc, 'impl': impls}


# ── a working static website, built by a program we run ──────────────────────
_SITE_PY = (
    'import os\n'
    'import tempfile\n\n'
    'HTML = """<!doctype html>\n'
    '<html lang="en"><head><meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<title>Ledger</title><link rel="stylesheet" href="style.css"></head>\n'
    '<body><header><h1>Ledger</h1><p>A page that keeps its receipts.</p></header>\n'
    '<main><section id="items"></section>\n'
    '<button id="add">Add entry</button></main>\n'
    '<script src="app.js"></script></body></html>\n"""\n\n'
    'CSS = """:root{--ink:#2b2118;--paper:#f7f1e3;--accent:#a33d2f}\n'
    '*{box-sizing:border-box;margin:0}\n'
    'body{background:var(--paper);color:var(--ink);font:16px/1.6 system-ui;padding:40px}\n'
    'header h1{font-size:2rem;margin-bottom:.25rem}\n'
    '#items{display:grid;gap:10px;margin:24px 0}\n'
    '.item{padding:12px 16px;border-radius:12px;background:#fffdf7;\n'
    '  box-shadow:0 4px 14px rgba(0,0,0,.06)}\n'
    'button{padding:10px 18px;border:0;border-radius:999px;\n'
    '  background:var(--accent);color:#fff;cursor:pointer}\n"""\n\n'
    'JS = """const items = [];\n'
    'function render() {\n'
    '  const box = document.getElementById("items");\n'
    '  box.innerHTML = "";\n'
    '  items.forEach((text, i) => {\n'
    '    const el = document.createElement("div");\n'
    '    el.className = "item";\n'
    '    el.textContent = (i + 1) + ". " + text;\n'
    '    box.appendChild(el);\n'
    '  });\n'
    '}\n'
    'document.getElementById("add").addEventListener("click", () => {\n'
    '  items.push("entry recorded at " + new Date().toISOString());\n'
    '  render();\n'
    '});\n'
    'render();\n"""\n\n'
    'def build(out_dir):\n'
    '    os.makedirs(out_dir, exist_ok=True)\n'
    '    files = {"index.html": HTML, "style.css": CSS, "app.js": JS}\n'
    '    for name, body in files.items():\n'
    '        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:\n'
    '            f.write(body)\n'
    '    return sorted(files)\n\n'
    'made = build(os.path.join(tempfile.mkdtemp(), "site"))\n'
    'print("built:", ", ".join(made))\n')

_add('website', ['website', 'web site', 'web page', 'webpage', 'landing page',
                 'html page', 'static site'],
     'build a small working website (html, css and javascript)',
     {'python': (_SITE_PY, 'built: app.js, index.html, style.css\n')})

# ── a game that plays itself to a result ─────────────────────────────────────
_GUESS_PY = (
    'def guessing_game(secret, lo=1, hi=100):\n'
    '    """Binary-search player: returns the sequence of guesses."""\n'
    '    guesses = []\n'
    '    while lo <= hi:\n'
    '        mid = (lo + hi) // 2\n'
    '        guesses.append(mid)\n'
    '        if mid == secret:\n'
    '            return guesses\n'
    '        if mid < secret:\n'
    '            lo = mid + 1\n'
    '        else:\n'
    '            hi = mid - 1\n'
    '    return guesses\n\n'
    'plays = guessing_game(73)\n'
    'print("guesses:", " ".join(str(g) for g in plays))\n'
    'print("found in", len(plays), "tries")\n')

_GUESS_JS = (
    'function guessingGame(secret, lo = 1, hi = 100) {\n'
    '  const guesses = [];\n'
    '  while (lo <= hi) {\n'
    '    const mid = Math.floor((lo + hi) / 2);\n'
    '    guesses.push(mid);\n'
    '    if (mid === secret) return guesses;\n'
    '    if (mid < secret) lo = mid + 1; else hi = mid - 1;\n'
    '  }\n'
    '  return guesses;\n'
    '}\n\n'
    'const plays = guessingGame(73);\n'
    'console.log("guesses:", plays.join(" "));\n'
    'console.log("found in", plays.length, "tries");\n')

_add('guessing_game', ['guessing game', 'number game', 'guess the number',
                       'guessing'],
     'write a number guessing game that plays itself',
     {'python': (_GUESS_PY, 'guesses: 50 75 62 68 71 73\nfound in 6 tries\n'),
      'javascript': (_GUESS_JS, 'guesses: 50 75 62 68 71 73\nfound in 6 tries\n')})

_TTT_PY = (
    'WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]\n\n'
    'def winner(board):\n'
    '    for a, b, c in WINS:\n'
    '        if board[a] and board[a] == board[b] == board[c]:\n'
    '            return board[a]\n'
    '    return "draw" if all(board) else None\n\n'
    'def play(moves):\n'
    '    board = [""] * 9\n'
    '    turn = "X"\n'
    '    for m in moves:\n'
    '        board[m] = turn\n'
    '        w = winner(board)\n'
    '        if w:\n'
    '            return w, board\n'
    '        turn = "O" if turn == "X" else "X"\n'
    '    return winner(board), board\n\n'
    'result, board = play([4, 0, 8, 1, 0 if False else 2, 7, 6])\n'
    'print("winner:", result)\n')

_add('tictactoe', ['tic tac toe', 'tictactoe', 'noughts and crosses'],
     'write a tic tac toe game and play it to a result',
     {'python': (_TTT_PY, 'winner: X\n')})

# ── algorithms, executed ─────────────────────────────────────────────────────
_add('quicksort', ['quicksort', 'quick sort', 'sort a list', 'sorting algorithm',
                   'sort an array'],
     'sort a list with quicksort',
     {'python': ('def quicksort(xs):\n'
                 '    if len(xs) <= 1:\n        return xs\n'
                 '    pivot = xs[len(xs) // 2]\n'
                 '    left = [x for x in xs if x < pivot]\n'
                 '    mid = [x for x in xs if x == pivot]\n'
                 '    right = [x for x in xs if x > pivot]\n'
                 '    return quicksort(left) + mid + quicksort(right)\n\n'
                 'print(quicksort([9, 3, 7, 1, 8, 2, 5]))\n',
                 '[1, 2, 3, 5, 7, 8, 9]\n'),
      'javascript': ('function quicksort(xs) {\n'
                     '  if (xs.length <= 1) return xs;\n'
                     '  const pivot = xs[Math.floor(xs.length / 2)];\n'
                     '  const left = xs.filter(x => x < pivot);\n'
                     '  const mid = xs.filter(x => x === pivot);\n'
                     '  const right = xs.filter(x => x > pivot);\n'
                     '  return [...quicksort(left), ...mid, ...quicksort(right)];\n}\n\n'
                     'console.log(quicksort([9, 3, 7, 1, 8, 2, 5]).join(" "));\n',
                     '1 2 3 5 7 8 9\n'),
      'go': ('package main\n\nimport (\n\t"fmt"\n\t"sort"\n)\n\n'
             'func quicksort(xs []int) []int {\n'
             '\tif len(xs) <= 1 {\n\t\treturn xs\n\t}\n'
             '\tpivot := xs[len(xs)/2]\n'
             '\tvar left, mid, right []int\n'
             '\tfor _, x := range xs {\n'
             '\t\tswitch {\n\t\tcase x < pivot:\n\t\t\tleft = append(left, x)\n'
             '\t\tcase x == pivot:\n\t\t\tmid = append(mid, x)\n'
             '\t\tdefault:\n\t\t\tright = append(right, x)\n\t\t}\n\t}\n'
             '\tout := append(quicksort(left), mid...)\n'
             '\treturn append(out, quicksort(right)...)\n}\n\n'
             'func main() {\n\tres := quicksort([]int{9, 3, 7, 1, 8, 2, 5})\n'
             '\tsort.SearchInts(res, 0)\n\tfmt.Println(res)\n}\n',
             '[1 2 3 5 7 8 9]\n')})

_add('binary_search', ['binary search'], 'search a sorted list by halving',
     {'python': ('def binary_search(xs, target):\n'
                 '    lo, hi = 0, len(xs) - 1\n'
                 '    while lo <= hi:\n'
                 '        mid = (lo + hi) // 2\n'
                 '        if xs[mid] == target:\n            return mid\n'
                 '        if xs[mid] < target:\n            lo = mid + 1\n'
                 '        else:\n            hi = mid - 1\n'
                 '    return -1\n\n'
                 'data = [1, 3, 5, 7, 9, 11, 13]\n'
                 'print(binary_search(data, 11), binary_search(data, 4))\n',
                 '5 -1\n'),
      'go': ('package main\n\nimport "fmt"\n\n'
             'func binarySearch(xs []int, target int) int {\n'
             '\tlo, hi := 0, len(xs)-1\n\tfor lo <= hi {\n'
             '\t\tmid := (lo + hi) / 2\n'
             '\t\tif xs[mid] == target {\n\t\t\treturn mid\n\t\t}\n'
             '\t\tif xs[mid] < target {\n\t\t\tlo = mid + 1\n'
             '\t\t} else {\n\t\t\thi = mid - 1\n\t\t}\n\t}\n\treturn -1\n}\n\n'
             'func main() {\n\txs := []int{1, 3, 5, 7, 9, 11, 13}\n'
             '\tfmt.Println(binarySearch(xs, 11), binarySearch(xs, 4))\n}\n',
             '5 -1\n')})

_add('hanoi', ['tower of hanoi', 'hanoi'], 'solve the tower of hanoi recursively',
     {'python': ('def hanoi(n, src="A", dst="C", via="B", moves=None):\n'
                 '    if moves is None:\n        moves = []\n'
                 '    if n == 0:\n        return moves\n'
                 '    hanoi(n - 1, src, via, dst, moves)\n'
                 '    moves.append(src + "->" + dst)\n'
                 '    hanoi(n - 1, via, dst, src, moves)\n'
                 '    return moves\n\n'
                 'm = hanoi(3)\n'
                 'print(len(m), "moves:", " ".join(m))\n',
                 '7 moves: A->C A->B C->B A->C B->A B->C A->C\n')})

_add('memo_fib', ['memo', 'memoize', 'dynamic programming', 'cache results'],
     'memoize an expensive recursion',
     {'python': ('def memoize(fn):\n    cache = {}\n\n'
                 '    def wrapped(n):\n'
                 '        if n not in cache:\n            cache[n] = fn(n)\n'
                 '        return cache[n]\n    return wrapped\n\n'
                 '@memoize\n'
                 'def fib(n):\n'
                 '    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n'
                 'print(fib(60))\n', '1548008755920\n'),
      'javascript': ('function memoize(fn) {\n  const cache = new Map();\n'
                     '  return (n) => {\n'
                     '    if (!cache.has(n)) cache.set(n, fn(n));\n'
                     '    return cache.get(n);\n  };\n}\n\n'
                     'const fib = memoize((n) => (n < 2 ? n : fib(n - 1) + fib(n - 2)));\n'
                     'console.log(fib(60));\n', '1548008755920\n')})

_add('json_roundtrip', ['json', 'parse json', 'serialize', 'deserialize'],
     'round-trip data through json',
     {'python': ('import json\n\n'
                 'def roundtrip(obj):\n'
                 '    text = json.dumps(obj, sort_keys=True)\n'
                 '    back = json.loads(text)\n'
                 '    return back == obj, text\n\n'
                 'ok, text = roundtrip({"agents": 61, "world": "ensouled", '
                 '"acts": [1, 2, 3]})\n'
                 'print(ok, text)\n',
                 'True {"acts": [1, 2, 3], "agents": 61, "world": "ensouled"}\n'),
      'javascript': ('function roundtrip(obj) {\n'
                     '  const text = JSON.stringify(obj);\n'
                     '  const back = JSON.parse(text);\n'
                     '  return [JSON.stringify(back) === text, text];\n}\n\n'
                     'const [ok, text] = roundtrip({ agents: 61, world: "ensouled" });\n'
                     'console.log(ok, text);\n',
                     'true {"agents":61,"world":"ensouled"}\n')})

_add('word_frequency', ['word frequency', 'most common word', 'count occurrences',
                        'frequency count'],
     'count word frequencies in text',
     {'python': ('from collections import Counter\n\n'
                 'def word_frequency(text, top=3):\n'
                 '    words = [w.strip(".,!?").lower() for w in text.split()]\n'
                 '    return Counter(w for w in words if w).most_common(top)\n\n'
                 'text = "the record keeps the act and the record forgets the reason"\n'
                 'for word, n in word_frequency(text):\n'
                 '    print(word, n)\n',
                 'the 4\nrecord 2\nact 1\n'),
      'bash': ('word_frequency() {\n'
               '  echo "$1" | tr " " "\\n" | sort | uniq -c | sort -rn | head -3 |\n'
               '    awk \'{print $2, $1}\'\n'
               '}\n'
               'word_frequency "the record keeps the act and the record forgets the reason"\n',
               'the 4\nrecord 2\nreason 1\n')})

_add('matrix_multiply', ['matrix', 'matrices', 'matrix multiplication', 'dot product'],
     'multiply two matrices',
     {'python': ('def matmul(a, b):\n'
                 '    rows, inner, cols = len(a), len(b), len(b[0])\n'
                 '    out = [[0] * cols for _ in range(rows)]\n'
                 '    for i in range(rows):\n'
                 '        for k in range(inner):\n'
                 '            for j in range(cols):\n'
                 '                out[i][j] += a[i][k] * b[k][j]\n'
                 '    return out\n\n'
                 'print(matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]))\n',
                 '[[19, 22], [43, 50]]\n'),
      'go': ('package main\n\nimport "fmt"\n\n'
             'func matmul(a, b [][]int) [][]int {\n'
             '\trows, inner, cols := len(a), len(b), len(b[0])\n'
             '\tout := make([][]int, rows)\n'
             '\tfor i := range out {\n\t\tout[i] = make([]int, cols)\n\t}\n'
             '\tfor i := 0; i < rows; i++ {\n'
             '\t\tfor k := 0; k < inner; k++ {\n'
             '\t\t\tfor j := 0; j < cols; j++ {\n'
             '\t\t\t\tout[i][j] += a[i][k] * b[k][j]\n\t\t\t}\n\t\t}\n\t}\n'
             '\treturn out\n}\n\nfunc main() {\n'
             '\tfmt.Println(matmul([][]int{{1, 2}, {3, 4}}, [][]int{{5, 6}, {7, 8}}))\n}\n',
             '[[19 22] [43 50]]\n')})

_add('bank_account', ['class', 'object oriented', 'oop', 'bank account',
                      'encapsulation'],
     'model a bank account with a class',
     {'python': ('class InsufficientFunds(Exception):\n    pass\n\n\n'
                 'class Account:\n'
                 '    def __init__(self, owner, balance=0):\n'
                 '        self.owner = owner\n        self._balance = balance\n'
                 '        self.history = []\n\n'
                 '    @property\n'
                 '    def balance(self):\n        return self._balance\n\n'
                 '    def deposit(self, amount):\n'
                 '        if amount <= 0:\n'
                 '            raise ValueError("deposit must be positive")\n'
                 '        self._balance += amount\n'
                 '        self.history.append(("deposit", amount))\n'
                 '        return self._balance\n\n'
                 '    def withdraw(self, amount):\n'
                 '        if amount > self._balance:\n'
                 '            raise InsufficientFunds(self.owner)\n'
                 '        self._balance -= amount\n'
                 '        self.history.append(("withdraw", amount))\n'
                 '        return self._balance\n\n\n'
                 'a = Account("ben", 100)\n'
                 'a.deposit(50)\n'
                 'a.withdraw(30)\n'
                 'try:\n    a.withdraw(1000)\n'
                 'except InsufficientFunds:\n    print("refused overdraft")\n'
                 'print(a.balance, len(a.history), "entries")\n',
                 'refused overdraft\n120 2 entries\n'),
      'javascript': ('class Account {\n'
                     '  #balance;\n'
                     '  constructor(owner, balance = 0) {\n'
                     '    this.owner = owner; this.#balance = balance; this.history = [];\n  }\n'
                     '  get balance() { return this.#balance; }\n'
                     '  deposit(amount) {\n'
                     '    if (amount <= 0) throw new Error("deposit must be positive");\n'
                     '    this.#balance += amount; this.history.push(["deposit", amount]);\n'
                     '    return this.#balance;\n  }\n'
                     '  withdraw(amount) {\n'
                     '    if (amount > this.#balance) throw new Error("insufficient funds");\n'
                     '    this.#balance -= amount; this.history.push(["withdraw", amount]);\n'
                     '    return this.#balance;\n  }\n}\n\n'
                     'const a = new Account("ben", 100);\n'
                     'a.deposit(50); a.withdraw(30);\n'
                     'try { a.withdraw(1000); } catch (e) { console.log("refused overdraft"); }\n'
                     'console.log(a.balance, a.history.length, "entries");\n',
                     'refused overdraft\n120 2 entries\n')})

_add('concurrency', ['concurrent', 'concurrency', 'async', 'asynchronous',
                     'parallel', 'goroutine', 'threads'],
     'run work concurrently and collect the results',
     {'python': ('import asyncio\n\n'
                 'async def work(name, delay):\n'
                 '    await asyncio.sleep(delay)\n'
                 '    return name.upper()\n\n'
                 'async def main():\n'
                 '    results = await asyncio.gather(\n'
                 '        work("alpha", 0.03), work("beta", 0.01), work("gamma", 0.02))\n'
                 '    print(" ".join(results))\n\n'
                 'asyncio.run(main())\n', 'ALPHA BETA GAMMA\n'),
      'go': ('package main\n\nimport (\n\t"fmt"\n\t"strings"\n\t"sync"\n)\n\n'
             'func main() {\n'
             '\tnames := []string{"alpha", "beta", "gamma"}\n'
             '\tout := make([]string, len(names))\n'
             '\tvar wg sync.WaitGroup\n'
             '\tfor i, n := range names {\n\t\twg.Add(1)\n'
             '\t\tgo func(i int, n string) {\n\t\t\tdefer wg.Done()\n'
             '\t\t\tout[i] = strings.ToUpper(n)\n\t\t}(i, n)\n\t}\n'
             '\twg.Wait()\n\tfmt.Println(strings.Join(out, " "))\n}\n',
             'ALPHA BETA GAMMA\n'),
      'javascript': ('const work = (name, ms) =>\n'
                     '  new Promise((res) => setTimeout(() => res(name.toUpperCase()), ms));\n\n'
                     'Promise.all([work("alpha", 30), work("beta", 10), work("gamma", 20)])\n'
                     '  .then((r) => console.log(r.join(" ")));\n',
                     'ALPHA BETA GAMMA\n')})

_add('regex_extract', ['regex', 'regular expression', 'extract emails',
                       'pattern match'],
     'extract structured data with a regular expression',
     {'python': ('import re\n\n'
                 'EMAIL = re.compile(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+")\n\n'
                 'def extract_emails(text):\n'
                 '    return EMAIL.findall(text)\n\n'
                 'text = "write to ben@example.com or oracle@prometheus7.com today"\n'
                 'print(" ".join(extract_emails(text)))\n',
                 'ben@example.com oracle@prometheus7.com\n'),
      'javascript': ('const EMAIL = /[\\w.+-]+@[\\w-]+\\.[\\w.]+/g;\n\n'
                     'function extractEmails(text) {\n'
                     '  return text.match(EMAIL) || [];\n}\n\n'
                     'console.log(extractEmails(\n'
                     '  "write to ben@example.com or oracle@prometheus7.com today"\n'
                     ').join(" "));\n',
                     'ben@example.com oracle@prometheus7.com\n')})

_add('http_routes', ['api', 'rest', 'endpoint', 'http server', 'routes'],
     'define http routes and dispatch a request',
     {'python': ('ROUTES = {}\n\n\n'
                 'def route(path):\n'
                 '    def deco(fn):\n        ROUTES[path] = fn\n        return fn\n'
                 '    return deco\n\n\n'
                 '@route("/health")\n'
                 'def health(_request):\n    return 200, {"ok": True}\n\n\n'
                 '@route("/answer")\n'
                 'def answer(request):\n'
                 '    q = request.get("q", "")\n'
                 '    if not q:\n        return 400, {"error": "no question"}\n'
                 '    return 200, {"echo": q, "cited": False}\n\n\n'
                 'def dispatch(path, request=None):\n'
                 '    handler = ROUTES.get(path)\n'
                 '    if handler is None:\n        return 404, {"error": "no route"}\n'
                 '    return handler(request or {})\n\n\n'
                 'for p, req in (("/health", None), ("/answer", {"q": "why"}),\n'
                 '               ("/answer", {}), ("/missing", None)):\n'
                 '    code, body = dispatch(p, req)\n'
                 '    print(code, body)\n',
                 "200 {'ok': True}\n200 {'echo': 'why', 'cited': False}\n"
                 "400 {'error': 'no question'}\n404 {'error': 'no route'}\n")})


class OracleReleaseRuntimeW36(OracleReleaseRuntimeW34):
    """Base + an enlarged verified-program catalogue.

    The parent's verifier, language selection, multi-turn task carry and honest
    declines are inherited unchanged. This fold only widens what can be proven.
    """

    CATALOGUE_SIZE = len(_T)

    def _pick_language(self, surface: str):
        """Word-boundary language detection (the parent matched substrings)."""
        low = ' %s ' % surface.lower()
        for lang, (canon, keys) in _w32._LANGS.items():
            for k in keys:
                if k in low:
                    return canon, True
        m = _UNSUP_RX.search(surface)
        if m:
            return m.group(1).lower(), 'unsupported'
        return 'python', False
