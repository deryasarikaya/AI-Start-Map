# AI Start Map

## Product

AI Start Map is an AI-supported process diagnostic application for solo entrepreneurs and small businesses.

The application guides a user through one concrete business process, identifies the actual bottleneck and later produces grounded automation opportunities.

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

## AI and knowledge rules

These rules apply only when AI or RAG is part of the current task:

* Do not treat retrieved examples as facts about the current user.
* Separate source evidence from professional analysis.
* Do not invent missing process information.
* Preserve uncertainty and contradictions.
* Use Structured Outputs when requested.
* Do not claim that an integration or API exists unless it has been verified.

## Security

* Never commit `.env`, API keys, passwords or database credentials.
* Do not log full interview answers unnecessarily.
* Validate external input.
* Do not commit virtual environments, IDE files, caches or logs.

## Git

* Work in small, reviewable commits.
* Use short, precise imperative commit messages.
* Commit only related changes.
* Run tests before committing.
* Do not force-push or rewrite existing history.


## Completion

A task is complete only when:

* the requested behavior is implemented,
* relevant tests pass,
* migrations run successfully when the schema changed,
* the application starts,
* the final diff contains no unrelated changes,
* and the result is documented honestly.
