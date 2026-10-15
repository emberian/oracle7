# Data licences: oracle7 (full)

The code is Apache-2.0 (`LICENSE`). The knowledge stores are compilations: every stored record keeps the source it came
from (each store's `manifest.json` / `corpus_inventory.json`, and every reply cites its record), and each record stays under
its source's licence. Attribution and ShareAlike apply to the stores and to anything you build from them.

**Non-commercial.** 68 of the 71 OpenStax books in this release are CC BY-NC-SA 4.0 (licence per book from OpenStax's
own catalogue, checked 2026-10-02; this supersedes the 'CC BY 4.0' label inside the store manifests, which was wrong).
The OpenStax records are mixed through the deep stores, so **the full release as a whole may be used only for
non-commercial purposes**, with attribution, and adaptations must be shared alike. For commercial use, use
**oracle7-slim**, which contains no OpenStax or other non-commercial material.

| Source | Licence | Attribution |
|---|---|---|
| Simple English Wikipedia (`m13e5_simplewiki*`, `m13e5_dbpedia_build_a_v2`) | CC BY-SA 4.0 | Wikipedia contributors |
| English Wikipedia text (`m13e7_wiki_openstax_full_fable_build_a_v1`, `m13e8_*`) | CC BY-SA 4.0 | Wikipedia contributors |
| DBpedia abstracts (`m13e7_dbpedia_*`, `m13e8_dbpedia_*`) | CC BY-SA 3.0 | DBpedia Association / Wikipedia contributors |
| OpenStax textbooks (inside the `m13e7`/`m13e8` stores, and `textbooks/textbook_store_v1.sqlite3`) | per book, table below: mostly CC BY-NC-SA 4.0 | OpenStax, Rice University |
| Wiktionary (`m13e5_wiktionary_build_a_v1`) | CC BY-SA 4.0 | Wiktionary contributors |
| ConceptNet 5 (`m13e5_conceptnet_build_a_v1`) | CC BY-SA 4.0 | ConceptNet / Luminoso and contributors |
| WordNet 3.0 (`m13a_wordnet_build_a_v4`, `m31_wordnet_corpus_v3`, `nltk_data/corpora/wordnet.zip`) | WordNet 3.0 licence (see WORDNET_LICENSE.txt) | Princeton University |
| Wikidata relations (`relstore/`) | CC0 1.0 | Wikidata contributors |
| Project Gutenberg texts (`textbooks/gutenberg/`) | Public domain (US); files keep the Project Gutenberg header | Project Gutenberg |
| Public-source compilations (`wander-train/oracle_relational_v3/data/m10`) | USGS public domain; CC0 1.0; World Bank dataset terms | USGS; World Bank; see source_manifest.json |
| Project-written material (admitted closure, explanatory 'Fable' articles inside the stores, specialist code and data) | CC BY-SA 4.0 (data) / Apache-2.0 (code) | Prometheus7 |

**Specialists.** Each specialist's card (`root/specialists/_cards/<id>.md`) lists its sources. Specialists ship facts,
formulas and small public tables (NASA planetary fact sheet: US government work; PubChem periodic table: public domain;
USDA nutrient data: public domain/CC0; Python documentation facts: PSF licence); where a card cites documentation under
another licence (git, Linux man-pages), only facts are used and no text is shipped. Where a card labels an OpenStax
book 'CC BY 4.0', the table below is authoritative; specialists use its formulas, not its text.

## OpenStax books in this release

| Book | Licence (OpenStax catalogue, 2026-10-02) | Where |
|---|---|---|
| Additive Manufacturing Essentials | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Algebra 1 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Algebra and Trigonometry 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| American Government 4e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Biology for AP® Courses | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Business Ethics | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Business Law I Essentials 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Calculus Volume 1 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Calculus Volume 2 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Calculus Volume 3 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Chemistry 2e | CC BY-NC-SA 4.0 | textbook store |
| Chemistry: Atoms First 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Clinical Nursing Skills | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| College Algebra 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| College Algebra 2e with Corequisite Support | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| College Algebra with Corequisite Support 2e | CC BY-NC-SA 4.0 | textbook store |
| College Physics 2e | CC BY-NC-SA 4.0 | textbook store |
| College Physics For AP® Courses 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| College Physics for AP® Courses 2e | CC BY-NC-SA 4.0 | textbook store |
| College Success | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| College Success Concise | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Concepts of Biology | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Contemporary Mathematics | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Elementary Algebra 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Entrepreneurship | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Foundations of Information Systems | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Fundamentals of Nursing | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Intermediate Algebra 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Introduction to Anthropology | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Behavioral Neuroscience | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Business 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Computer Science | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Intellectual Property | CC BY 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Philosophy | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Political Science | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Python Programming | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introduction to Sociology 3e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Introductory Business Statistics 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Introductory Statistics 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Lifespan Development | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Maternal-Newborn Nursing | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Medical-Surgical Nursing | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Microbiology | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Nutrition for Nurses | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Organic Chemistry: A Tenth Edition | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Organizational Behavior | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Pharmacology for Nurses | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Physics | CC BY 4.0 | knowledge stores (m13e7/m13e8) |
| Population Health for Nurses | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Prealgebra 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Precalculus 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Preparing for College Success | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Accounting, Volume 1: Financial Accounting | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Accounting, Volume 2: Managerial Accounting | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Data Science | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Economics 3e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Finance 2e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Macroeconomics 3e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Management | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Marketing | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Principles of Microeconomics 3e | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Psychiatric-Mental Health Nursing | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Statistics | CC BY 4.0 | knowledge stores (m13e7/m13e8) |
| U.S. History | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| University Physics Volume 1 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| University Physics Volume 2 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| University Physics Volume 3 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8), textbook store |
| Workplace Software and Skills | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| World History, Volume 1: to 1500 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| World History, Volume 2: from 1400 | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |
| Writing Guide with Handbook | CC BY-NC-SA 4.0 | knowledge stores (m13e7/m13e8) |

OpenStax content attribution: "Access for free at openstax.org". © Rice University. OpenStax is a registered
trademark of Rice University; this release is not endorsed by OpenStax or Rice University.

Benchmark datasets are **not** redistributed. No visitor, user or runtime data of any kind is included: the runtime
state directory ships empty, and the build scans every text file for keys, tokens and server addresses.
