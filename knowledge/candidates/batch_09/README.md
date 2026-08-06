# Batch 09 – Lösungswissen für digital arbeitende Kleinbetriebe

## Ziel und Abgrenzung

Batch 09 beschreibt Kleinbetriebe der digitalen Reifegrade 2 und 3: Digitale Spuren sind vorhanden, aber freie Inhalte, mehrere Kanäle und manuelle Übergaben verhindern einen durchgängigen, prüfbaren Ablauf. Rein analoge Fälle, physische Zuordnungsprobleme als Hauptursache sowie hochregulierte oder autonome Entscheidungen sind ausgeschlossen. SP-04 bleibt nur als dokumentarischer Katalogeintrag enthalten.

## Lieferumfang

- 27 prüfpflichtige Customer-Inference-Patterns
- 28 konkrete Solution Workflows
- 10 deterministische Output-Grundstrukturen
- 30 Evaluationen, strikt von allen RAG-Indizes ausgeschlossen
- 20 Quellen im Quellenregister
- eine kurze menschenlesbare Zusammenfassung

## Suchstrategie und Quellen

Gesucht wurde in offiziellen Statistiken und Studien zu KMU und GenAI, Kammer- und Behördenleitfäden zu Auftragsabwicklung, E-Rechnung, Dokumentation und Digitalisierung sowie regulatorischen Leitlinien zu Datenschutz, Sicherheit, Richtigkeit und Human Oversight. Branchenabläufe wurden nur übertragen, wenn ihre Prozessschritte nachvollziehbar waren. Alltagssprache wurde knapp paraphrasiert und nie als repräsentatives Zitat ausgegeben.

Quellentypen: OECD- und Eurostat-Studien, Bundesministerien, EU-Kommission, Datenschutzkonferenz, BSI, IHK und öffentlich geförderte Mittelstandsleitfäden. Widerspruch: Quellen zeigen steigende KI-Nutzung, zugleich aber erhebliche Kompetenz-, Rechts- und Datenschutzbarrieren. Deshalb empfiehlt Batch 09 kleine, überprüfbare Assistenzschritte statt autonome End-to-End-Automation.

## Verteilung

Inference Patterns nach Problemfamilie: {'PF-02': 3, 'PF-03': 3, 'PF-04': 3, 'PF-06': 3, 'PF-07': 3, 'PF-08': 3, 'PF-09': 3, 'PF-11': 3, 'PF-12': 3}

Solution Workflows nach Lösungsmuster: {'SP-01': 3, 'SP-02': 3, 'SP-03': 3, 'SP-04': 1, 'SP-05': 3, 'SP-06': 3, 'SP-07': 3, 'SP-08': 3, 'SP-09': 3, 'SP-10': 3}

Content Origin: Inference Patterns und Workflows sind `source_synthesized`; Output-Strukturen sind wegen ihrer normativen Produktfunktion `expert_derived`. Evaluationen sind `research_proposed` und kein Produktwissen.

## Systemrollen

- Deterministische Runtime-Daten: Output-Grundstrukturen, Pflichtfelder, Human Checks, Nicht-Automationen, Mindestvoraussetzungen.
- RAG-Wissen: Kundensprache, Branchenvarianten, Zielworkflows, Hindernisse und typische offene Punkte.
- Agentenwissen: Hypothesen, beobachtbare Verifikationsfragen, Antwortverzweigungen und Informationslücken.

Diese Rollen dürfen beim späteren Merge nicht vermischt werden. Eine Hypothese wird nie zu einem Nutzerfakt, nur weil sie gut zur Wissensbasis passt.

## Qualitätsregeln

1. Jede Empfehlung endet in einem konkreten Zielworkflow und sichtbaren Output.
2. Keine Empfehlung ohne Mindestvoraussetzungen und Quellenbezug.
3. KI erzeugt Entwürfe; Regeln prüfen harte Bedingungen; Menschen bestätigen folgenreiche Angaben.
4. Keine autonomen Preis-, Vertrags-, Zahlungs-, Personal-, Qualitäts- oder Herausgabeentscheidungen.
5. Keine Produktnamen, erfundenen Einsparungen oder unbelegten Prozentwerte.
6. Originale bleiben erhalten; Unsicherheiten, Widersprüche und fehlende Angaben bleiben sichtbar.
7. Beispielwerte sind Platzhalter und niemals Kundenfakten.
8. Evaluationen dürfen niemals indexiert werden.

## Bekannte Lücken

- Nur begrenzte öffentlich zugängliche qualitative Primärdaten mit wörtlicher Alltagssprache deutscher Solo-Selbstständiger.
- Branchenvarianten sind fachlich plausible Synthesen und müssen durch Interviews mit echten Betrieben validiert werden.
- Keine Rechtsberatung und keine abschließende Datenschutz-Folgenabschätzung pro konkreter Implementierung.
- Keine Toolauswahl, Schnittstellenprüfung oder Wirtschaftlichkeitsrechnung.
- PF-05 und physische Objekt-/Ablagezuordnung bewusst nicht untersucht.

## Fachliche Prüfung vor Produktiveinsatz

Die Daten sind maschinenlesbar und formal validiert, bleiben aber Forschungsentwürfe. Vor dem Merge: Branchenexpert:innen prüfen Pflichtfelder und Fachsprache; reale Betriebe prüfen Verständlichkeit und Alltagstauglichkeit; Datenschutz und Recht prüfen konkrete Datenflüsse; Engineering prüft Runtime-Schema, Versionierung und Index-Ausschluss.

## Kernaussage

Für digital arbeitende Kleinbetriebe ist der sinnvolle erste KI-Schritt meist: vorhandene Nachrichten, Sprache, PDFs, Fotos oder Tabellen in einen prüfbaren Entwurf überführen, Lücken sichtbar machen und erst nach menschlicher Bestätigung weiterarbeiten.
