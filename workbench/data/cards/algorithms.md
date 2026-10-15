# Oracle7 Algorithms & Data Structures (#57, tier A)

**id** `algorithms` - organ `organ_algorithms_v1.AlgorithmsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 42/42 (false yes 0) vs head 1/42 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Standard algorithms (Dijkstra, Kruskal, binary search, comparison sort) executed on the user's own input; textbook complexity bounds (Cormen et al. / Wikibooks Algorithms, CC-BY-SA) in a small stated table (execution / CC-BY-SA (table facts)) https://en.wikibooks.org/wiki/Algorithms

## What it takes

- answers: shortest_path, unreachable, mst, disconnected, bsearch, not_found, sorted, complexity
- declines (in-domain): underspecified, no_node, negative, unsorted
- everything else falls through to the head unchanged

## Notes and known gaps

Answers by EXECUTION on the stated graph or list; the panel's expectations come from DIFFERENT algorithms (Floyd-Warshall, Prim, bisect). Binary search refuses an unsorted list; Dijkstra refuses negative weights. Requests to WRITE code are left to the head (full-core sweep caught one).
