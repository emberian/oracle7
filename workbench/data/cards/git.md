# Oracle7 Version Control (git) (#58, tier B)

**id** `git` - organ `organ_git_v1.GitOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 7/10 (false yes 0) vs head 1/10 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- git reference documentation (git-scm.com) - commands and options (facts; no documentation text shipped) (GPL-2.0 documentation; facts used) https://git-scm.com/docs

## What it takes

- answers: git_cmd
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

A typed intent table; destructive commands (reset --hard, restore <file>) carry a WARNING in the answer; history-rewriting advice notes shared branches. Never runs a command. Tool-choice opinions are not taken. Narrowed from the start (narrow_v1).
