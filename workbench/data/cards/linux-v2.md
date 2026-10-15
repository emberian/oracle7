# Oracle7 Linux & the Command Line v2 (#54, tier B)

**id** `linux-v2` - organ `organ_linux_v2.LinuxOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 42/42 (false yes 0) vs head 3/42 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Linux man-pages: chmod(1), umask(2), crontab(5), signal(7) (x86/ARM numbering) (man-pages licences (verbatim / GPL; facts used, text not shipped)) https://man7.org/linux/man-pages/man7/signal.7.html
- POSIX shell: exit status of a command terminated by a signal is greater than 128 (bash: 128 + n) (facts) https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html

## What it takes

- answers: chmod_symbolic, chmod_octal, umask, umask_file, umask_dir, cron_per_hour, cron_per_day, signal_number, signal_name, exit_status
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

Supersedes: linux (v1 NEGATIVE under gate v3: held-out 37/42, 2 wrong from head fallthrough)

## Notes and known gaps

v2 = v1 + 'in one day / in 24 hours / every day' read as per day, 'signal has the number N' read as signal N, and a RECOGNISED cron run-count question with no readable period DECLINES in-domain instead of falling silent. v1 NEGATIVE under gate v3: held-out 37/42 vs 2/42 but 2 WRONG - the wrong answers were the HEAD's (-3.83, -10) on 'In one day, how many runs...' turns the organ fell silent on. Corollary of the numbers-rule law: recognise-then-decline, never silence into a weak head. Judged under spec_gate_v3.1 on a FRESH panel v2 (seeds 545454/54545454). Same author - disclosed.
