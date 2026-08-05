# AI Start Map

## Product

AI Start Map is an AI-supported process diagnostic application for solo entrepreneurs and small businesses.

The application guides a user through one concrete business process, identifies the actual bottleneck and later produces grounded automation opportunities.

AI Start Map is a diagnostic and decision-support system. It does not autonomously execute company processes. The current approved visible journey is:

* landing page,
* free narration by voice or text,
* recognized process options and selection of one process,
* short current-process summary with a safe vertical HTML process line,
* confirmation or correction,
* zero to four relevant follow-up questions shown one at a time,
* visible analysis state,
* a concise result ordered as problem, first change, concrete AI support, weekly test and later automation,
* customer-facing print/PDF report, first-step plan and contact action.

Diagnose before recommending. Depending on the current digital maturity, the correct first step may be order and standardization, simple digitization, rule-based automation or AI support.

Do not invent product features, interview questions, business rules or user flows. Use only requirements explicitly approved in the current task or already implemented in the repository.

## Current technology

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy 2.x
* Alembic
* Pydantic
* Jinja2
* pytest

Do not introduce Flask, SQLite, Docker, frontend frameworks or additional production dependencies unless explicitly requested.

## Working rules

* Inspect the repository before changing files.
* Follow the current task exactly.
* Do not expand the requested scope.
* Do not modify unrelated files.
* Do not make product decisions independently.
* Do not add database tables or fields for possible future needs.
* Every database table, field and relationship must be required by current behavior.
* Prefer the smallest working implementation.
* Avoid unnecessary abstractions and architecture layers.
* Do not create repository, service or domain layers unless the current task requires them.
* Ask before making a destructive or major structural change.

## Database rules

* Use stable business keys where required.
* Use real foreign keys for relationships.
* Do not store important relationships only inside JSON.
* Use JSONB only for variable structured result data that is not independently queried or managed.
* Do not add fields such as `updated_at`, `is_active`, status fields or version fields unless the application currently uses them.
* Change the database schema through Alembic migrations.
* Do not create production tables with `Base.metadata.create_all()`.

## Code quality

* Use type hints.
* Use clear, descriptive names.
* Keep functions and modules small.
* Add or update tests for changed behavior.
* Run the relevant tests after implementation.
* Do not hide failed tests.
* Review the final diff for unnecessary code and files.

## User experience

* All customer-facing language is German.
* Avoid technical terminology in the interface.
* Show one clear step at a time.
* The user must understand what is being requested and what happens next.
* Do not add user-facing content that was not approved.
* Treat mobile as a primary viewport: stack cards, keep diagrams vertical, avoid horizontal tables and use touch targets of about 48--56 pixels.
* Voice input is an optional browser enhancement; editable text input must always remain available.
* Never show the internal numeric session ID in page content.
* Do not present uncertainty as an error or use invented percentages.
* Keep the interface warm and human, with clear contrast and the central green, cream, yellow, coral and blue design tokens.

## AI and knowledge rules

These rules apply only when AI or RAG is part of the current task:

* Do not treat retrieved examples as facts about the current user.
* Separate source evidence from professional analysis.
* Do not invent missing process information.
* Preserve uncertainty and contradictions.
* Use Structured Outputs when requested.
* Do not claim that an integration or API exists unless it has been verified.
* Visible output must distinguish confirmed user facts, professional inference, open uncertainty and future recommendation.
* `as_is_steps` contains only actual process actions, never metadata such as "unknown", missing-detail notices or recommendations.
* Generate visible process views only from validated structured process data. Use the vertical HTML/CSS process line for customer-facing screens and print.
* Retrieved material is diagnostic comparison knowledge only and must never leak source IDs, prompts, model names or other-company facts into customer output.

## Current implementation boundaries

* Keep the five existing tables: `sessions`, `interview_questions`, `process_options`, `analyses` and `automation_opportunities`.
* Prefer the existing JSONB result fields for variable structured presentation data that is not independently queried.
* Preserve working demo routes and the existing structured OpenAI/RAG architecture.
* Use browser `SpeechRecognition`/`webkitSpeechRecognition` for the first voice-input version and provide a safe unsupported-browser fallback.
* Use a readable vertical HTML/CSS process line; never render model-written diagram source directly.
* Use a customer-facing print view of normally three pages plus `window.print()` for PDF saving; do not add a heavy PDF dependency.
* Contact is a plain `mailto:` link. Do not imply that a browser attaches the report automatically.

## Diagnostic interview agent

* The bounded action set is `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE` and `STOP`.
* Demo heuristics live only in `app/agent_config.py`: prefer zero to two follow-ups, allow three only for genuinely complex cases, keep four as the technical visible maximum, and bound agent and tool rounds.
* These limits are project heuristics, not universal research findings, and must be calibrated with real AI Start Map interviews.
* Deterministic code must enforce budgets, no-repeat behavior, loop prevention, fact immutability and the prohibition on autonomous execution.
* Batch 04 agent patterns may support a decision, but semantic retrieval must never be the sole enforcement mechanism for a safety rule.
* Keep confirmed user facts, unconfirmed extraction, professional inference, RAG evidence, contradictions and uncertainty technically separate.
* The production knowledge architecture uses a diagnostic index and a separate optional agent-pattern index. Evaluation files are never indexable.

## Security

* Never commit `.env`, API keys, passwords or database credentials.
* Do not log full interview answers unnecessarily.
* Validate external input.
* Do not commit virtual environments, IDE files, caches or logs.

## Documentation

Before completing any relevant task, review the affected project documentation. At minimum, check `docs/PROJECT_STATE.md`, `docs/ROADMAP.md`, `docs/KNOWN_ISSUES.md`, `docs/DECISIONS.md`, `docs/CHANGELOG.md`, `docs/ARCHITECTURE.md`, `README.md`, `docs/INDEX.md` and the active feature specification.

* Implementation and documentation must not contradict each other.
* Do not present planned, decided, implemented, integrated and tested as the same status.
* Update the active feature spec when requirements, scope, design, tasks or acceptance criteria change.
* Update `docs/INDEX.md` when documents are added, moved, renamed, superseded, archived or reactivated.
* Search for stale references after structural or behavioral changes.
* Report which documentation files were reviewed, changed or did not require changes.

For the detailed workflow, follow `.agents/skills/documentation-update/SKILL.md`.

## Git

* Work in small, reviewable commits.
* Use short, precise imperative commit messages.
* Commit only related changes.
* Run tests before committing.
* Do not force-push or rewrite existing history.
* When the user requests publication, commit and push with Derya's authenticated GitHub identity. Never use Codex as author, committer or co-author.

## GitHub workflow

GitHub is the authoritative project history.

For every relevant, logically complete change:

1. update all affected documentation,
2. run the relevant tests or validation,
3. review the complete diff,
4. commit the related changes,
5. push the commit to the current feature branch.

Do not leave completed relevant work only in the local working tree.

Do not work directly on `main`. Do not merge to `main` without explicit review and approval. Do not force-push or rewrite history. Do not commit unrelated changes, secrets, IDE files, caches or logs.

Commits and pushes must use Derya's authenticated GitHub identity. Codex must never appear as author, committer or co-author.


## Completion

A task is complete only when:

* the requested behavior is implemented,
* relevant tests pass,
* migrations run successfully when the schema changed,
* the application starts,
* the final diff contains no unrelated changes,
* and the result is documented honestly.
