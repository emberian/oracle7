# Oracle7 Robotics Basics (#97, tier B)

**id** `robotics-v2` - organ `organ_robotics_v2.RoboticsOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 20/23 (false yes 0) vs head 2/23 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Differential-drive kinematics, encoder odometry, planar forward kinematics - Wikibooks Robotics (CC-BY-SA 4.0 (store ships share-alike)) https://en.wikibooks.org/wiki/Robotics_Kinematics_and_Dynamics
- NASA robotics education (wheel speed from rpm, PWM average voltage) (public domain (US government)) https://www.nasa.gov/stem

## What it takes

- answers: wheel_speed, diff_linear, diff_angular, turn_radius, encoder, fk, pwm
- declines (in-domain): impossible, straight, underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

v2 of robotics (v1 NEGATIVE 2026-09-29: 3 head-fallthrough wrongs on 'X m/s (left)' phrasing). Parses differential drive itself (side labels in any position; track width only from a track phrase), recognise-then-decline, v1 declines kept for numeric turns. Fresh panel v2.
