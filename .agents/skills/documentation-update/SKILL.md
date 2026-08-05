---
name: documentation-update
description: Keep AI Start Map project documentation consistent with verified repository behavior. Use after relevant implementations, architecture or product decisions, confirmed bugs and fixes, changes to RAG, agents, data models, user flows, outputs or deployment, and whenever documents are created, moved, superseded, archived or reactivated.
---

# Documentation Update

Maintain one verified Source of Truth per concern. Never equate a plan or decision with working, integrated and tested behavior.

## Read first

Read completely before editing:

1. `AGENTS.md`
2. `README.md`
3. `docs/INDEX.md`
4. `docs/PROJECT_STATE.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DECISIONS.md`
7. `docs/KNOWN_ISSUES.md`
8. the active feature specification
9. the actual Git diff

Read affected flow, product, deployment or archive documents when the change touches them.

## Use status terms strictly

- `decided`: fachlich oder technisch beschlossen.
- `implemented`: im Code vorhanden.
- `integrated`: im echten Laufzeitpfad aktiv.
- `tested`: nachvollziehbar geprüft.
- `documented`: in den Projektdateien beschrieben.
- `planned`: noch nicht umgesetzt.

Never use these terms as synonyms. State unknown or unverified status explicitly.

## Workflow

1. Inspect the actual diff and current code.
2. Identify changed behavior and unaffected boundaries.
3. Determine every affected document through `docs/INDEX.md`.
4. Search repository-wide for contradictory or stale statements and old paths.
5. Update `docs/KNOWN_ISSUES.md`; keep partial or unresolved problems visible.
6. Add only verified changes to `docs/CHANGELOG.md`.
7. Update `docs/PROJECT_STATE.md` only when the confirmed current state changed.
8. Update `docs/ARCHITECTURE.md` when components, data flows, integrations or boundaries changed.
9. Update `docs/DECISIONS.md` when a decision was added, changed, superseded or rejected.
10. Update `docs/ROADMAP.md` only when priority or status changed.
11. Update the active feature spec when requirements, scope, design, tasks or acceptance criteria changed.
12. Update `docs/INDEX.md` for every added, moved, renamed, superseded, archived or reactivated document.
13. Mark stale documents `Superseded` or `Archived`; do not silently abandon them.
14. Reference tests, validation or other evidence used.
15. Review the complete documentation diff before commit.

## Issue closure

Remove an issue only after the fix is implemented or fachlich resolved, a fitting test or validation succeeds, and the verified change appears in `docs/CHANGELOG.md`. Otherwise retain it with `Open`, `Investigating`, `In Progress`, `Partially Fixed`, `Blocked` or `Verified Fixed`.

## Document lifecycle

- Keep an active document only when it was checked against current code or confirmed product state.
- Archive rather than delete when historical context, decisions or traceability remain useful.
- Reactivate an archived document only after review, status update, conflict resolution and `docs/INDEX.md` update.
- Preserve research and provenance artifacts at stable paths when runtime allow-lists, tests or source references depend on them.

## Validate

Run at minimum:

- `git status --short --branch`
- complete diff review
- stale path/name search
- orphaned Markdown link check
- `git diff --check`
- relevant tests or repository documentation checks

Do not install a new linter only for documentation. Do not run external APIs or build embeddings for a documentation-only task.

## Completion report

Always report each relevant document as `updated`, `reviewed — no change required`, or `not applicable`, with a short reason. Include at least:

- `docs/PROJECT_STATE.md`
- `docs/ROADMAP.md`
- `docs/KNOWN_ISSUES.md`
- `docs/DECISIONS.md`
- `docs/CHANGELOG.md`
- `docs/ARCHITECTURE.md`
- `README.md`
- active feature spec
- `docs/INDEX.md`
- stale references searched: yes/no

Also report validation, commit and push status when the task includes publication.
