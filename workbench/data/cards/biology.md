# Oracle7 Biology (molecular sequences) (#26, tier A)

**id** `biology` - organ `organ_biology_v1.BiologyOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 15/15 (false yes 0) vs head 1/15 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- OpenStax Biology 2e ch. 14-15 (DNA structure, transcription, translation, the genetic code) (CC-BY 4.0) https://openstax.org/details/books/biology-2e
- NCBI Genetic Codes - translation table 1 (the standard code) (public domain (US government)) https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi

## What it takes

- answers: codon, gc, revcomp, complement, transcribe, translate, protein_len
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Standard genetic code (NCBI table 1); translation from the first base, stops at the first stop codon (said so); never guesses a reading frame for a length not divisible by 3. The broader biology curriculum (MMLU biology) is not covered by this organ - v1 is the sequence core. Narrowed from the start (narrow_v1).
