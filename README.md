# JavaTrail

A personal learning platform: an interactive roadmap (React Flow) that opens structured,
visually explained topic pages built from your own material.

```bash
npm install
npm run dev      # http://localhost:5173
npm test         # roadmap graph, layout and progress logic
npm run build
```

## Architecture

```
content/                    YOUR data (roadmap + topic JSON). No UI code. See content/README.md
src/
  lib/                      framework-free logic, unit-tested
    roadmap/                model.js (validate + index), layout.js (auto layout), colors.js
    progress/               state.js (pure updates + stats), storage.js (repository), status.js
    content/                registry.js (finds content files), normalize.js, highlight.js, mermaid.js
  features/
    progress/               ProgressProvider (state + persistence)
    roadmap/                RoadmapScope (per-roadmap context), canvas, nodes, page
    dashboard/              dashboard page
    topic/                  topic page (TOC, subtopics, pager)
    content/                ContentRenderer, block registry, block components
  components/               layout + small UI pieces
```

Key decisions

- **Data is separate from UI.** `lib/content/registry.js` is the only file that knows where content lives.
- **Progress storage is a repository.** `createLocalStorageRepository` implements
  `load / save / subscribe`; replace it in `src/main.jsx` with a database-backed one later.
  Progress is keyed by roadmap id and topic id, and stale entries are ignored, so roadmap edits are safe.
- **Roadmap layout is computed** from dependencies (layered, top to bottom), or taken from `position`.
- **Heavy libraries load on demand:** Mermaid and highlight.js are dynamic imports; topic pages are code-split.
- Dark theme only for now; colours are tokens in `src/index.css` (`@theme`), so a light theme can be added.

## Turning your PDFs into content (`tools/`, Python)

```bash
pip install pdfplumber pypdf
python -I tools/build_roadmap.py <folder>                      # roadmap.json from the plan + PDF bookmarks
python -I tools/extract_topic.py <folder> <roadmap.json> --doc <Guide.pdf> <topics dir> [--force]
python -I tools/build_plan_topics.py <folder>                  # pages for the plan-only days
python -I tools/build_frontend_topics.py                       # pages for the frontend stage (not from a PDF)
```

The order of the learning path lives in `tools/learning_path.json`.

The extractor keeps code (with indentation), tables, callouts and check-yourself questions, and carries each
figure over as a dark-themed SVG redrawn from the PDF's own vector drawing (a few figures without a drawing
stay as labelled placeholders). `--force` overwrites existing topic files, including any hand edits.

`python -I tools/spotcheck.py <folder> <topic-id-prefix> --min-run 25` compares converted topics with the PDF text
and lists runs of words that were dropped or added (chapter boundaries and tables read in a different order show up
as noise; long mid-chapter runs are the ones worth a look).

## Status semantics

Topic status is stored explicitly. Setting a topic to Completed/Not started applies to all its
subtopics; changing subtopics moves the topic along (all done → Completed, any progress → In progress).
Overall and per-category percentages are completed topics / total topics.
