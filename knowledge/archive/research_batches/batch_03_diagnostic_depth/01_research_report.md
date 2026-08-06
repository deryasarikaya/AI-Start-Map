# Research-Batch 03 – Diagnostic Depth für kleine Betriebe

Stand: 22. Juli 2026

## Zweck

Eigenständige Recherche für AI Start Map. Der Batch erweitert den Wissensraum zu realen operativen Prozessen kleiner Betriebe, ohne bestehende Korpora ungeprüft zu vermischen. Quellenfälle sind ausschließlich Vergleichsmuster und niemals Fakten über den aktuell interviewten Betrieb.

## Harte Evidenzregeln

- `source_reported` enthält nur Inhalte, die aus der jeweiligen Quelle hervorgehen.
- `expert_derived` kennzeichnet Diagnosefragen, Minimalverbesserungen, Automationsoptionen und Guardrails.
- Schwache oder sekundäre Quellen dürfen nur Hypothesen und Rückfragen stützen.
- Größenangaben `small_unknown` sind unbekannt und dürfen nicht als 1–20 bestätigt ausgegeben werden.
- Fälle mit 25 Beschäftigten sind ergänzende Randfälle und zählen nicht als Beleg für das Kernsegment 1–20.

## Coverage

- Unternehmensfälle: 46
- Physische Annahme/Reparatur: 20
- Außeneinsatz: 15
- Auftragsfertigung/Kleinproduktion: 19
- Generalisierte Muster: 18
- Rechts-/Datenschutz-Guardrails: 12

## Zentrale neue Erkenntnisse

1. Objektidentität, physischer Ort und Systemstatus sind drei getrennte Wahrheiten und müssen abgeglichen werden.
2. Ein verlorener Zettel ist kein Sonderfall, sondern ein Test, ob der Betrieb eine zweite Suchkennung besitzt.
3. Drittabholung braucht eine eigene Berechtigung und Identitätsprüfung; sie ist nicht nur eine Kontaktfrage.
4. Zusatzschäden und Preisänderungen benötigen einen sichtbaren Arbeitsstopp bis zur dokumentierten Zustimmung.
5. Papier kann ein legitimes Shopfloor-Interface bleiben, wenn ID, Version und Übergaben robust sind.
6. Smartphone-only, Lärm, Schmutz, Handschuhe und Funklöcher sind Designparameter, keine Randnotizen.
7. Bei Reifegrad 0–1 sind Ordnungsmaßnahmen häufig wertvoller als KI.

## Unternehmensfälle

### RB03-C01 – Versandbasierter Schuhmacher mit strukturiertem Reparaturstart

- Branche: Schuhreparatur
- Land / Größe: DE / small_unknown
- Kategorien: physical_intake, repair, small_batch_production
- Reifegrad: 3
- Quelle/Belegstärke: company_process_page / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: workshop_shipping

**Belegter Ist-Zustand**

Shoedoc beschreibt einen realen deutschen Reparaturprozess: Kundinnen wählen Reparaturen, senden Schuhe ein oder bestellen eine Versandbox; individuelle Wünsche werden separat beraten. Die Werkstatt weist ausdrücklich auf knappen Lagerplatz für zusätzliche Kartons hin und hat mehr als 150.000 Reparaturen durchgeführt.

**Fachliche Diagnoseableitung**

- physischer Gegenstand muss Auftrag und Versand zugeordnet bleiben
- individuelle Wünsche passen nicht vollständig in Standardoptionen
- Lagerplatz ist operativ begrenzt

**Noch zu klären**

- interne Objektkennzeichnung
- Regal- und Zonenlogik
- Freigabeprozess bei Zusatzschäden
- Abholung durch Dritte bei lokaler Annahme

**Ausnahmen**

- Paket ohne eindeutige Zuordnung
- zusätzlicher Reparaturbedarf nach Sichtprüfung
- nicht gewünschter Zusatzkarton

**Kleinster praktikabler Schritt**

Auftrags-ID auf Auftrag, Paar und Verpackung; Pflichtfoto und Freitext für Sonderwünsche; separater Klärstatus.

**Mögliche spätere Automation**

Strukturierte Intake-Extraktion, Statusmeldungen und priorisierte Klärfälle; keine autonome Schadens- oder Preisentscheidung.

**Guardrail**

Keine unbekannten Schäden, Preise oder Reparaturumfänge aus Vergleichsfällen übernehmen; Mehrarbeit erst nach dokumentierter Zustimmung.

Quelle: https://www.shoedoc.de/

### RB03-C02 – Verlorener Abholschein und Suche über Telefonnummer

- Branche: Textilreinigung
- Land / Größe: US / micro_unknown
- Kategorien: physical_intake, repair_like_service
- Reifegrad: 2
- Quelle/Belegstärke: employee_discussion / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Eine Person aus einer Reinigung erklärt, dass der Betrieb Aufträge normalerweise über eine Nummer und die Telefonnummer wiederfindet. Als reale Fehlerpfade nennt sie falschen Namen sowie versehentlich als abgeholt verbuchte Kleidung, die noch auf der Stange hängt.

**Fachliche Diagnoseableitung**

- Papierticket ist nicht robuste alleinige Identität
- Status und physischer Ort können auseinanderlaufen
- Suche unter falschem Namen

**Noch zu klären**

- eindeutige Kleidungsstück-ID
- Identitätsprüfung bei Abholung
- Umgang mit mehreren Teilen pro Auftrag

**Ausnahmen**

- Ticket verloren
- falscher Name
- digital abgeholt, physisch noch vorhanden

**Kleinster praktikabler Schritt**

Zweite Suchkennung wie Telefonnummer plus eindeutige Auftrags-ID; Abholstatus erst beim tatsächlichen Aushändigen setzen.

**Mögliche spätere Automation**

Telefonnummer-/ID-Suche und Abgleichsliste für Status-Ort-Widersprüche.

**Guardrail**

Telefonnummer nie als alleinige sichere Berechtigung für hochwertige oder sensible Gegenstände behandeln.

Quelle: https://www.reddit.com/r/drycleaning/comments/1949xsb/help_lost_dry_cleaning_ticket_am_i_sol/

### RB03-C03 – Papiernummer als primäre Zuordnung von Kleidungsstücken

- Branche: Textilreinigung
- Land / Größe: US / micro_unknown
- Kategorien: physical_intake, repair_like_service
- Reifegrad: 0
- Quelle/Belegstärke: customer_observation / medium
- Primäre Selbstauskunft: false
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Kunde beschreibt eine kleine Reinigung, die bei Annahme einen nummerierten papiernen Abholschein mit Namen ausgibt, offenbar zur Zuordnung der Kleidung.

**Fachliche Diagnoseableitung**

- Papiernummer kann verloren gehen
- keine belegte alternative Suchkennung
- unklare digitale Grundlage

**Noch zu klären**

- Gegenetikett am Kleidungsstück
- Kopie oder Nummernregister
- Abholregel ohne Ticket

**Ausnahmen**

- Ticket unleserlich oder verloren
- mehrere gleichartige Kleidungsstücke

**Kleinster praktikabler Schritt**

Papier beibehalten, aber Nummernliste mit Name und optional Telefonnummer führen; Nummer auch am Objekt befestigen.

**Mögliche spätere Automation**

Erst bei stabilen IDs digitale Suche oder Benachrichtigung ergänzen.

**Guardrail**

Der Kundenbericht belegt nicht den vollständigen internen Ablauf und darf nur Rückfragen/Hypothesen stützen.

Quelle: https://www.reddit.com/r/drycleaning/comments/1neu1t0/why_do_a_lot_of_small_dry_cleaning_business_still/

### RB03-C04 – Nicht abgeholte Kleidung trotz Anrufen und Nachrichten

- Branche: Textilreinigung
- Land / Größe: US / micro_unknown
- Kategorien: physical_intake, repair_like_service
- Reifegrad: 1
- Quelle/Belegstärke: owner_discussion / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Betreiber erklärt: Auf Belegen stehen 30 Tage Abholfrist; tatsächlich werden Kleidungsstücke sechs bis acht Monate aufbewahrt und Kunden zwei- bis dreimal angerufen oder angeschrieben.

**Fachliche Diagnoseableitung**

- Lagerfläche durch Altaufträge
- Erinnerungen ohne verlässliche Eskalationsspur
- Policy und gelebter Prozess weichen ab

**Noch zu klären**

- deutsche Rechtslage und AGB
- Zahlungsstatus
- Lagerort alter Aufträge
- Kontaktkanalpräferenz

**Ausnahmen**

- Kunde reagiert nicht
- Kontaktangabe falsch
- wertvolles oder sentimentales Stück

**Kleinster praktikabler Schritt**

Fälligkeitsdatum, Kontaktversuche und Altauftragszone einheitlich dokumentieren.

**Mögliche spätere Automation**

Gestufte Erinnerungsvorschläge und Altauftragsliste, aber keine automatische Entsorgung oder Verwertung.

**Guardrail**

Aufbewahrung, Gebühren und Verwertung sind rechtlich zu prüfen; niemals autonom entsorgen.

Quelle: https://www.reddit.com/r/drycleaning/comments/a0o0as/dry_clean_owners_how_do_you_deal_with_customers/

### RB03-C05 – Fertige Reparaturen bleiben über ein Jahr in der Werkstatt

- Branche: Trommelbau und -reparatur
- Land / Größe: US / micro
- Kategorien: physical_intake, repair, small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein kleiner Betrieb baut und repariert Trommeln. Schwere Instrumente werden abgegeben und bleiben bis zur Fertigstellung; zwei fertige Reparaturen eines Kunden standen seit über 1,5 Jahren unbezahlt in der Werkstatt. Versand, Onlinezahlung und Abholung durch einen Freund wurden angeboten.

**Fachliche Diagnoseableitung**

- nicht abgeholte sperrige Gegenstände
- offene Zahlung
- wiederholte erfolglose Kommunikation

**Noch zu klären**

- schriftliche Annahmebedingungen
- Lagerplatz
- Anzahlung
- berechtigte Drittperson

**Ausnahmen**

- Drittabholung
- Versand statt Abholung
- Kunde will nur persönlich kommen

**Kleinster praktikabler Schritt**

Bei Annahme Abholfrist, Kontaktweg, Anzahlung und alternative berechtigte Abholperson erfassen.

**Mögliche spätere Automation**

Erinnerungs- und Eskalationsübersicht sowie dokumentierte Freigabe für Versand/Drittabholung.

**Guardrail**

Keine Lagergebühr, Verwertung oder Herausgabe an Dritte ohne geprüfte Regel und Identitätsnachweis.

Quelle: https://www.reddit.com/r/smallbusiness/comments/o45ejx/how_do_you_deal_with_customers_not_picking_up/

### RB03-C06 – Papier-Reparaturaufträge ohne durchsuchbare Fahrzeughistorie

- Branche: Kfz-Werkstatt
- Land / Größe: US / micro_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 0
- Quelle/Belegstärke: operator_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Eine Werkstatt läuft weitgehend mit Papier und Stift. Gesucht wird eine durchsuchbare Erfassung von Fahrzeug, Kunde, Telefon, einzelnen Arbeiten und verbauten Teilen; QuickBooks passte nicht gut zum Serviceprozess.

**Fachliche Diagnoseableitung**

- nicht durchsuchbare Papierhistorie
- Fahrzeug- und Kundendaten nicht sauber gekoppelt
- individuelle Kalkulation je Auftrag

**Noch zu klären**

- Anzahl Mitarbeitende
- aktuelle Nummernlogik
- Fahrzeugidentifikation
- Freigabe bei Mehrarbeit

**Ausnahmen**

- mehrere Fahrzeuge pro Kunde
- zusätzliche Teile
- wiederkehrender Kunde

**Kleinster praktikabler Schritt**

Standardisiertes Reparaturblatt mit Auftrags-ID, Fahrzeug-ID, Pflichtfeldern, Arbeits- und Teilezeilen.

**Mögliche spätere Automation**

Erst nach Standardisierung durchsuchbare Auftragsakte und Rechnungsvorbereitung.

**Guardrail**

KI darf keine Diagnose, Teilebestellung oder Mehrarbeit ohne Fachprüfung/Freigabe auslösen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/2j50a3/invoicing_system_for_car_repair_shop/

### RB03-C07 – Einfacher statt überladener Umstieg von Handschrift

- Branche: Kfz-Werkstatt
- Land / Größe: US / micro_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 0
- Quelle/Belegstärke: family_report / medium
- Primäre Selbstauskunft: false
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Der Sohn eines Werkstattinhabers berichtet, dass sein Vater handschriftliche Rechnungen ablösen will, wenig computererfahren ist und viele Programme als zu komplex empfindet. Chromebook/Google Drive sind bereits vorhanden.

**Fachliche Diagnoseableitung**

- Überladene Systeme gefährden Akzeptanz
- Handschrift als Ausgangspunkt
- begrenzte digitale Kompetenz

**Noch zu klären**

- welche Pflichtdaten wirklich benötigt werden
- wer erfasst
- Gerät am Annahmeplatz

**Ausnahmen**

- Mitarbeiter verweigern komplexe Oberfläche
- Internet fällt aus

**Kleinster praktikabler Schritt**

Minimalformular und eine einfache Rechnungsvorlage auf vorhandenem Gerät testen.

**Mögliche spätere Automation**

Keine KI nötig; später Vorbefüllung wiederkehrender Kunden/Fahrzeuge möglich.

**Guardrail**

Nicht mehr Funktionen einführen als der Betrieb verlässlich nutzt; Quelle ist ein Familienbericht.

Quelle: https://www.reddit.com/r/smallbusiness/comments/gygz9z/simple_invoicing_software_for_auto_repair_shop/

### RB03-C08 – Teilefächer nach letzter Ziffer des Reparaturauftrags

- Branche: Powersports-Werkstatt
- Land / Größe: US / small_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 2
- Quelle/Belegstärke: employee_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_workshop

**Belegter Ist-Zustand**

Ein Mitarbeitender beschreibt ein eigenes Regal für bestellte Werkstattteile. Kartons und Behälter tragen groß die Reparaturauftragsnummer; das Regal ist nach der letzten Ziffer organisiert.

**Fachliche Diagnoseableitung**

- physischer Lagerort hängt an lesbarer Auftragsnummer
- Teile und Auftrag können getrennt eintreffen
- Wissen über Regalregel ist implizit

**Noch zu klären**

- Teilstatus vollständig/teilweise
- Vertretungsregel
- Umgang mit kleinen losen Teilen

**Ausnahmen**

- Nummer fehlt
- falsches Fach
- nur Teilmenge angekommen

**Kleinster praktikabler Schritt**

Regalregel sichtbar dokumentieren; jedes Teil mit Auftrags-ID und Teilstatus versehen.

**Mögliche spätere Automation**

Scan oder Foto beim Einlagern kann digitalen Ort und Vollständigkeit aktualisieren.

**Guardrail**

Automatisch niemals 'vollständig' melden, wenn erwartete Teileliste oder Eingangsscan fehlt.

Quelle: https://www.reddit.com/r/partscounter/comments/zea282/service_schedulework_order_organization/

### RB03-C09 – Sonderteile in nummerierten Regalen mit Papierbeleg

- Branche: Fahrzeugteile/Werkstatt
- Land / Größe: US / small_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 1
- Quelle/Belegstärke: employee_discussion / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_workshop

**Belegter Ist-Zustand**

Ein Teilemitarbeiter beschreibt Regale 0–9; Sonderbestellungen landen anhand der letzten Ziffer des Arbeitsauftrags im Fach. Teile tragen Pickticket oder liegen mit Papier in einer Box. Der Werkstattmeister muss selbst nachsehen.

**Fachliche Diagnoseableitung**

- Status wird durch Nachsehen ermittelt
- Papier begleitet Kleinteile
- Verantwortung zwischen Teilelager und Meister

**Noch zu klären**

- Benachrichtigung bei vollständigem Eingang
- Fehlteilprozess
- Rückgabe falscher Teile

**Ausnahmen**

- Papier löst sich
- Teil in falschem Fach
- Auftrag wartet auf mehrere Lieferungen

**Kleinster praktikabler Schritt**

Erwartete Teileliste plus sichtbarer Vollständigkeitsmarker am Fach.

**Mögliche spätere Automation**

Eingangserfassung kann Meister nur bei vollständiger Liste benachrichtigen.

**Guardrail**

Keine Termin- oder Fertigzusage allein aus einem einzelnen Teileingang ableiten.

Quelle: https://www.reddit.com/r/partscounter/comments/1kyioc1/special_orders/

### RB03-C10 – Papier- und Digitalakten als Nachweis bei falscher Bewertung

- Branche: Computerreparatur
- Land / Größe: US / micro
- Kategorien: physical_intake, repair
- Reifegrad: 2
- Quelle/Belegstärke: former_owner_comment / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein ehemaliger PC-Werkstattinhaber berichtet, Arbeitsaufträge parallel auf Papier und digital aufbewahrt zu haben. Dadurch konnte er feststellen, dass ein negativer Bewerter nie Kunde war.

**Fachliche Diagnoseableitung**

- doppelte Aktenführung
- Nachweis realer Kundenbeziehung
- personenbezogene Reparaturhistorie

**Noch zu klären**

- Aufbewahrungsdauer
- Abgleich zwischen Papier und digital
- Zugriffsrechte

**Ausnahmen**

- Aliasname in Bewertung
- Altauftrag
- Datenlöschpflicht

**Kleinster praktikabler Schritt**

Eindeutige Auftrags-ID und eine maßgebliche Akte definieren; Papier nur soweit nötig referenzieren.

**Mögliche spätere Automation**

Suche und Nachweisunterstützung ohne öffentliche automatische Antwort.

**Guardrail**

Bewertungen nicht automatisch personenbezogen zuordnen oder beantworten; Datenschutz und Beleglage prüfen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1uviuvj/one_bad_review_from_a_customer_who_was_never_in/

### RB03-C11 – Volle Kapazität und viele Anfragen außerhalb des Gebiets

- Branche: Hausgerätereparatur
- Land / Größe: US / micro
- Kategorien: physical_intake, repair, field_service
- Reifegrad: 2
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein selbstständiger Reparaturbetrieb ist im eigenen Gebiet ausgebucht; bessere Google-Platzierung erzeugt viele Anrufe von Kunden, die geografisch zu weit entfernt sind.

**Fachliche Diagnoseableitung**

- unqualifizierte Anfragen verbrauchen Zeit
- Gebiets- und Kapazitätsgrenze
- Weiterleitung nicht organisiert

**Noch zu klären**

- genaue Postleitzahlen
- Reisezeitgrenze
- Warteliste
- Partnerbetriebe

**Ausnahmen**

- dringender Notfall
- Bestandskunde außerhalb Kerngebiet
- mehrere Aufträge in derselben Route

**Kleinster praktikabler Schritt**

Servicegebiet und Kapazitätsregel sichtbar erfassen; Anfragen zunächst nach Ort und Gerät qualifizieren.

**Mögliche spätere Automation**

Intake-Assistent kann unpassende Anfragen markieren und Antwortentwurf/Partnerliste anbieten.

**Guardrail**

Keine Terminbestätigung ohne reale Kapazitäts- und Gebietsprüfung.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1637zuw/what_do_i_do_with_too_much_business/

### RB03-C12 – Abholstatus widerspricht Kundenaussage; alte Papierbelege werden durchsucht

- Branche: Schmuckreparatur
- Land / Größe: US / small_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 2
- Quelle/Belegstärke: employee_story / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Eine Mitarbeiterin eines Juweliergeschäfts beschreibt einen Reparaturfall, der im System als lange zuvor abgeholt stand. Bei späterer Nachfrage wurden Papierbelege durchsucht; dort war vermerkt, dass das Stück nach langer Nichtabholung verworfen worden sei.

**Fachliche Diagnoseableitung**

- digitaler Abholstatus und Papiernotiz müssen zusammenpassen
- langfristige Aufbewahrung
- hohes Konflikt- und Wertrisiko

**Noch zu klären**

- Identitätsprüfung bei Abholung
- Unterschrift
- Aufbewahrungsregel
- Wert und Fotos

**Ausnahmen**

- Kunde behauptet Nichtabholung
- Abholung durch Dritte
- Gegenstand verwertet

**Kleinster praktikabler Schritt**

Abholung mit Datum, abholender Person und Beleg erfassen; Altaufträge gesondert prüfen.

**Mögliche spätere Automation**

Widerspruchsflag bei Statuskonflikt und gezielte Akten-/Ortssuche.

**Guardrail**

Keine Herausgabe, Verwertung oder Schuldzuweisung automatisieren; Quelle ist ein Mitarbeiterbericht aus dem Einzelhandel.

Quelle: https://www.reddit.com/r/TalesFromRetail/comments/6r582h/in_which_the_customer_doesnt_pick_up_her_item_for/

### RB03-C13 – Arbeitsaufträge, Teilelisten und Serviceintervalle auf Papier/Whiteboard

- Branche: Flottenwartung
- Land / Größe: unknown / small_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 0
- Quelle/Belegstärke: employee_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_mobile_workshop

**Belegter Ist-Zustand**

Ein Mitarbeitender beschreibt Papier-Arbeitsaufträge, Ordner für Teile- und Filterlisten, einen Notizblock für offene Arbeiten und ein Whiteboard für aktuelle und nächste Servicekilometer/-stunden. Arbeitszeit wurde nicht in den Kosten erfasst.

**Fachliche Diagnoseableitung**

- mehrere analoge Wahrheiten
- offene Aufgaben werden manuell übertragen
- Arbeitskosten fehlen
- Servicefälligkeit nur am Whiteboard

**Noch zu klären**

- Fahrzeug-ID
- verantwortliche Person
- Pflichtfelder für Abschluss
- Offline-Anforderung

**Ausnahmen**

- Aufgabe beim Monatswechsel vergessen
- Whiteboard gelöscht
- Teil nicht dokumentiert

**Kleinster praktikabler Schritt**

Einheitliche Fahrzeug-ID und ein einziges Wartungsblatt je Fahrzeug; offene Arbeit mit Verantwortlichem und Fälligkeit.

**Mögliche spätere Automation**

Später mobile/offline Erfassung und Fälligkeitsliste; KI höchstens für Notizstrukturierung.

**Guardrail**

Keine Sicherheitsfreigabe oder Wartungsentscheidung aus unvollständigen Notizen automatisieren.

Quelle: https://www.reddit.com/r/MechanicAdvice/comments/1r86f4/id_like_your_advice_on_how_to_improve_how_our/

### RB03-C14 – 75 Maschinen in Warteschlange und drei Wochen Durchlauf

- Branche: Nähmaschinenreparatur
- Land / Größe: US / small_independent_store
- Kategorien: physical_intake, repair
- Reifegrad: 2
- Quelle/Belegstärke: technician_story / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_workshop

**Belegter Ist-Zustand**

Ein Techniker eines unabhängigen Quiltladens mit eigener Reparatur beschreibt ungefähr 75 Maschinen im Lager in der Warteschlange und rund drei Wochen Durchlauf. Zusätzlich gibt es eine Queue, bei der Kunden erst zum erreichten Platz bringen.

**Fachliche Diagnoseableitung**

- Kapazitäts- und Reihenfolgeplanung
- viele ähnliche physische Geräte
- zwei unterschiedliche Annahmemodelle

**Noch zu klären**

- Kennzeichnung im Lager
- Prioritätsregeln
- Abgleich Anruf/Voicemail
- Ersatzteile

**Ausnahmen**

- Kunde bringt Maschine nicht rechtzeitig
- früher fertig als erwartet
- Maschine nicht auffindbar

**Kleinster praktikabler Schritt**

Queue-Typ, Position, Geräte-ID und tatsächlichen Lagerort dokumentieren.

**Mögliche spätere Automation**

Benachrichtigungsentwürfe, Queue-Übersicht und Kapazitätswarnung.

**Guardrail**

Fertigtermin nicht autonom versprechen; reale Werkstattkapazität und Teile prüfen.

Quelle: https://www.reddit.com/r/TalesFromRetail/comments/vylv44/how_dare_you_finish_my_machine_repair_quickly/

### RB03-C15 – Gerät nach Monaten nicht auffindbar und Rückruf bleibt aus

- Branche: Nähmaschinenreparatur
- Land / Größe: US / small_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 1
- Quelle/Belegstärke: customer_report / medium
- Primäre Selbstauskunft: false
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Eine Kundin berichtet, eine Maschine mit zugesagten vier bis sechs Wochen abgegeben zu haben. Nach rund 40 Wochen klang es, als sei noch nicht begonnen worden; der Betrieb habe zunächst nicht gewusst, wo die Maschine sei, und nicht zurückgerufen.

**Fachliche Diagnoseableitung**

- verlorener physischer Standort
- nicht eingehaltene Durchlaufzusage
- fehlender Rückruf

**Noch zu klären**

- tatsächlicher interner Ablauf
- Ticket/ID
- Lagerzonen
- Kontaktprotokoll

**Ausnahmen**

- Gerät falsch abgestellt
- Auftrag ohne Status
- Kundeneskalation

**Kleinster praktikabler Schritt**

Jedes Gerät beim Ortswechsel mit ID und Zone dokumentieren; Rückrufaufgabe mit Verantwortlichem.

**Mögliche spätere Automation**

Standort-/Statussuche und Eskalationsliste erst nach stabiler Kennzeichnung.

**Guardrail**

Kundenbericht nicht als bestätigtes internes Fehlverhalten verallgemeinern; keine automatische Schuldzuweisung.

Quelle: https://www.reddit.com/r/sewinghelp/comments/1pwqtrf/singer_repair_shop_has_my_machine_since_march/

### RB03-C16 – Zeit und Wirtschaftlichkeit je Stück werden schlecht verfolgt

- Branche: Möbelrestaurierung
- Land / Größe: US / micro
- Kategorien: physical_intake, repair, small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_workshop

**Belegter Ist-Zustand**

Eine Inhaberin im Möbel-/Vintagegeschäft sagt offen, die Zeit zur Verkaufsfertigkeit schlecht zu verfolgen. Zwischen Arbeitsaufwand, theoretischem Höchstpreis und Qualitätsanspruch entstehen wiederkehrende Abwägungen; Stücke können drei bis sechs Monate binden.

**Fachliche Diagnoseableitung**

- fehlende Stückzeit
- unklare Marge
- Qualitätsentscheidung personengebunden
- langes Work-in-progress

**Noch zu klären**

- Stück-ID
- Materialkosten
- Arbeitsphasen
- Abbruchkriterium

**Ausnahmen**

- verdeckter Zusatzschaden
- mehr Arbeit als wirtschaftlich
- sentimentaler Qualitätsanspruch

**Kleinster praktikabler Schritt**

Stück-ID und grobe Start/Stopp-Zeiten je Phase; Material und erwarteter Verkaufspreis erfassen.

**Mögliche spätere Automation**

WIP-Übersicht und Warnung bei Zeit-/Kostenabweichung; Entscheidung bleibt beim Menschen.

**Guardrail**

KI darf weder Restaurierungsumfang noch Preis auf Basis theoretischer Werte autonom bestimmen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/14lgjmj/i_stuck_at_the_business_part_of_my_business_how/

### RB03-C17 – Smartphone-only Zeiterfassung direkt am Projekt

- Branche: Polsterei/Katzenmöbel
- Land / Größe: unknown / micro
- Kategorien: physical_intake, repair, small_batch_production
- Reifegrad: 2
- Quelle/Belegstärke: owner_post / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_smartphone_only

**Belegter Ist-Zustand**

Ein Betreiber eines kleinen Polster-/Katzenmöbelgeschäfts beschreibt eine selbst gebaute mobile Zeiterfassung: Projekt auf dem Smartphone wählen und Start/Stop drücken; die App berechnet Dauer und kann einen Link erzeugen.

**Fachliche Diagnoseableitung**

- Zeiterfassung muss werkstattnah und extrem einfach sein
- Projektwahl ist zentrale Zuordnung
- Smartphone ist das verfügbare Gerät

**Noch zu klären**

- Offlinefähigkeit
- schmutzige Hände
- Korrektur vergessener Stopps
- Mehrbenutzerbetrieb

**Ausnahmen**

- falsches Projekt gewählt
- Timer läuft weiter
- Telefon nicht verfügbar

**Kleinster praktikabler Schritt**

Ein-Tap-Projektauswahl mit sichtbarer laufender Arbeit und einfacher Korrektur.

**Mögliche spätere Automation**

Aus Zeiten können Nachkalkulationshinweise entstehen; keine automatische Leistungsbewertung.

**Guardrail**

Mitarbeiterzeiten nicht heimlich überwachen; Zweck, Zugriff und Korrektur transparent regeln.

Quelle: https://www.reddit.com/r/furniturerestoration/comments/1t14f05/i_made_a_time_tracker_for_my_cattree_upholstery/

### RB03-C18 – Zusatzarbeit ohne dokumentierte Freigabe

- Branche: Kfz-Reparatur
- Land / Größe: US / small_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 2
- Quelle/Belegstärke: customer_report / medium
- Primäre Selbstauskunft: false
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Kunde berichtet, auf dem Annahmeformular ausdrücklich keine Arbeit vor Kostenvoranschlag autorisiert zu haben; trotzdem sei Arbeit ausgeführt worden. Der Fall zeigt den Konflikt zwischen Diagnose, Zusatzarbeit und Zustimmung.

**Fachliche Diagnoseableitung**

- Freigabegrenze nicht im Arbeitsablauf erzwungen
- Annahmehinweis erreicht Werkstatt nicht sicher
- Kostenkonflikt

**Noch zu klären**

- tatsächliche Werkstattdokumentation
- Diagnosegebühr
- Freigabekanal
- Rechtsraum

**Ausnahmen**

- Sicherheitskritischer Befund
- Kunde nicht erreichbar
- Preis ändert sich nach Demontage

**Kleinster praktikabler Schritt**

Freigabestatus und genehmigter Maximalbetrag direkt am Arbeitsauftrag sichtbar machen.

**Mögliche spätere Automation**

Freigabeanfrage mit Befund, Foto, Preisänderung und explizitem Ja/Nein; Arbeit bleibt gesperrt.

**Guardrail**

Keine Mehrarbeit, Preisänderung oder rechtliche Bewertung automatisch freigeben; Kundenbericht ist keine geprüfte Rechtsfeststellung.

Quelle: https://www.reddit.com/r/MechanicAdvice/comments/1bvu92k/mechanic_did_work_without_my_authorization/

### RB03-C19 – Papierauftrag wandert wöchentlich vom Feld bis zur Rechnung

- Branche: Elektroservice
- Land / Größe: CA / small_unknown
- Kategorien: field_service
- Reifegrad: 0
- Quelle/Belegstärke: operator_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_noisy_mobile

**Belegter Ist-Zustand**

Ein Elektroservice gibt Papier-Arbeitsaufträge aus. Monteure tragen Zeit und Material auf einem weiteren Blatt ein, sammeln eine Woche und geben montags ab; Papiere wandern zu Projektleitern, werden bepreist und zur Rechnung geschrieben.

**Fachliche Diagnoseableitung**

- lange Verzögerung bis Faktura
- mehrfache Papierübergabe
- Zeit und Material auf getrennten Blättern
- Verlustrisiko

**Noch zu klären**

- Geräte im Feld
- Netzabdeckung
- Freigabe des Projektleiters
- Nachträge

**Ausnahmen**

- Blatt fehlt
- unleserliche Menge
- Zusatzarbeit
- mehrere Projektleiter

**Kleinster praktikabler Schritt**

Ein einheitlicher nummerierter Arbeitsnachweis mit Zeit, Material, Unterschrift und Projektzuordnung.

**Mögliche spätere Automation**

Mobile/offline Erfassung und Rechnungsvorbereitung nach Projektleiterfreigabe.

**Guardrail**

Keine Materialmenge oder Kundenabnahme aus unleserlichen Notizen erraten.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1b8h7kb/electrical_contracting/

### RB03-C20 – Wachstum von Solo auf sechs Mitarbeitende überlastet Inhaber

- Branche: SHK/HVAC
- Land / Größe: US / small_6
- Kategorien: field_service
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein HVAC-Inhaber wuchs in etwa einem Jahr von Solo auf sechs Mitarbeitende: Servicetechniker, Installateure, Auszubildende und Büroleitung. Er beschreibt hohe Arbeitslast und Burnout-Angst bei fehlender Managementerfahrung.

**Fachliche Diagnoseableitung**

- Rollen und Übergaben wachsen schneller als Prozess
- Inhaber bleibt Engpass
- unterschiedliche Qualifikation bei Einsatzzuordnung

**Noch zu klären**

- Dispatch-Regeln
- Auftragsarten
- Qualifikationsmatrix
- Büro-Feld-Übergaben

**Ausnahmen**

- Mitarbeiterausfall
- Notdienst
- Azubi braucht Begleitung

**Kleinster praktikabler Schritt**

Auftragsarten, Rollen, Zuständigkeiten und Eskalationen sichtbar definieren.

**Mögliche spätere Automation**

Vorschlag für Einsatzzuordnung und Tagesbriefing, aber menschliche Disposition.

**Guardrail**

Keine Leistungsbewertung oder Einsatzentscheidung nur aus KI-Scoring.

Quelle: https://www.reddit.com/r/smallbusiness/comments/113psbe/hvac_company_has_grown_quickly_but_i_am/

### RB03-C21 – Fertige Aufträge bleiben mit hohem Restbetrag unbezahlt

- Branche: Zaunbau
- Land / Größe: US / small_unknown
- Kategorien: field_service, small_batch_production
- Reifegrad: 2
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein kleiner Zaunbaubetrieb verlangt 40 Prozent Anzahlung und Restzahlung bei Fertigstellung. Rund 20.000 Dollar waren überfällig; der Inhaber schrieb wiederholt E-Mails und Erinnerungen.

**Fachliche Diagnoseableitung**

- Leistungsabschluss und Zahlung entkoppelt
- manuelles Nachfassen
- Liquiditätsrisiko

**Noch zu klären**

- Abnahmebeleg
- Fälligkeit und Vertrag
- strittige Mängel
- Teilzahlungen

**Ausnahmen**

- Kunde reklamiert
- Abnahme fehlt
- Zahlung falsch zugeordnet

**Kleinster praktikabler Schritt**

Abnahme, Schlussrechnung, Fälligkeit und Kontaktversuche pro Auftrag dokumentieren.

**Mögliche spätere Automation**

Zahlungsabgleich und Erinnerungsentwürfe; Eskalationsstufen nur nach Freigabe.

**Guardrail**

Keine Mahngebühr, Drohung oder rechtliche Maßnahme automatisch auslösen; US-Fall nicht als deutsches Recht verwenden.

Quelle: https://www.reddit.com/r/smallbusiness/comments/15cxem4/customers_not_paying_when_job_is_completed/

### RB03-C22 – Acht Beschäftigte, Planung und Telefon hängen an einer Person

- Branche: Handwerker-/Hausmeisterbetrieb
- Land / Größe: US / small_8
- Kategorien: field_service
- Reifegrad: 1
- Quelle/Belegstärke: manager_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: smartphone_field

**Belegter Ist-Zustand**

Die Managerin eines Acht-Personen-Handwerkerbetriebs plant die Woche, schreibt Rechnungen, kassiert, erledigt Payroll, beantwortet das Firmenhandy auf ihrer privaten Nummer und dirigiert Teams tagsüber. Drei unterschiedliche Stundensätze werden genutzt; Margen sind knapp.

**Fachliche Diagnoseableitung**

- starke Personenabhängigkeit
- privates Telefon als Betriebskanal
- Planänderungen
- knappe Nachkalkulation

**Noch zu klären**

- Auftragsprioritäten
- Bereitschaft
- Materialkosten
- Vertretung
- Erreichbarkeitszeiten

**Ausnahmen**

- Krankheit der Managerin
- dringender Auftrag
- falscher Stundensatz

**Kleinster praktikabler Schritt**

Firmenkanal und gemeinsamer Wochenplan; Auftrag, Team, Satz und Status einheitlich führen.

**Mögliche spätere Automation**

Intake-Zusammenfassung, Planänderungsvorschlag und Rechnungsvorbereitung.

**Guardrail**

Private Kontaktdaten schützen; keine Lohn-/Leistungsentscheidung automatisch treffen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1phv2xp/need_advice_as_the_manager_of_a_small_handyman/

### RB03-C23 – Excel, Jobber und Monday für denselben Betrieb

- Branche: Handwerker/Landschaftspflege
- Land / Größe: US / micro_with_helpers
- Kategorien: field_service
- Reifegrad: 2
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Teilzeit-Handwerker-/Landschaftspflegebetrieb mit einigen Aushilfen nutzt Excel für Geschäftsübersicht, Jobber für Angebote und Monday für Mitarbeitendenplanung. Der Inhaber bevorzugt Excel wegen Anpassbarkeit.

**Fachliche Diagnoseableitung**

- gleiche Auftragsdaten über drei Systeme
- Toolkosten
- Akzeptanz hängt an Flexibilität

**Noch zu klären**

- welches System führend ist
- doppelte Eingabe
- Zahlungs-/Statusabgleich
- mobile Nutzung

**Ausnahmen**

- Plan geändert, Angebot nicht aktualisiert
- Mitarbeiter sieht veralteten Stand

**Kleinster praktikabler Schritt**

Führendes Auftragsregister festlegen und nur notwendige Übergaben definieren.

**Mögliche spätere Automation**

Synchronisation erst nach Feldmapping; KI kann Notizen strukturieren, nicht Inkonsistenzen verdecken.

**Guardrail**

Keine Datenkopplung ohne Verantwortlichkeit und Fehlerbehandlung.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1m38230/is_it_worth_purchasing_a_software_for_my_company/

### RB03-C24 – Nischenbetrieb findet kein passendes Termin- und Rechnungssystem

- Branche: Brunnen-/Wassertechnik
- Land / Größe: US / small_unknown
- Kategorien: field_service
- Reifegrad: 2
- Quelle/Belegstärke: operator_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Nischen-Servicebetrieb für Wasserbrunnen nutzt Kickserv, sucht aber mehr Anpassbarkeit. Ein getestetes System importierte Rechnungen und Steuergebiete nicht, obwohl beides benötigt wird.

**Fachliche Diagnoseableitung**

- Standardsoftware bildet Nischenregeln nicht ab
- Datenmigration unvollständig
- steuerliche Gebietslogik

**Noch zu klären**

- wiederkehrende Einsätze
- Objekt-/Standortstruktur
- Steuerlogik
- Offlinebedarf

**Ausnahmen**

- mehrere Standorte
- altes Rechnungshistorie fehlt
- falsches Steuergebiet

**Kleinster praktikabler Schritt**

Muss-Felder und unverzichtbare Schnittstellen vor Toolwahl festlegen; Testmigration mit wenigen Aufträgen.

**Mögliche spätere Automation**

Automatisierung nur nach geprüftem Mapping; Abweichungsbericht bei fehlenden Daten.

**Guardrail**

Steuerzuordnung nie durch Sprachmodell raten lassen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/hbf6g1/what_scheduling_software_do_you_use_to_schedule/

### RB03-C25 – Mehrere Einsatzorte pro Kunde müssen erhalten bleiben

- Branche: Hausreparaturservice
- Land / Größe: US / micro
- Kategorien: field_service
- Reifegrad: 2
- Quelle/Belegstärke: owner_comment / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Betreiber eines Hausreparaturservices berichtet, ein System zur Verfolgung von Serviceaufträgen je Kunde zu nutzen; mehrere Orte pro Kunde sind für HOA- und Gewerbekunden wichtig.

**Fachliche Diagnoseableitung**

- Kunde und Einsatzort dürfen nicht gleichgesetzt werden
- Auftragshistorie je Objekt
- wiederkehrende Standorte

**Noch zu klären**

- Ansprechperson je Standort
- Zutritt
- Objekt-ID
- Leistungsnachweis

**Ausnahmen**

- Rechnung an Zentrale, Arbeit an Objekt
- Kontakt wechselt
- mehrere offene Aufträge

**Kleinster praktikabler Schritt**

Kundenkonto, Standort und konkreten Auftrag als getrennte Objekte modellieren.

**Mögliche spätere Automation**

Standortbezogene Historie und Vorbereitungshinweise abrufen.

**Guardrail**

Keine Zugangsdaten oder sensible Objektinformationen unnötig in KI-Kontext geben.

Quelle: https://www.reddit.com/r/smallbusiness/comments/p5drdh/software_for_small_maintenanceservice_company/

### RB03-C26 – Handschriftliche Außendienstbelege gehen verloren

- Branche: HVAC-Reparatur
- Land / Größe: US / micro
- Kategorien: field_service, repair
- Reifegrad: 0
- Quelle/Belegstärke: owner_post / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_noisy_mobile

**Belegter Ist-Zustand**

Ein kleiner HVAC-Reparaturbetrieb schreibt Arbeitsaufträge auf einfachem Papier, verliert Kopien und möchte detaillierte Rechnungen erstellen, ohne nach jedem Einsatz ins Büro zurückzumüssen.

**Fachliche Diagnoseableitung**

- keine Durchschläge
- Verlust zwischen Einsatz und Büro
- mobile Rechnungsvorbereitung
- professioneller Nachweis für Gewerbekunden

**Noch zu klären**

- Smartphone verfügbar
- Offline/Netz
- Kundenunterschrift
- Materialliste

**Ausnahmen**

- nasse/verschmutzte Umgebung
- Telefon leer
- Kunde verlangt Papier

**Kleinster praktikabler Schritt**

Nummerierter Durchschreibesatz oder offlinefähiges Minimalformular mit Export; Papieroption erhalten.

**Mögliche spätere Automation**

Foto/OCR kann lesbare Felder vorschlagen, muss aber vom Techniker bestätigt werden.

**Guardrail**

Unleserliche Mengen, Zeiten oder Leistungen niemals automatisch ergänzen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1rrjp22/how_do_you_handle_paperwork_and_invoicing_when/

### RB03-C27 – Millionenumsatz vollständig in Papierheften und Rechnungsblöcken

- Branche: Bauunternehmen
- Land / Größe: US / small_unknown
- Kategorien: field_service, small_batch_production
- Reifegrad: 0
- Quelle/Belegstärke: family_employee_comment / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Familienmitglied berichtet, der Bau-betrieb führe das gesamte Geschäft in Papiernotizbüchern und Rechnungsblättern, ohne Website; genannt werden 5–6 Mio. Umsatz. Beschäftigtenzahl ist unbekannt.

**Fachliche Diagnoseableitung**

- keine digitale Grundlage
- Wissen in Heften
- hohes Umstellungsrisiko trotz funktionierendem Betrieb

**Noch zu klären**

- Mitarbeitendenzahl
- welche Hefte wofür
- Suchprobleme
- Gerätebereitschaft

**Ausnahmen**

- Heft verloren
- Vertretung
- parallel geführte Notizen

**Kleinster praktikabler Schritt**

Nicht alles digitalisieren: zuerst Auftragsnummer, Pflichtfelder, Ablage und Wochenregister vereinheitlichen.

**Mögliche spätere Automation**

Später Smartphone-Fotoeingang und strukturierte Übernahme ausgewählter Felder.

**Guardrail**

Funktionierenden Papierprozess nicht ohne Nutzenbeleg ersetzen; Umsatz beweist keine Prozessqualität oder Zielgruppengröße.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1epn7eo/i_cannot_believe_people_still_do_this/

### RB03-C28 – Ein-Mann-Außendienst weiß nicht, wie Wachstum organisiert werden soll

- Branche: Teppichreinigung
- Land / Größe: US / solo
- Kategorien: field_service
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Solo-Teppichreiniger arbeitet seit vier Jahren mit einem Van und eigener Ausrüstung, nennt rund 90.000 Dollar Jahresumsatz und weiß nicht, wie er den Übergang zu Wachstum/Personal organisieren soll.

**Fachliche Diagnoseableitung**

- Inhaber ist Leistung, Vertrieb und Disposition zugleich
- fehlende replizierbare Übergabe
- Fahrzeug/Ausrüstung als Kapazitätsgrenze

**Noch zu klären**

- Standardleistungen
- Einsatzdauer
- Qualitätscheck
- zweites Fahrzeug
- Tourengebiet

**Ausnahmen**

- Krankheit
- Nacharbeit
- Mitarbeiter ohne Ausrüstung

**Kleinster praktikabler Schritt**

Standardauftrag, Checkliste, Zeit- und Materialbedarf sowie Qualitätsnachweis dokumentieren.

**Mögliche spätere Automation**

Erst danach Termin-/Routenvorschläge und Übergabe an Mitarbeitende.

**Guardrail**

Keine Skalierungsempfehlung ohne Nachfrage, Marge, Qualitätsstandard und Einarbeitungsfähigkeit.

Quelle: https://www.reddit.com/r/smallbusiness/comments/etpa15/looking_to_expand_my_one_man_business_dont_know/

### RB03-C29 – Neun-Personen-Betrieb koppelt Einsatz und Abrechnung

- Branche: Schädlingsbekämpfung
- Land / Größe: US / small_9
- Kategorien: field_service
- Reifegrad: 3
- Quelle/Belegstärke: vendor_case_study / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Die Anbieterfallstudie nennt Parker Eco Pest Control, einen von einem Ehepaar geführten Betrieb mit neun Beschäftigten. Im Mittelpunkt stehen wiederkehrende Einsätze, Abrechnung und Zahlungseingänge.

**Fachliche Diagnoseableitung**

- wiederkehrende Routen müssen korrekt fakturiert werden
- Büro und Feld benötigen gemeinsamen Status
- Anbieterquelle betont Produkterfolg

**Noch zu klären**

- Vorherprozess im Detail
- Chemikalien-/Leistungsnachweis
- Ausnahmen bei Zutritt
- deutsche Anforderungen

**Ausnahmen**

- Kunde nicht zuhause
- Nachbehandlung
- Route verschoben

**Kleinster praktikabler Schritt**

Wiederkehrenden Auftrag, Besuch, Leistungsnachweis und Rechnung getrennt aber verknüpft führen.

**Mögliche spätere Automation**

Tourenvorschläge, Besuchsdokumentation und Fakturavorbereitung.

**Guardrail**

Anbieterfall nicht als unabhängigen Wirkungsnachweis behandeln; keine Behandlung oder Rechnung ohne bestätigten Besuch.

Quelle: https://www.getjobber.com/academy/pest-control/parker-eco-pest-control/

### RB03-C30 – Sales-Pitch übergeht Wunsch nach einfachem Tarif

- Branche: Teppichreinigung
- Land / Größe: US / micro_unknown
- Kategorien: field_service
- Reifegrad: 2
- Quelle/Belegstärke: owner_post / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Teppichreinigungsbetrieb sucht POS, Rechnungen, Angebote, Automatisierung, Marketing und Onlinebuchung. Im Verkaufsgespräch sei der Wunsch nach dem Basistarif ignoriert und nur der höchste Tarif beworben worden.

**Fachliche Diagnoseableitung**

- Toolauswahl wird von Verkauf statt Bedarf getrieben
- Funktionsumfang und Budget unklar
- bestehendes Lead-System

**Noch zu klären**

- tatsächliche Kernprobleme
- Integrationsbedarf
- Nutzerzahl
- Must-have versus nice-to-have

**Ausnahmen**

- Doppeltes Lead-System
- zu teurer Tarif
- Mitarbeiterakzeptanz

**Kleinster praktikabler Schritt**

Anforderungen priorisieren und kleinen Pilot mit echten Aufträgen durchführen.

**Mögliche spätere Automation**

Erst nach Pilot gezielte Integration; keine pauschale All-in-one-Empfehlung.

**Guardrail**

Produktempfehlungen müssen Bedarf, Kosten und Datenmigration transparent machen.

Quelle: https://www.reddit.com/r/CarpetCleaning/comments/1k0wuie/house_call_pro/

### RB03-C31 – 14-Personen-Betrieb modelliert erst analoge Ist-Prozesse

- Branche: Tischlerei
- Land / Größe: DE / small_14
- Kategorien: small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: public_program_case / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Die Tischlerei Dreyer mit 14 Beschäftigten fertigt individuelle Fenster, Türen, Treppen und Möbel. Vor der Digitalisierung riet das Mittelstand-Digital-Zentrum zur Prozessaufnahme. Zwei Ist-Prozesse zeigten sofort Verbesserungsmöglichkeiten und wie analog der Ablauf war; erst danach wurde die Modernisierung des Warenwirtschaftssystems geplant.

**Fachliche Diagnoseableitung**

- Digitalisierung ohne Prozessklarheit wäre verfrüht
- individuelle Fertigung
- WWS soll reale Kernprozesse unterstützen

**Noch zu klären**

- konkrete zwei Ist-Prozesse
- Auftrags-ID
- Material- und Freigabepunkte
- Maschinendaten

**Ausnahmen**

- Sondermaß
- Änderung nach Auftrag
- Denkmalschutzanforderung

**Kleinster praktikabler Schritt**

Prozesslandkarte, zwei konkrete Ist-Abläufe und Verantwortlichkeiten vor Toolauswahl.

**Mögliche spätere Automation**

Später strukturierte Auftragsakte, Material-/Statusübergaben und WWS-Anbindung.

**Guardrail**

Keine KI-Lösung empfehlen, solange Ablauf, Datenverantwortung und Pflichtfelder nicht verstanden sind.

Quelle: https://www.digitalzentrum-magdeburg.de/praxisbeispiele/prozesse-als-grundlage-der-digitalisierung-im-tischlereihandwerk/

### RB03-C32 – Kleines Druckunternehmen sucht Entlastung in Planung und Qualität

- Branche: Etikettendruck
- Land / Größe: DE / small_25
- Kategorien: small_batch_production
- Reifegrad: 3
- Quelle/Belegstärke: public_program_case / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Jungdruck produziert Etiketten mit rund 25 Beschäftigten. Mitarbeitende nannten bedarfsgerechte Dokumentbereitstellung, Forecasts für Druckplanung, weniger Ablagen und Wiederholungen sowie weniger unnötige Telefonate. Persönlicher Kontakt soll nicht ersetzt werden; bei Produktionsprotokollen sollen Audioinhalte gelöscht werden.

**Fachliche Diagnoseableitung**

- Dokumente erreichen nicht zielgenau die richtigen Personen
- wiederholte Abläufe und Telefonate
- Planungs- und Qualitätsfragen

**Noch zu klären**

- konkrete Dokumenttypen
- Datenqualität für Forecast
- Fehlerklassen
- Audio-Löschprozess

**Ausnahmen**

- Qualitätsabweichung
- Planänderung
- sensible Gesprächsinhalte

**Kleinster praktikabler Schritt**

Dokumenttypen, Empfänger, Planungsdaten und Löschregeln zuerst festlegen.

**Mögliche spätere Automation**

Dokumentenrouting, Protokollentwurf und Forecast-Unterstützung mit Parallelprüfung.

**Guardrail**

25 Beschäftigte liegen knapp über dem Kernsegment; Audio nicht dauerhaft speichern und persönliche Kommunikation nicht ersetzen.

Quelle: https://www.digitalzentrum-zukunftskultur.de/praxisbeispiele/wie-kuenstliche-intelligenz-ein-kleines-druckunternehmen-voranbringen-kann-14157/

### RB03-C33 – Variantenreicher Auftrag braucht neuen Angebotsprozess

- Branche: Kabelkonfektionierung
- Land / Größe: DE / small_25
- Kategorien: small_batch_production
- Reifegrad: 3
- Quelle/Belegstärke: public_program_case / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein deutscher Kabelkonfektionierer mit 25 Beschäftigten fertigt kundenspezifische, zu 100 Prozent geprüfte Kabelsätze. Der bisherige Anfrage-bis-Angebot-Prozess dauerte etwa zwei Wochen; für kleine variantenreiche Startup-Aufträge wurde ein neuer Prozess mit Konfigurator entwickelt, Ziel drei Tage.

**Fachliche Diagnoseableitung**

- viele Varianten
- Angebotsprozess nicht für kleine schnelle Lose geeignet
- Preis hängt an technischen Parametern

**Noch zu klären**

- zulässige Parameterkombinationen
- Sonderfall außerhalb Konfigurator
- Freigabe und Prüfung

**Ausnahmen**

- nicht konfigurierbare Anfrage
- Prototyp
- Änderung der Stückzahl

**Kleinster praktikabler Schritt**

Varianten, Pflichtparameter, Regeln und Sonderfallpfad definieren.

**Mögliche spätere Automation**

Konfigurator/Regelwerk; KI nur zur Vorstrukturierung freier Anfragen.

**Guardrail**

Preis und technische Machbarkeit nicht vom Sprachmodell erfinden; 25 Beschäftigte knapp über Kernsegment.

Quelle: https://mittelstand-digital-ruhr-owl.de/kabelkonfektionierung-konfigurator-beschleunigt-den-vertriebsprozess/

### RB03-C34 – Wachstum verdeckt fehlende Wirtschaftlichkeit

- Branche: Individueller Möbelbau
- Land / Größe: US / small_unknown
- Kategorien: small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Inhaber kaufte einen bestehenden individuellen Möbelbaubetrieb und steigerte im ersten Jahr den Umsatz deutlich. Später beschreibt er eine wirtschaftliche Krise; der Betrieb entwirft und baut Einzelmöbel für Privatkunden und Designer.

**Fachliche Diagnoseableitung**

- Umsatz allein zeigt keine Auftragsprofitabilität
- individuelle Planung und Fertigung
- Kapazität und Kosten je Auftrag

**Noch zu klären**

- Angebotskalkulation
- Nachträge
- Materialpreis
- Arbeitsstunden
- Auftragsmix

**Ausnahmen**

- Designänderung
- Materialverzug
- Nacharbeit

**Kleinster praktikabler Schritt**

Auftragsbezogene Nachkalkulation mit Material, Zeit, Fremdleistung und Änderung.

**Mögliche spätere Automation**

Abweichungs- und WIP-Übersicht; KI kann Spezifikationen strukturieren.

**Guardrail**

Keine Profitabilitäts- oder Preisentscheidung ohne vollständige belegte Kosten.

Quelle: https://www.reddit.com/r/smallbusiness/comments/17050bx/business_is_failing_struggling_to_get_out_of_this/

### RB03-C35 – 200 Sonderhoodies, Designfreigabe und Storno nach Produktionsstart

- Branche: Textildruck
- Land / Größe: US / micro
- Kategorien: small_batch_production
- Reifegrad: 2
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein kleiner Textildruckbetrieb berichtet über 200 individuell bedruckte Hoodies, mehrere Designrunden, ausdrückliche Freigabe, 50 Prozent Anzahlung und eine spezielle Puffdruck-Anforderung. Der Konflikt entstand nach der Freigabe/Anzahlung im weiteren Auftragsverlauf.

**Fachliche Diagnoseableitung**

- Varianten- und Designfreigabe
- Sondermaterial/Verfahren
- Storno- und Änderungsrisiko
- Anzahlung deckt nicht zwingend alles

**Noch zu klären**

- Freigabeversion
- Produktionsstart
- Materialbestellung
- Stornoregel
- Restzahlung

**Ausnahmen**

- Kunde ändert Design
- Sonderdruck misslingt
- Storno nach Materialkauf

**Kleinster praktikabler Schritt**

Versionierte Freigabe, Produktionsfreigabe und Material-/Kostenstatus dokumentieren.

**Mögliche spätere Automation**

Freigabe-Workflow, Änderungsfolgen-Entwurf und Produktionsstatus.

**Guardrail**

Keine Design-, Preis- oder Stornoentscheidung autonom; Vertragslage getrennt prüfen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1qh8hv9/custom_apparel_customer_placed_huge_order_then/

### RB03-C36 – Papierauftrag bleibt trotz digitalem System am physischen Job

- Branche: Druckerei
- Land / Größe: unknown / small_unknown
- Kategorien: small_batch_production
- Reifegrad: 3
- Quelle/Belegstärke: print_employee_discussion / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: noisy_dirty_workshop

**Belegter Ist-Zustand**

Ein Druckereimitarbeiter beschreibt, dass ein vorheriger Betrieb Jobs digital suchbar und verfolgbar machte, aber weiterhin Papierdockets in Hüllen am physischen Auftrag nutzte. Papier ermöglicht, ähnliche Jobs vor der Maschine in Sekunden zu gruppieren.

**Fachliche Diagnoseableitung**

- physisches Papier erfüllt schnelle Shopfloor-Funktion
- rein digitales Soll kann Arbeit verlangsamen
- digitaler Status und physischer Stapel koexistieren

**Noch zu klären**

- führender Status
- Docket-ID
- Änderung während Produktion
- Fehler bei Gruppierung

**Ausnahmen**

- Docket getrennt vom Material
- digitale Änderung erreicht Papier nicht
- Eilauftrag

**Kleinster praktikabler Schritt**

Papierdocket mit eindeutiger ID und Versionsmarker beibehalten; digitalen Status nur an klaren Übergaben aktualisieren.

**Mögliche spätere Automation**

Scan an Stationen und Änderungswarnung; keine Pflicht zur papierlosen Werkstatt.

**Guardrail**

Papier nicht als Rückständigkeit behandeln; die reale Handhabung und Geschwindigkeit zählen.

Quelle: https://www.reddit.com/r/CommercialPrinting/comments/1l21gqv/ticketless_print_shop/

### RB03-C37 – Bestellungen in Textnachrichten und Notizbuch

- Branche: Pflanzenverkauf
- Land / Größe: unknown / micro
- Kategorien: small_batch_production
- Reifegrad: 0
- Quelle/Belegstärke: family_solution_report / low
- Primäre Selbstauskunft: false
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Entwickler berichtet, seine Frau verkaufe Pflanzen und habe Bestellungen in Textnachrichten und einem Notizbuch verfolgt; daraus entstand ein einfaches Auftragswerkzeug. Der ursprüngliche Betrieb spricht nicht selbst.

**Fachliche Diagnoseableitung**

- unstrukturierte Bestelleingänge
- Notizbuch ohne Status
- Medienbruch zu Rechnung

**Noch zu klären**

- Produktvarianten
- Bestand
- Abholung/Versand
- Zahlung
- Saison

**Ausnahmen**

- doppelte Anfrage
- Pflanze nicht mehr verfügbar
- Abholung verschoben

**Kleinster praktikabler Schritt**

Eine gemeinsame Bestellliste mit Kunde, Pflanze, Menge, Fälligkeit, Status und Zahlung.

**Mögliche spätere Automation**

Nachrichtenextraktion nur als Entwurf mit Bestätigung.

**Guardrail**

Niedrige Quellenstärke: nur Hypothesen und Rückfragen stützen, nie allein eine Empfehlung.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1s19mjg/promote_your_business_week_of_march_23_2026/

### RB03-C38 – Nachfrage übersteigt manuelle Fertigungskapazität

- Branche: Handgefertigte Produkte
- Land / Größe: unknown / micro
- Kategorien: small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Ein Betreiber eines arbeitsintensiven Handmade-Geschäfts fragt nach Skalierung, weil die aktuelle Nachfrage nicht mehr erfüllt werden kann.

**Fachliche Diagnoseableitung**

- Handarbeit ist Kapazitätsgrenze
- Skalierung darf Qualität nicht verdecken
- Auftragsannahme ohne realistische Kapazität

**Noch zu klären**

- Produktmix
- Arbeitszeit je Stück
- Wartezeit
- auslagerbare Schritte
- Qualitätsprüfung

**Ausnahmen**

- Eilauftrag
- Qualitätsabweichung
- Material fehlt

**Kleinster praktikabler Schritt**

Zeit je Produktfamilie und verfügbare Wochenkapazität grob messen; Annahmelimit definieren.

**Mögliche spätere Automation**

Kapazitätswarnung und realistische Lieferfenster; keine autonome Annahme.

**Guardrail**

Nicht automatisch mehr Aufträge bestätigen oder Handarbeit durch ungeprüfte Standardisierung entwerten.

Quelle: https://www.reddit.com/r/smallbusiness/comments/8zxy73/scaling_a_handmade_business_not_sure_in_which/

### RB03-C39 – Herstellung ist nur noch ein kleiner Teil der Arbeit

- Branche: Handgefertigter Schmuck
- Land / Größe: unknown / solo
- Kategorien: small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / medium
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Eine Schmuckmacherin berichtet, nur etwa 20 Prozent der Zeit mit Herstellung zu verbringen; der Rest entfällt auf E-Mails, Social Media, Bestände, Preise, Lieferanten, Ausgaben und Versandprobleme.

**Fachliche Diagnoseableitung**

- Administration verdrängt Kernleistung
- Bestand und Preisfindung
- Lieferanten- und Versandfälle

**Noch zu klären**

- wiederkehrende E-Mailtypen
- SKU/Material
- Marge
- Sonderanfertigung
- Retouren

**Ausnahmen**

- Materialpreis ändert sich
- Versandproblem
- Kunde vergleicht mit Massenware

**Kleinster praktikabler Schritt**

Produktfamilien, Materialkosten, Bestände und wiederkehrende Kommunikationsfälle strukturieren.

**Mögliche spätere Automation**

Antwortentwürfe, Bestandswarnung und Kalkulationsunterstützung.

**Guardrail**

Keine Preisentscheidung oder Qualitätsbehauptung autonom; genannte Zeitanteile nicht übertragen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1pumohp/opening_a_small_jewelry_business_felt_like_a/

### RB03-C40 – Drei Systeme für Bestand und Rückverfolgbarkeit

- Branche: Austernzucht und -distribution
- Land / Größe: US / small_unknown
- Kategorien: small_batch_production, field_service
- Reifegrad: 3
- Quelle/Belegstärke: operations_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: normal

**Belegter Ist-Zustand**

Die Betriebskoordination einer Austernfarm beschreibt Google Sheets, QuickBooks und eine branchenspezifische Rückverfolgungs-App. Eigene Produktion und zugekaufte Ware lokaler Farmen müssen gemeinsam verteilt und rückverfolgt werden.

**Fachliche Diagnoseableitung**

- mehrere Datenquellen
- eigene und fremde Chargen
- regulatorisch relevante Rückverfolgbarkeit
- Bestandsabgleich

**Noch zu klären**

- Chargen-ID
- Ernte-/Eingangsdatum
- Kühlkette
- führendes System
- Rückrufprozess

**Ausnahmen**

- Charge gemischt
- Menge korrigiert
- Rückruf
- Lieferantendaten fehlen

**Kleinster praktikabler Schritt**

Datenverantwortung, Chargen-ID und Pflichtfelder systemübergreifend festlegen; Testabgleich.

**Mögliche spätere Automation**

Anomalie- und Dublettenhinweise, keine autonome Compliance-Freigabe.

**Guardrail**

Rückverfolgbarkeits- oder Lebensmittelsicherheitsentscheidungen nie allein durch KI treffen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1fz1sdj/looking_for_new_inventory_management_softwareerp/

### RB03-C41 – WhatsApp als Bedienoberfläche für Auftragsstatus

- Branche: Fenster- und Türenfertigung
- Land / Größe: unknown / small_unknown
- Kategorien: small_batch_production
- Reifegrad: 3
- Quelle/Belegstärke: solution_author_report / medium
- Primäre Selbstauskunft: false
- Arbeitsumgebung: smartphone_only_workshop

**Belegter Ist-Zustand**

Ein Lösungsentwickler berichtet von einem laufenden System in einer Fenster- und Türenfertigung: Aufträge per WhatsApp anlegen/ändern, Fotos in Drive, Live-Sheet, Status-/Liefermeldungen und Zahlungslinks. Die behauptete Arbeitsreduktion stammt vom Entwickler, nicht vom Betrieb.

**Fachliche Diagnoseableitung**

- WhatsApp ist verfügbare Oberfläche
- Fotos und Auftragsdaten brauchen Zuordnung
- Statusänderung über Chat birgt Fehler

**Noch zu klären**

- Betriebsgröße
- Freigaberegeln
- Dubletten
- Änderungsprotokoll
- Datenschutz

**Ausnahmen**

- Sprachnachricht missverstanden
- falscher Auftrag geändert
- Preis-/Lieferzusage

**Kleinster praktikabler Schritt**

Vor Chat-Automation stabile Auftrags-ID, erlaubte Statuswerte, Rollen und Bestätigungsansicht.

**Mögliche spätere Automation**

Chat kann Aktionen vorschlagen; jede Änderung zeigt Zielauftrag und neue Werte zur Bestätigung.

**Guardrail**

Entwicklerbehauptungen nicht als unabhängigen Erfolg werten; keine Preis-, Zahlungs- oder Lieferzusage ohne Freigabe.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1pncop7/i_built_a_whatsapp_ai_system_that_runs_business/

### RB03-C42 – Inhaber hält Frontdesk, Teile, Planung und Buchhaltung allein zusammen

- Branche: Kfz-Reparatur
- Land / Größe: US / micro_unknown
- Kategorien: physical_intake, repair
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_noisy_workshop

**Belegter Ist-Zustand**

Der Betreiber einer kleinen informellen Kfz-Werkstatt beschreibt, persönlich Telefon, Terminplanung, Kundenkontakt, Teile, Serviceberatung, Buchhaltung und Reinigung zu übernehmen, während Techniker die Reparaturen ausführen. Unzuverlässige Anwesenheit der Techniker ist sein wiederkehrendes Kernproblem.

**Fachliche Diagnoseableitung**

- viele Rollen bündeln sich beim Inhaber
- Planung hängt von kurzfristiger Personalverfügbarkeit ab
- Frontdesk und Werkstatt brauchen verlässliche Übergaben

**Noch zu klären**

- Anzahl Techniker
- verbindliche Schichten
- Status je Fahrzeug
- Vertretung am Frontdesk

**Ausnahmen**

- Techniker erscheint nicht
- Kunde wartet bereits
- Teil ist da, aber Qualifikation fehlt

**Kleinster praktikabler Schritt**

Tagesplan mit Fahrzeug, Arbeit, benötigter Qualifikation, bestätigter Person und Eskalation bei Ausfall.

**Mögliche spätere Automation**

Kapazitätswarnung und Umplanungsvorschlag; keine automatische Personalmaßnahme.

**Guardrail**

Arbeits- und Personalentscheidungen bleiben menschlich; informelle US-Werkstatt nicht als deutsches Arbeitsmodell übertragen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1g2jgm9/auto_repair_shop_what_more_can_i_do_seeking_raw/

### RB03-C43 – Fehlende Ausgabenbelege verhindern verlässliche Wirtschaftlichkeitsanalyse

- Branche: Kleinmotoren-Reparatur
- Land / Größe: US / micro
- Kategorien: physical_intake, repair
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_workshop

**Belegter Ist-Zustand**

Der Inhaber einer sehr kleinen Kleinmotoren-Werkstatt berichtet im ersten Steuerjahr nur einen geringen rechnerischen Gewinn und vermutet, Ausgabenbelege verloren zu haben, die das Ergebnis verändern würden.

**Fachliche Diagnoseableitung**

- Belege fehlen
- Wirtschaftlichkeit kann nicht belastbar beurteilt werden
- Auftrags- und Kostenbezug ist unklar

**Noch zu klären**

- Belegkanäle
- Material je Auftrag
- Eigenzeit
- private und betriebliche Ausgaben

**Ausnahmen**

- Barbeleg fehlt
- Teil für mehrere Aufträge
- Rückerstattung oder Retoure

**Kleinster praktikabler Schritt**

Ein fester Belegeingang per Umschlag oder Smartphonefoto und wöchentlicher Vollständigkeitscheck.

**Mögliche spätere Automation**

Belegextraktion darf Felder vorschlagen; steuerliche Zuordnung und Buchung werden geprüft.

**Guardrail**

Keine Steuerentscheidung oder Rentabilitätsaussage aus unvollständigen Belegen automatisieren.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1ank4bq/i_own_a_small_engine_repair_shop_it_is_a_very/

### RB03-C44 – Papieraufträge laufen durch Produktion und werden erst am Ende fakturiert

- Branche: Druck, Stickerei und Werbetechnik
- Land / Größe: unknown / small_unknown
- Kategorien: small_batch_production
- Reifegrad: 1
- Quelle/Belegstärke: operator_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_noisy_workshop

**Belegter Ist-Zustand**

Ein Betrieb mit Druck, Stickerei/Workwear und Beschilderung beschreibt Papieraufträge, die durch die Produktion bis zur abschließenden Rechnung wandern. Der Betrieb ist stark über Kapazität, verliert den Überblick und erlebt dadurch Verzögerungen; ein passendes System für alle drei Arbeitsarten ist schwer zu finden.

**Fachliche Diagnoseableitung**

- Papierauftrag ist Träger von Status und Rechnungsdaten
- heterogene Produktionsarten
- Überkapazität und fehlender Überblick verursachen Verspätung

**Noch zu klären**

- Mitarbeitendenzahl
- Arbeitsstationen
- Prioritätsregeln
- führende Auftragsliste
- Freigaben

**Ausnahmen**

- Auftrag teilt sich auf mehrere Produktionswege
- Eilauftrag
- Papier fehlt vor Faktura

**Kleinster praktikabler Schritt**

Gemeinsame Auftrags-ID und wenige Statuswerte über alle drei Bereiche; Papierbegleiter bleibt mit ID erhalten.

**Mögliche spätere Automation**

WIP- und Kapazitätsübersicht sowie Rechnungsvorbereitung nach dokumentiertem Abschluss.

**Guardrail**

Keinen Liefertermin allein aus nominaler Queue ableiten; Material, Maschine und Qualifikation prüfen.

Quelle: https://www.reddit.com/r/CommercialPrinting/comments/1ozhvsq/shop_order_management/

### RB03-C45 – Wachstum erzeugt manuelle Rechnungen und verstreute Wartungsprotokolle

- Branche: Mobile Kfz- und Flottenreparatur
- Land / Größe: US / small_unknown
- Kategorien: field_service, repair
- Reifegrad: 1
- Quelle/Belegstärke: owner_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_noisy_mobile

**Belegter Ist-Zustand**

Der Betreiber einer wachsenden kleinen Kfz-/Flottenwerkstatt beschreibt mehrere Kundenkonten, Außentechniker, mobile Serviceeinsätze sowie zu viele manuelle Rechnungen und Wartungsprotokolle.

**Fachliche Diagnoseableitung**

- Kunde, Fahrzeug und Einsatz müssen getrennt verbunden werden
- mobile Übergabe zur Rechnung
- Wartungshistorie verteilt sich

**Noch zu klären**

- Flottengröße
- Fahrzeug-ID
- Offlinebedarf
- Freigabe und Abnahme
- wiederkehrende Intervalle

**Ausnahmen**

- Techniker ohne Netz
- Fahrzeug wechselt Standort
- Notfalleinsatz außerhalb Planung

**Kleinster praktikabler Schritt**

Kundenkonto, Fahrzeug, Einsatz und Wartungsereignis als getrennte Datensätze mit einer gemeinsamen Einsatz-ID führen.

**Mögliche spätere Automation**

Offlinefähiger Arbeitsnachweis, Wartungsfälligkeit und geprüfte Rechnungsvorbereitung.

**Guardrail**

Keine Sicherheitsfreigabe, Wartungsentscheidung oder Rechnung aus unbestätigten Feldnotizen erzeugen.

Quelle: https://www.reddit.com/r/smallbusiness/comments/1lk5955/any_recommendations_for_managing_a_growing/

### RB03-C46 – Papier-Jobtasche bewahrt Korrekturen, die das elektronische Ticket nicht enthält

- Branche: Druckproduktion
- Land / Größe: unknown / small_unknown
- Kategorien: small_batch_production
- Reifegrad: 2
- Quelle/Belegstärke: employee_post / high
- Primäre Selbstauskunft: true
- Arbeitsumgebung: dirty_noisy_workshop

**Belegter Ist-Zustand**

Eine Person aus der Druckproduktion beschreibt elektronische Arbeitstickets neben physischen Jobtaschen. In einem konkreten Auftrag war die Materialnummer im elektronischen Ticket falsch; die handschriftlich korrigierte Nummer im vorherigen Papierticket half, den Fehler erneut zu korrigieren.

**Fachliche Diagnoseableitung**

- Korrektur erreicht Stammdaten oder Vorlage nicht
- Papier enthält operative Wahrheit
- Fehler wiederholt sich in Folgeauftrag

**Noch zu klären**

- wer darf Materialnummer ändern
- Versionsführung
- Verknüpfung von Wiederholauftrag und Jobtasche
- Qualitätsprüfung

**Ausnahmen**

- alte Handschrift falsch
- mehrere gültige Materialalternativen
- digitale Vorlage überschreibt Korrektur

**Kleinster praktikabler Schritt**

Korrekturen mit Grund, Verantwortlichem und Gültigkeit direkt an der führenden Spezifikation erfassen; Papier referenziert die Version.

**Mögliche spätere Automation**

Abweichung zwischen aktuellem Ticket und letzter bestätigter Spezifikation markieren.

**Guardrail**

Korrektur nicht autonom übernehmen; Material und Version müssen fachlich bestätigt werden.

Quelle: https://www.reddit.com/r/CommercialPrinting/comments/187q2wd/workflow/
