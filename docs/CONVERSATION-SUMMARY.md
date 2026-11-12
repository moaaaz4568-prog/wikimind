# Conversation Summary — How wikimind Was Built

**Scope:** a sanitized summary of the working conversation of 11–12 November 2026
in which this repository was researched, designed, and built. No secrets are
recorded here: no token, key, password, or cookie value appears anywhere in
this file or in this repository. The GitHub access token used once during the
work is referred to only as "GitHub access token (value never recorded)".
Credential files from the source archive were excluded and never opened.

Evidence tags used below: OBSERVED (measured or read directly), REPORTED
(claimed in source material, not re-measured here), PROPOSED (a plan or
decision, not yet built), UNKNOWN (not established), NOT_RUN (never executed).

---

## 1. Timeline (11–12 November 2026)

### 11 November — Handoff and audit

- The work began with the public handoff repository
  `moaaaz4568-prog/layered-wiki-rag-handoff`, cloned and read in full:
  handoff documents, the complete 42-file project package, work reports, and
  the author's messages (106 messages in the old conversation, plus a 223-message
  conversation export).
- The private repository `moaaaz4568-prog/layered-wiki-rag` holds the original
  project; its v1.0.0 release ("WIKI_ARCHIVE_2026-11-03") was downloaded once
  with a GitHub access token (value never recorded). The release contains a
  single asset, `WIKI_ARCHIVE_2026-11-03.tar.gz` (60,072,453 bytes), whose
  SHA-256 matched the known fingerprint exactly; it was byte-identical to a
  copy already present in the handoff, so it added no new content. The token
  had been pasted in chat; the user was advised to rotate/delete it in
  GitHub Settings (Developer settings → Personal access tokens → Revoke),
  and to use secure entry for any future credential. Rotation status is
  UNKNOWN.
- The archive (`WIKI_ARCHIVE_2026-11-03.tar.gz`, 2,713 files) was extracted
  and searched directly. Finding [OBSERVED]: the 5,896 persona wiki pages
  are NOT in the archive — only pointer files (`.link.txt`) to paths on the
  original machine, not content. What IS present is business content:
  a compressed brain file holding exactly 39 masters, plus roughly 150
  concept files in the archive's sections 03 and 04. Conversation dumps and
  session logs in the archive are noise and were never indexed.
- Authorship audit [OBSERVED]: in the author's own messages, the user
  invented the goal, the master mechanism (extract → topic folders → main
  master + specialist masters), "no quarantine, show both sides", "no
  publishing, private", the RAG decision, and working via agents. Agents
  invented the governance/ops layer, the evaluation bureaucracy (Recall@k,
  known-answer set), the gates G0–G8, contradiction quarantine, the canon
  lifecycle, and the human-review gate. The rule "terms first, no master
  before its folder's terms complete" does not appear in any of the author's
  32 messages, despite being claimed as his words.

### 11 November — Goal clarification

- The user corrected the framing: the goal is to **build the system
  itself**, not to convert the wiki — a complete, ideal, integrated
  system. His stated vision: ask one question and the system draws on all
  the minds, determines the persona first, searches only that persona's
  library, answers in that persona's voice from its passages only, cites
  the raw passage, says "don't know" with no evidence, and shows both
  sides on contradiction.
- Ruling delivered and accepted as the working basis: keep the goal,
  hybrid RAG (RAG as base, wiki as a layer above it), the mandatory
  persona metadata filter, raw-passage citation, and structural chunking
  (heading/paragraph/table/list, no blind character splitting); drop the
  gates, canon lifecycle, quarantine, and evaluation bureaucracy as
  blockers — none of them ever produced a working system.

### 12 November — Masters: study, don't rebuild

- The user redirected: do not build the wiki and do not remake the
  masters. Study them, understand their structure and how they are made,
  and build a skill that makes masters like them.
- Master study [OBSERVED]: each of the 39 masters is 11 lines, sections
  1/4/16 only; §4 is truncated at 5,000 characters in 26/39; `[[Concept_...]]`
  links are 100% broken (95/95); no documented "make a master" step exists;
  there is no single main master in the material; the old template
  mismatches reality in 10 points; the masters predate the surviving
  concepts by about 2.5 months, so literal tracing is impossible.
- The make-master skill was built at `docs/skills/make-master/` (SKILL.md
  plus structure spec, template, quality checklist, and study). Its
  verification coverage is 16/22 full, 6 partial, 0 missing, after 14
  corrections. It is a prerequisite for the wiki layer in this system:
  links in any new master must point to real paths (checked before
  writing) or be dropped; broken `[[Concept_...]]` links are forbidden.

### 12 November — A general system, not a one-off

- The user widened the scope: build a **complete general wiki system as
  a GitHub repository anyone can use** — a person with files downloads the
  repo and uses it on their own files, at any time, to turn them into a
  "mind" and extract knowledge. Research first (what was done, the files,
  existing tools and approaches), then design and build. The master study
  and the make-master skill are phase 1 and a component of the repo.
- A second research repository was assigned and studied:
  `moaaaz4568-prog/wiki-rag-youtube-research` (public, 13 files, 1 commit,
  144-video YouTube research). Full report: `docs/youtube-research/STUDY-REPORT.md`.
- The general repo was built fresh locally in this directory. It was
  never pushed during the conversation; the push decision (public repo)
  was made by the user at the end of the work.

---

## 2. Decisions

| # | Decision | Status |
|---|----------|--------|
| 1 | Build the system itself (not just convert the wiki) | Implemented — this repo |
| 2 | Hybrid: RAG is the base, wiki is a layer above it | Implemented (BM25 retrieval + masters layer) |
| 3 | Persona / dataset is a mandatory metadata filter, not a similarity hint | Implemented in `src/wikimind/ask.py` |
| 4 | Every answer cited to the raw passage; say "don't know" with no evidence; show both sides on contradiction, no quarantine | Implemented in `ask.py` |
| 5 | Masters: study them; build a master-making skill; never remake the 39 masters | Implemented — `docs/skills/make-master/` |
| 6 | General public repo: anyone can clone it and run it on their own files | Implemented — this repo |
| 7 | Research first (handoff, archive, YouTube research repo, existing tools) before designing | Done — `docs/study/`, `docs/youtube-research/` |
| 8 | Push this repo to GitHub as public | Approved by the user; first commit prepared locally |
| 9 | The GitHub access token used during the work should be rotated/deleted by the user | Pending user action (UNKNOWN) |
| 10 | Privacy of the original private wiki (personas, 5,896 pages) | Not in this repo; unchanged — private material was never copied here |

---

## 3. What the research repos found (all opinions)

### YouTube research (`docs/youtube-research/STUDY-REPORT.md`)

- 144 videos analyzed (6 queries × 30 results → 144 unique). Transcripts
  fetched 144/144 via yt-dlp with a cookies file — the only proven route;
  without cookies the transcript API failed with LOGIN_REQUIRED and an
  earlier download script died with 429/403.
- Dominant opinion [REPORTED from the analysis]: Obsidian + Claude as a
  "second brain" (Obsidian in 72/144 videos, Claude in 88/144) — plain
  Markdown files any model can read, maintained in Git. Published
  criticism of Karpathy's LLM-Wiki also appears ("Karpathy's LLM-Wiki is
  Bad", "doesn't work for teams", "The AI Second Brain Lie").
- RAG appears in 99 videos; GraphRAG by name in 2 only; hybrid retrieval
  in 9. Knowledge graphs are a later step, for relational questions only.
- BM25 numbers are consistent across sources [REPORTED]: 12/15 rank-1 and
  14/15 top-3 on the 210-page Haitham corpus; paraphrased questions only
  1/3. The texts of the 15 questions themselves were never saved, so they
  are UNKNOWN and the totals cannot be re-derived.

### Phase-2 research (`docs/study/phase2-research.md`)

- Recommendation adopted: stdlib-only Python first, BM25 first; dense
  embedding only later, with a small ONNX model, measured on the missed
  paraphrase questions; never repeat Cognee / RAGFlow / GraphRAG, the
  claim/quarantine/gates bureaucracy, or YouTube without cookies.
- A local embedding model of 1–2 GB is not guaranteed to load here: only
  about 435–610 MB of RAM was free at measurement time (8 GB total).

---

## 4. Results and measurements (this repo, sample corpus)

All measurements below are OBSERVED — re-run from the sample corpus in
`examples/sample-corpus/` (20 files, 60,964 bytes) with the 20 questions in
`examples/eval-questions.json` (6 title + 7 paragraph + 7 paraphrase).

| Measurement | Value |
|---|---|
| Unit tests | 18/18 passing |
| Build: files → chunks | 20 files → 151 chunks |
| Terms / concepts | 2,023 terms, 134 concepts |
| Masters built | 4 (Content 3, General 3, Outbound 9, Sales 5) |
| Master links verified / dropped | 40 verified, 0 dropped |
| Eval rank-1 | 14/20 (0.700) |
| Eval top-3 | 15/20 (0.750) |
| Eval by type | titles 6/6, paragraphs 7/7, paraphrases 1/7 rank-1, 2/7 top-3 |
| Ask: literal title query | correct passage, score 18.886, ~5 ms |
| Ask: no-evidence query | "don't know — no evidence" (best score = 0) |
| Ask: contradiction query | both sides shown, "no quarantine" |
| Secrets in repo | none found (final grep scan; see §6) |

The only measured gap is paraphrase (1/7 rank-1). The planned fix is a
small dense ONNX model plus rerank, measured on the 5 missed paraphrases;
that work is NOT_RUN. Also NOT_RUN: dense embedding + rerank, the graph
layer, a glm chat interface, systematic latency/memory measurement, the OKF
package shape on Arabic content, and the repo on a random user's files.

---

## 5. Files and sources

- **This repo** — `src/wikimind/` (10 stdlib-only modules:
  tokenize, ingest, chunk, index, terms, masters, ask, eval, cli,
  `__main__`), `docs/` (README, QUICKSTART, DESIGN, EVAL, MEASUREMENTS,
  THRESHOLDS, CONTRADICTIONS, YOUTUBE), `docs/skills/make-master/`
  (the make-master skill), `examples/` (20-file sample corpus + 20 eval
  questions), `tests/` (18 unit tests).
- **Master study** — `docs/study/`: `anatomy.md`, `process.md`,
  `raw-material.md`, `variance-qa.md`, `verification.md`,
  `phase2-research.md`. Source material: the 39-master compressed brain
  file and the concept files from the archive listed in §1. The 5,896
  persona pages were never present and are not in this repo.
- **YouTube research** — `docs/youtube-research/STUDY-REPORT.md`. Source:
  public repo `moaaaz4568-prog/wiki-rag-youtube-research` (144-video
  research; transcripts are not included, by design, as they belong to
  their owners).
- **Handoff** — public repo `moaaaz4568-prog/layered-wiki-rag-handoff`
  (handoff documents, full 42-file project package, work reports, message
  archive). The original private repo is `moaaaz4568-prog/layered-wiki-rag`;
  its v1.0.0 release archive was verified byte-identical to the copy in
  the handoff and contains no persona pages.
- **What is deliberately NOT here:** the 5,896 persona wiki pages; any
  credential or cookie file (excluded, never opened, never indexed, never
  uploaded); any token, key, password, or cookie value; raw chat
  transcripts or conversation dumps.

---

## 6. Security notes

- This repository was scanned for secret patterns (`ghp_`, `gho_`,
  `sk-`, `BEGIN ... PRIVATE KEY`, `AKIA`) before its first commit: no
  real secret values found.
- `docs/YOUTUBE.md` mentions the string `COOKIES_TEXT` only as text
  warning against a bad practice (embedding cookie text inside code).
  It is not a secret and no cookie value is present.
- If you run this system on your own files, keep credentials (API keys,
  cookie files) outside the indexed corpus and outside any repository —
  in environment variables or a secure vault, never pasted in chat and
  never committed.
