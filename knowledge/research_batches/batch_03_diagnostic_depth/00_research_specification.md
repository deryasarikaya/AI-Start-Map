# Research-Spezifikation – Batch 03 Diagnostic Depth

Stand: 22. Juli 2026

## 1. Ziel

Batch 03 erweitert die AI-Start-Map-Wissensbasis um belastbares Wissen zur operativen Realität kleiner Betriebe. Der Batch unterstützt die Analyse von Ist-Prozessen, Engpässen, Reifegrad, Ausnahmen, Priorisierung, Automationsvoraussetzungen, minimalen Verbesserungen und menschlichen Freigaben.

Er wird nicht mit den bestehenden 111 beziehungsweise 162 Chunks zusammengeführt. Integration erfolgt erst nach eigenständiger Qualitäts- und Dublettenprüfung.

## 2. Zielgruppe und geografischer Fokus

- Solo-Selbstständige, Kleinstunternehmen und Betriebe mit ungefähr 1–20 Mitarbeitenden
- Schwerpunkt Deutschland
- internationale Fälle nur ergänzend, wenn der operative Prozess übertragbar ist
- Fälle außerhalb 1–20 werden als Randfälle gekennzeichnet und zählen nicht zur Kernabdeckung

## 3. Prozessabdeckung

- Kundengewinnung und Eingang von Anfragen
- Angebot, Freigabe und Auftrag
- Termin-, Touren- und Kapazitätsplanung
- physische Annahme, Kennzeichnung, Lagerung, Reparatur und Abholung
- Leistungserbringung im Außendienst
- Auftragsfertigung und Kleinproduktion
- Einkauf, Material, Teile und Bestand
- Kundenkommunikation, Dokumentation und Übergaben
- Rechnung, Zahlung, Erinnerung und Mahnung
- Reklamation, Zusatzschäden und Nacharbeit
- Personalorganisation und Zeiterfassung
- interne Wissensablage
- Datenschutz, Sicherheit und menschliche Freigaben

Der Schwerpunkt liegt auf operativen Abläufen, nicht auf allgemeiner Unternehmensstrategie.

## 4. Verbindliche Fallziele

- mindestens 30 neue Unternehmensfälle
- mindestens 15 Fälle aus physischer Annahme, Reparatur oder Werkstatt
- mindestens 10 Fälle mit Außeneinsätzen
- mindestens 10 Fälle aus Auftragsfertigung oder Kleinproduktion

Kategorien dürfen sich überschneiden. Bereits in Batch 01/02 verwendete URLs werden nicht erneut als neue Fälle gezählt.

## 5. Besondere Lücken

Explizit zu prüfen sind:

- Schuhmacher und andere Reparaturen physischer Gegenstände
- verlorene Nummern, Zettel und Abholscheine
- Regal, Fach, Stange, Stapel und Statuszone
- Abholung durch Familienmitglieder oder andere Dritte
- Zusatzschaden, Preisänderung und neue Zustimmung
- nicht abgeholte Gegenstände
- Betriebe ohne Laptop sowie Smartphone-only
- Lärm, Schmutz, Handschuhe, Feuchtigkeit, Funkloch und mobile Arbeit
- Prozesse, die vor Digitalisierung erst geordnet werden müssen

## 6. Quellenhierarchie

1. direkte öffentliche Aussagen von Inhabenden oder beteiligten Mitarbeitenden
2. deutsche Handwerkskammern, IHK, Mittelstand-Digital, Verbände und seriöse Forschungs-/Praxisberichte
3. konkrete Anbieterfallstudien mit transparentem Vorherprozess
4. Kunden- oder Familienberichte nur als sekundäre Evidenz

Reine Produktwerbung ohne konkreten Ist-Prozess wird nicht als Fallbeleg genutzt. Schwache Evidenz darf nur Hypothesen und Rückfragen stützen.

## 7. Trennung der Inhalte

- `case_evidence`: nur belegter Ist-Ablauf und belegter Engpass
- `diagnostic_pattern`: generalisiertes fachliches Muster
- `diagnostic_question_set`: fachlich fehlende Prozessinformationen, keine Agentensteuerung
- `digital_readiness_pattern`: Voraussetzungen des Reifegrads
- `implementation_prerequisite`: notwendige Ordnung, Daten und Verantwortung
- `minimal_viable_improvement`: kleinster praktikabler Schritt
- `automation_pattern`: möglicher späterer Zielablauf
- `automation_guardrail`: Grenzen, Risiken und Human-Approval

`content_origin`, `source_strength`, `is_primary_evidence`, `batch_id` und Quellen-URL bleiben erhalten.

## 8. Bewertungs- und Priorisierungslogik

Nutzen, Häufigkeit, Standardisierbarkeit, Datenreife, Integrationsaufwand, Datenschutz, Akzeptanz und notwendige menschliche Entscheidung werden anhand transparenter Rubrics und belegter Eingaben bewertet. Fehlende Werte werden nicht erfunden.

Bei Reifegrad 0–1 werden Standardisierung, Objekt-ID, Pflichtfelder, Status, Ablage und Verantwortung vor KI oder Systemintegration priorisiert.

## 9. Recht und Guardrails

Rechts- und Datenschutzwissen stammt soweit möglich aus deutschen/EU-Primärquellen, erhält Prüfdatum und muss aktualisierbar bleiben. Es ersetzt keine Rechtsberatung.

Preis, Zusatzarbeit, Termin, Zahlung, Bestellung, Vertrag, Qualität, Personalentscheidung, Entsorgung und Herausgabe an Dritte benötigen menschliche Freigabe.

## 10. Ausdrückliche Abgrenzung zu Batch 04

Nicht Bestandteil von Batch 03 sind:

- `agent_decision_pattern`
- `next_question_pattern`
- `information_gap_pattern` als Auswahl-/Rankinglogik des Agenten
- `contradiction_pattern` als Dialogsteuerung
- `stop_condition`
- `tool_selection_pattern`
- `insufficient_evidence_pattern` als Agentenentscheidung

Diese Inhalte werden später eigenständig und evidenzbasiert in `batch_04_agentic_interview` recherchiert. Batch 03 liefert nur fachliche Prozesslücken, keine Policy zur dynamischen Auswahl der nächsten Frage.

## 11. Qualitäts- und Merge-Ablauf

Neue Recherche → Ergebnis prüfen → neue Muster identifizieren → Dopplungen entfernen → Quellenstärke prüfen → Fallwissen und späteres Agentenwissen trennen → kontrolliert integrieren.

Evaluation bleibt vom produktiven RAG-Index getrennt.
