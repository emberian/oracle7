# Oracle7 Music Theory v2 (#74, tier B)

**id** `music-v2` - organ `organ_music_v2.MusicOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 64/64 (false yes 0) vs head 5/64 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Music theory (intervals, scales, key signatures, circle of fifths) - Wikibooks Music Theory (CC-BY-SA 4.0 (store ships share-alike)) https://en.wikibooks.org/wiki/Music_Theory
- 12-tone equal temperament f = 440 x 2^((m-69)/12) (ISO 16:1975 standard pitch A4 = 440 Hz); MIDI 1.0 note numbering (middle C = 60) (facts) https://www.iso.org/standard/3601.html

## What it takes

- answers: frequency, midi_number, midi_note, semitones, semitones_between, interval, key_sig, relative, scale, duration, cents
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

Supersedes: music (v1 NEGATIVE under gate v3: held-out 56/64 vs 2/64, 3 wrong > cap 1)

## Notes and known gaps

v2 = v1 + the tuning REFERENCE is never the target (v1 NEGATIVE under gate v3: 'Tuning to A4 = 432 Hz, what frequency is C5?' answered A4 = 432 Hz, 3 confident wrong - roles from grammar, never order of mention) + 'which minor key is relative to X' (5 safe misses) + 'frequency' in the decline context (v1 dev: the correct decline on 'frequency of C' was dropped). Judged under spec_gate_v3.1 on a FRESH panel v2 (seeds 747474/74747474; reference first AND last on both splits). Same author - disclosed.
