# AI Start Map V2 — TODO

_Last updated: 2026-07-22_

## 1. Product goal

AI Start Map is an AI-supported diagnostic system for solo self-employed people, microbusinesses and small businesses.

The app should:

1. let the user describe an operational problem naturally by voice or text,
2. identify concrete business processes in that description,
3. focus on one process,
4. reconstruct the current workflow,
5. show the understood workflow visually,
6. ask only relevant follow-up questions,
7. identify the real bottleneck,
8. determine whether order, standardization, digitization, automation or AI support is the right next step,
9. provide three realistic, explainable starting points,
10. give the user a practical first-step plan and a downloadable report.

AI Start Map remains a diagnostic and decision-support system. It does not autonomously execute company processes.

---

# 2. Core product principles

- Diagnose before recommending.
- Understand the current process before suggesting software.
- The user should be able to narrate instead of completing a long form.
- The user should never feel that they are working for the app.
- The app must work for analog, low-digital-maturity and smartphone-only businesses.
- A correct recommendation may be physical order or standardization before digitization.
- RAG evidence is comparison and diagnostic knowledge, never a fact about the current user.
- Separate facts, inferences, uncertainties and recommendations.
- Preserve human approval for prices, contracts, payments, quality decisions and exceptions.
- Prefer the smallest realistic improvement over a complex transformation.
- No autonomous execution.

---

# 3. Current technical baseline

- FastAPI
- Jinja2
- HTML
- CSS
- JavaScript
- PostgreSQL
- SQLAlchemy
- Alembic
- OpenAI API
- Structured Outputs
- FAISS-based RAG
- automated tests
- demo cases
- five existing database tables:
  - `sessions`
  - `interview_questions`
  - `process_options`
  - `analyses`
  - `automation_opportunities`

The current architecture should be extended, not replaced.

Do not migrate to React, Next.js or Lovable for the current phase.

---

# 4. Current RAG status

## Existing corpus

- 111 curated chunks
- 25 separate evaluation cases
- production diagnostic index: 634 chunks
- separate production agent-pattern index: 205 patterns
- previous 111-chunk index preserved as backup

## Batch 02 — analog reality

- 35 documented cases
- 162 separate RAG chunks
- source register
- quality and merge gate
- 162 RAG chunks integrated through the explicit diagnostic-index allow-list

## Batch 03 — diagnostic depth

- 46 new company cases
- 361 separate RAG chunks
- 49 generalized patterns
- 12 German/EU guardrails
- 14 separate evaluation cases
- 20 physical-intake cases
- 22 repair/workshop cases
- 15 field-service cases
- 19 custom-production or small-production cases
- 361 RAG chunks integrated through the explicit diagnostic-index allow-list
- Interview-Agent knowledge intentionally excluded

## Batch 04 — agentic interview

- 60 agent-decision patterns
- 40 next-question patterns
- 25 clarification/contradiction patterns
- 25 stop rules
- 25 tool-selection patterns
- 30 agent guardrails
- 40 separate `NEVER_INDEX` evaluation cases
- 205 optional patterns in a separate production index
- deterministic safety and budget rules implemented in code
- state model kept separate from the five-table persistence model; no migration required

---

# 5. Current main priority

## Complete visible user journey

The entire UI and UX flow has now been conceptually defined.

The next implementation must cover the full journey, not isolated pages.

Target flow:

```text
Landing page
→ free narration by voice or text
→ recognized process options
→ select one process
→ structured process summary
→ Mermaid visualization
→ user confirms or corrects
→ dynamic follow-up questions
→ visible loading state
→ result
→ PDF export
→ first-step plan
→ another process or contact CTA
```

---

# 6. Landing page

## Goal

Immediately reach a stressed self-employed person or small-business owner who:

- feels overwhelmed,
- knows something could be easier,
- has heard that AI may help,
- does not know where to start,
- fears breaking a process that currently works somehow,
- does not want another complicated tool or questionnaire.

## Required hero content

Headline:

> Was läuft in deinem Betrieb immer wieder unnötig kompliziert?

Subheadline:

> Erzähl uns, was dich im Alltag aufhält, nervt oder durcheinanderbringt. AI Start Map erkennt den Ablauf dahinter, zeigt dir den größten Engpass und schlägt drei realistische nächste Schritte vor.

Primary CTA:

> Jetzt einfach erzählen

Supporting text:

> Per Sprache oder Text · keine Vorbereitung nötig

Trust message:

> Du musst deinen Betrieb nicht komplett verändern. Wir finden zuerst den Schritt, der wirklich zu deinem Alltag passt.

## Required sections

- chaos-to-clarity visual
- “Kommt dir das bekannt vor?”
- multiple communication channels
- information on paper, phone and in people's heads
- owner as the central information hub
- uncertainty about where to start with AI
- psychological relief section
- how AI Start Map works in three steps
- difference from a general chatbot
- examples from shoe repair, hairdressing, trades and coaching
- trust and control
- final CTA

---

# 7. Design system

## Colors

```css
:root {
  --green-dark: #2F4A3A;
  --green-main: #6C8870;
  --green-light: #DDE7DE;

  --cream: #F7F3EA;
  --beige: #EFE8DC;
  --surface: #FFFEFB;

  --text-main: #28322C;
  --text-secondary: #657068;
  --text-muted: #8A928C;

  --accent-warning: #D3A34A;
  --accent-problem: #C97961;
  --accent-info: #7895A3;

  --border: #D9DDD7;
}
```

## Style

- warm
- calm
- human
- trustworthy
- modern
- visually clear
- not technical or cold
- no robot imagery
- no neon startup aesthetic
- no heavy enterprise dashboard
- large touch targets
- rounded cards
- generous whitespace
- simple process visuals
- subtle animation

## Typography

Preferred:

- headings: Lora or suitable serif fallback
- body and UI: Inter or `system-ui`

---

# 8. Mobile-first requirements

Mobile is not a reduced afterthought. It is a primary use case.

Required:

- cards stacked vertically
- no horizontal tables
- no horizontal process diagram on narrow screens
- Mermaid flowcharts vertical
- buttons approximately 48–56 px high
- large microphone button
- editable transcript immediately visible
- no tiny icon-only controls
- no two cramped columns
- keyboard must not hide the next action
- readable on Android and iPhone browsers
- no horizontal page scrolling

---

# 9. Voice and text input

Voice is a core feature.

## First implementation

Use browser-based speech recognition when supported.

Requirements:

- German as default
- live or near-live transcript
- transcript always editable
- text input always available
- unsupported browser must fail gracefully
- clear microphone-permission guidance
- same voice control usable for:
  - initial description
  - corrections
  - dynamic follow-up answers

## Visible states

```text
idle
recording
processing
done
error
```

Required labels:

- Aufnahme starten
- Ich höre zu …
- Aufnahme beenden
- Wir bringen deine Erzählung gerade in Text.
- Das haben wir verstanden.
- Noch einmal versuchen
- Lieber schreiben

## Later extension

Prepare the frontend structure so a future `MediaRecorder` + backend transcription pipeline can be added without rebuilding the user journey.

Do not add ElevenLabs or Whisper automatically in the current implementation unless explicitly approved and configured.

---

# 10. Process selection

Required headline:

> Welchen Ablauf sollen wir zuerst genauer ansehen?

Required explanation:

> Aus deiner Erzählung haben wir diese Abläufe erkannt. Wähle den aus, der dich gerade am meisten Zeit oder Nerven kostet.

Supporting sentence:

> Wir schauen uns zuerst einen Ablauf genauer an, damit das Ergebnis konkret bleibt.

Each card must include:

- plain-language process name
- start
- end
- why it was recognized
- CTA: `Diesen Ablauf ansehen`

Alternative:

> Nichts Passendes dabei?

CTA:

> Einen anderen Ablauf beschreiben

The user must never need to know or type a session ID.

---

# 11. Understood-process summary

Required headline:

> So haben wir deinen Ablauf verstanden

Required explanation:

> Schau kurz drüber. Du kannst alles ändern oder ergänzen, bevor wir weitermachen.

Show:

- plain-language process title
- start and end
- actual process steps
- confirmed user facts
- observed difficult points
- open questions
- no final recommendation yet

## Mermaid

Use Mermaid on this screen as the trust and understanding moment.

Rules:

- generate Mermaid from validated structured process data
- never render uncontrolled LLM-generated Mermaid directly
- sanitize labels
- no raw HTML from user input
- use secure Mermaid configuration
- use `flowchart TD`
- keep labels short
- mobile must be vertical
- provide a simple list fallback if rendering fails

## Editing

Allow:

- edit process title
- edit a step
- add a step
- free correction by voice
- free correction by text

Confirmation:

- `Ja, so läuft es`
- `Etwas ändern`

Do not show final opportunities on this screen.

---

# 12. Dynamic follow-up questions

Replace the visible fixed questionnaire with dynamic, process-specific follow-ups.

Rules:

- one question at a time
- normally two to three
- maximum four
- never repeat an answered question
- do not ask generic questions when a specific question is possible
- ask only when the answer could change the diagnosis or recommendation
- one topic per question
- no solution-leading questions
- simple language
- answer by voice or text
- allow `Weiß ich gerade nicht`
- skipped information remains an uncertainty
- contradictions must be clarified explicitly
- do not invent missing answers

Required heading:

> Eine Sache möchten wir noch verstehen

Show a short reason:

> Das hilft uns zu erkennen, …

Progress orientation:

```text
Erzählt ✓
Ablauf verstanden ✓
Details klären ●
Ergebnis ○
```

Do not display `Frage 2 von 7`.

---

# 13. Loading and error states

Required headline:

> Wir bringen deinen Ablauf gerade in ein klares Bild

Required explanation:

> Das dauert einen kurzen Moment. Wir prüfen, wo es heute hakt und welcher nächste Schritt wirklich zu deinem Betrieb passt.

Visible phases:

```text
✓ Deine Angaben wurden übernommen
✓ Dein Ablauf wird geordnet
● Schwierige Stellen werden geprüft
○ Passende nächste Schritte werden ausgewählt
○ Dein Ergebnis wird vorbereitet
```

Requirements:

- show immediately
- prevent double submission
- no fake percentages
- no technical terms such as RAG, LLM, tool call or embeddings
- quiet chaos-to-clarity animation
- preserve user data if analysis fails

Error copy:

> Das hat gerade nicht geklappt.

> Deine Angaben sind gespeichert. Du musst nichts noch einmal erzählen.

Actions:

- `Noch einmal versuchen`
- `Angaben bearbeiten`

---

# 14. Result page

The result must be short, visual and useful.

Required order:

1. result heading
2. biggest bottleneck
3. best first step
4. mini test
5. current process
6. next realistic target process
7. two additional options
8. prerequisites and open points
9. PDF and next actions

## Result heading

> Jetzt ist klar, wo du am sinnvollsten anfangen kannst

## Bottleneck

Separate:

- visible symptom
- root cause
- operational effect

## First recommendation

Heading:

> Damit solltest du anfangen

Category must be one of:

- Ordnung und Standardisierung
- einfache Digitalisierung
- regelbasierte Automatisierung
- KI-Unterstützung

Explain:

- why it fits now
- prerequisites
- smallest practical test
- what still requires a human decision

## Current and target process

- current process: confirmed Mermaid
- target process: only the next realistic maturity step
- no unrealistic full automation
- highlight bottleneck, waiting, missing information and human decisions

## Additional opportunities

Two smaller cards with:

- category
- title
- short benefit
- prerequisite
- human approval
- effort: low / medium / high
- adoption risk

## Uncertainties

Heading:

> Das ist noch nicht ganz klar

Show only real open points.

No confidence percentages.

---

# 15. PDF report

Create one customer-facing report.

It is not a hidden internal dossier.

The report contains:

- AI Start Map branding
- Derya Sarikaya
- `deryaxsarikaya@gmail.com`
- analysis date
- process title
- summary
- confirmed current process
- current-process diagram or robust fallback
- biggest bottleneck
- symptom, cause and effect
- first recommendation
- mini test
- two additional opportunities
- next realistic target process
- prerequisites
- human approvals
- open points
- contact note

Contact note:

> Bei Fragen zur Auswertung oder zur Umsetzung kannst du Derya Sarikaya unter deryaxsarikaya@gmail.com kontaktieren.

Do not include:

- internal RAG IDs
- chunk IDs
- prompts
- model names
- logs
- technical scores
- session ID
- other-company data
- unconfirmed assumptions

Prefer a robust print view or lightweight PDF approach over a heavy new dependency.

---

# 16. Result actions and CTA

Required primary action:

> Meinen ersten Schritt genauer ansehen

Required secondary actions:

- `Ergebnis als PDF speichern`
- `Einen anderen Ablauf untersuchen`

Business CTA:

Heading:

> Du möchtest Unterstützung bei der Umsetzung?

Text:

> Wenn du deine Auswertung gemeinsam besprechen und daraus einen konkreten Umsetzungsplan machen möchtest, kannst du dich direkt an Derya wenden.

Mail link:

```text
mailto:deryaxsarikaya@gmail.com?subject=Unterstützung%20bei%20meiner%20AI-Start-Map-Auswertung
```

Show this instruction:

> Lade deine Auswertung vorher als PDF herunter und hänge sie anschließend an deine E-Mail an.

Do not claim the browser automatically attaches the PDF.

---

# 17. Session behavior

- session ID stays internal
- no numeric session ID in visible content
- reuse the current session for another recognized process
- preserve answers after analysis errors
- prevent duplicate analysis submission
- do not build a full account system now
- do not promise long-term resume links before a secure token solution exists

---

# 18. RAG integration work

Do not merge all corpora blindly.

Before merge:

- compare 111 + 162 + 361 chunks
- identify duplicate and near-duplicate patterns
- preserve source origin, batch ID and source strength
- keep evaluation cases out of the FAISS index
- keep legal guardrails distinct
- keep case evidence distinct from patterns and recommendations
- weight low-strength evidence down
- retrieve diagnostic patterns and guardrails together with case evidence
- limit repetitive same-pattern cases
- prioritize analog prerequisites for maturity 0–1
- test for unsupported claims and source leakage

Create a merge report before rebuilding the production index.

---

# 19. Bounded Interview Agent

Implemented agent behavior:

- inspect current answers
- decide whether more information is required
- choose the next most useful question
- call specialized tools
- stop when sufficient information is available
- produce three explainable starting points

Implemented tools:

1. workflow and bottleneck extraction
2. curated RAG search
3. opportunity evaluation and prioritization

The agent remains diagnostic and does not execute business processes.

Batch 04 supplies optional retrieval patterns. Safety rules, budgets, no-repeat behavior and loop prevention do not depend on semantic retrieval. The centrally configured demo limits must still be calibrated with real interviews.

---

# 20. Testing priorities

## User journey

- landing page works
- voice and text input work
- unsupported voice browser falls back safely
- transcript is editable
- process cards are understandable
- session ID is not visible
- summary can be corrected
- Mermaid fallback works
- one dynamic question at a time
- max follow-up count enforced
- `Weiß ich gerade nicht` works
- loading state appears immediately
- double submit is blocked
- errors preserve answers
- result clearly separates symptom, cause and effect
- three ranked starting points exist
- current and target process render
- customer PDF includes contact details
- PDF excludes internal data
- mobile controls are usable

## Quality

- no unsupported user facts
- no invented devices, APIs or integrations
- no invented fraud or security risks
- no meta-text inside `as_is_steps`
- no internal identifiers
- recommendations match digital maturity
- proposals are marked as future state
- human approval remains explicit
- low-quality RAG evidence cannot dominate

## Core evaluation cases

- shoe repair with paper notes and shelf search
- third-party pickup
- massage business with multiple channels and capacity constraints
- Etsy/3D print personalization
- carpet cleaning
- carpenter with measurements and changing requirements
- smartphone-only business
- business without digital order data
- contradictory user statements
- case where automation is not yet appropriate

---

# 21. Non-goals

Do not build now:

- React migration
- Lovable integration
- autonomous phone or voice agent
- WhatsApp agent
- messenger orchestration
- master calendar
- digital workforce
- autonomous process execution
- full CRM
- newsletter
- external tracking
- user account system
- automatic price or contract decisions
- full n8n product integration
- automatic PDF email delivery
- hidden internal customer dossier

---

# 22. Immediate execution order

- [x] 1. Analyze the current repository.
- [x] 2. Document the current routes, templates, services and tests in `UX_FLOW.md`.
- [x] 3. Create a minimal-change implementation plan in `UX_FLOW.md`.
- [x] 4. Update `AGENTS.md` with the current product rules.
- [x] 5. Create or update `UX_FLOW.md` and align it with this checklist.
- [x] 6. Implement the landing page and design system.
- [x] 7. Implement voice-first free input with text fallback.
- [x] 8. Redesign process selection.
- [x] 9. Implement the understood-process summary.
- [x] 10. Add safe Mermaid rendering and fallback.
- [x] 11. Add correction flows.
- [x] 12. Integrate dynamic follow-up UI.
- [x] 13. Add loading and error states.
- [x] 14. Redesign the result page.
- [x] 15. Add print/PDF report.
- [x] 16. Add mailto CTA.
- [x] 17. Test responsive structure and mobile interaction rules; visual device screenshots remain blocked by the unavailable local browser runtime.
- [x] 18. Update documentation.
- [x] 19. Review Batch 02 and Batch 03, build a separate 634-chunk test index, compare it and promote it with backup.
- [x] 20. Integrate Batch 04 as deterministic rules, documentation, 205 optional patterns and 40 excluded evaluations.
- [ ] 21. Calibrate question and tool-round heuristics with real AI Start Map interviews.
- [ ] 22. Perform manual Chrome/Android and Safari/iPhone visual acceptance before public production use.

---

# 23. Decision log

- V1 is no longer the product direction.
- V2 focuses on one concrete operational process.
- The visible fixed questionnaire is being replaced by natural narration and dynamic follow-ups.
- Voice is a core input method.
- Browser speech recognition is the first implementation; backend transcription remains a later fallback.
- Mermaid is used on the summary and result pages.
- The result leads with the bottleneck and best first step.
- The customer can export a branded PDF containing Derya's contact information.
- Contact is initially handled through `mailto:`.
- The app diagnoses and recommends but does not execute.
- React and Lovable are not needed for the current phase.
- Batch 02 and Batch 03 are loaded into one controlled diagnostic index without rewriting their source files.
- Batch 04 remains technically separate: hard rules in code/prompt, optional patterns in a second index, documentation outside indexes and evaluations marked `NEVER_INDEX`.
