# Research-Batch 02: Analoge Realität und digitale Anschlussfähigkeit in Kleinstunternehmen

**Recherche-Stichtag:** 17. Juli 2026  
**Umfang:** 35 neue, anonymisierte Quellenfälle  
**Abgrenzung:** separater Batch; keine Aussage aus früheren Korpora wurde als Beleg für diese Fälle verwendet.

## Methodik und Leseschlüssel

Die Fälle wurden nach öffentlich berichteten Arbeitsabläufen ausgewählt. Ein Reddit-Post gilt als öffentliche Selbstauskunft, nicht als unabhängig verifizierter Geschäftsbericht. `hoch` bedeutet hier: konkrete Ist-Abläufe, Akteure oder Medienbrüche sind detailliert beschrieben. `mittel`: der Kernengpass ist direkt berichtet, wichtige Prozessschritte fehlen. `niedrig`: kurzer oder indirekter Bericht; nur zur Hypothesenbildung geeignet.

Der **digitale Reifegrad** ist eine fachliche Einschätzung: 0 = überwiegend Gedächtnis/Papier; 1 = einzelne digitale Inseln; 2 = wiederkehrende Tabellen/Apps ohne gemeinsamen Datensatz; 3 = zentrale Fachanwendung mit Lücken; 4 = verbundene, weitgehend strukturierte Abläufe; 5 = messbar gesteuerte, integrierte Abläufe. Er ist kein Quellenfakt.

Die **Verbesserungstreppe** ist in allen Fällen gleich: A Ordnung/Standards, B minimale strukturierte Erfassung, C gemeinsamer Status, D regelbasierte Teilautomatisierung, E KI-Assistenz auf belastbaren Daten. Eine höhere Stufe ist nicht automatisch besser.

---

## RB02-C01 – Übernommene Änderungsschneiderei

1. **Kurzprofil:** Kleine Änderungsschneiderei mit mehreren Näherinnen und auftragsbezogener Vergütung.
2. **Quellenlage/Vertrauen:** Mittel; direkte Selbstauskunft des neuen Inhabers, aber nur ein Beitrag.
3. **Belegte Ausgangssituation:** Manuelle Tickets werden gesammelt; wöchentlich werden Ticketdaten in eine Tabelle übertragen, um prozentuale Zahlungen an selbstständige Näherinnen zu berechnen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1lsca4k/best_pos_system_for_alterationstailoring_business/)).
4. **Drei Prozesse:** Annahme und Ticket; Zuordnung zur Näherin; wöchentliche Vergütungsabrechnung. Nur diese Prozesskerne sind belegt.
5. **Hauptprozess:** Kleidungsstück → manuelles Ticket → Bearbeitung/Näherin → Ticketsammlung → Tabellenübertragung → Vergütungsberechnung. Übergabe- und Abholschritte bleiben offen.
6. **Informationsfluss:** Kunde/Kleidungsstück → Ticket (Auftragsdaten); Ticket → Näherin (Arbeitsauftrag); Ticketsammlung → Tabelle (Abrechnung). Besitzer des führenden Datensatzes ist ungeklärt.
7. **Hilfsmittel:** Papier-/manuelle Tickets und Tabelle belegt; Etikettierung am Kleidungsstück, POS und Gerätebestand unbekannt.
8. **Reifegrad:** 1/5, expert-derived: digitaler Abrechnungsschritt, aber primärer Auftrag analog.
9. **Physische Ordnung:** Eindeutige Verbindung aus Kleidungsstück, Auftrag, Näherin und Abholung ist erforderlich; aktuelle Kennzeichnung ist nicht belegt.
10. **Digitalisierungsreibung:** Erfassung darf die schnelle Annahme nicht verlängern; Bediengerät und Akzeptanz der Näherinnen sind offen.
11. **Kernengpass:** Doppelte Medienführung zwischen Ticket und Tabelle sowie zeitversetzte Vergütungsdaten.
12. **Fehlende Informationen:** Ticketfelder, Auftragsstatus, Ablageorte, Verwechslungen, Preisänderungen, Kundenbenachrichtigung, Geräte.
13. **Top-3-Fragen:** Wie bleibt Ticket am Kleidungsstück? Wer ändert Status und Preis? Welche Felder braucht die Vergütung zwingend?
14. **Verbesserungstreppe A–E:** A Pflichtfelder/Status definieren; B eindeutige ID erfassen; C gemeinsames Auftragsboard; D Vergütungsentwurf aus abgeschlossenen Tickets; E KI nur für Freitextklassifikation.
15. **Drei Chancen:** 1) Objekt-Auftrag-Verknüpfung, 2) Statussichtbarkeit, 3) vorbereitete Abrechnung.
16. **Kleinste Verbesserung:** Fortlaufende Auftrags-ID auf Ticket und Kleidungsanhänger plus einheitliche Pflichtfelder.
17. **As-Is:** `Kleidungsstück → manuelles Ticket → Näherin → Ticketsammlung → Tabelle`.
18. **Nächstes To-Be:** `ID-Ticket + Anhänger → Statusliste → Abschlussfreigabe → Abrechnungsentwurf`.
19. **Guardrails:** Preis, Leistungsumfang und Auszahlung nur nach menschlicher Prüfung; keine Kundendaten aus Vergleichsfällen übernehmen.
20. **Quellen:** Reddit-Beitrag wie oben; keine zweite betriebsbezogene Quelle gefunden.

## RB02-C02 – Fahrradwerkstatt mit Papieraufträgen

1. **Kurzprofil:** Fahrradwerkstatt mit Reparaturannahme und Sortierung nach Bearbeitungsstufen.
2. **Quellenlage/Vertrauen:** Mittel; direkte Werkstattaussage, wenige Details.
3. **Belegte Ausgangssituation:** Reparaturtickets sind aus Papier; ein Sortiersystem bildet Prozessstufen ab, wird aber als unübersichtlich beschrieben ([Quelle](https://www.reddit.com/r/BikeMechanics/comments/13tkbe7/bike_shop_service_writing_program/)).
4. **Drei Prozesse:** Reparaturannahme, physische Stufensortierung, Werkstattsteuerung; Teilebeschaffung ist nicht belegt.
5. **Hauptprozess:** Fahrrad und Ticket werden angenommen, danach anhand des Sortiersystems durch Werkstattstufen geführt. Wie Ticket und Rad verbunden bleiben, ist offen.
6. **Informationsfluss:** Kunde → Ticket; Ticket/Sortierort → Mechaniker; Mechaniker → nächster Sortierstatus. Kundenupdates und Abschlussdaten unbekannt.
7. **Hilfsmittel:** Papierkarten und physische Sortierung; vorhandene Geräte/Software nicht genannt.
8. **Reifegrad:** 0–1/5, expert-derived.
9. **Physische Ordnung:** Rad, Zubehör und Ticket brauchen eine dauerhafte ID; Stellplatz kann selbst Statusinformation tragen.
10. **Digitalisierungsreibung:** Schmutzige Hände, Werkstattbewegung und fehlender PC am Rad sind plausible Bedingungen, aber nicht belegt und zu erfragen.
11. **Kernengpass:** Status wird über Papier und Ablageposition repräsentiert; die Quelle nennt das System unübersichtlich.
12. **Fehlende Informationen:** Ticketverlust, Stellplätze, Zusatzarbeiten, Teilewartezeiten, Abholung, Anzahl Mechaniker.
13. **Top-3-Fragen:** Bleibt das Ticket am Rad? Welche Stufen gibt es? Wer darf Zusatzarbeiten/Preisänderungen freigeben?
14. **Verbesserungstreppe:** A Stufen und Kartenformat; B ID + kurzer Statusscan; C Werkstattboard; D Benachrichtigungsentwurf; E KI für Notizstrukturierung.
15. **Chancen:** 1) eindeutige Rad-ID, 2) WIP-Übersicht, 3) transparente Wartegründe.
16. **Kleinste Verbesserung:** Wasserfester ID-Anhänger und nummerierte Stellzonen mit täglichem Abgleich.
17. **As-Is:** `Rad → Papierkarte → physische Sortierstufe → nächste Stufe`.
18. **To-Be:** `Rad-ID → definierte Zone + Statusscan → Freigabe → Abholbereit`.
19. **Guardrails:** Keine Reparatur- oder Sicherheitsfreigabe automatisieren; Zusatzkosten vom Menschen bestätigen.
20. **Quellen:** Reddit r/BikeMechanics; Anbieterbeschreibungen wurden nicht als Ist-Beleg verwendet.

## RB02-C03 – Kleine Handyreparatur mit Zehnerteam

1. **Kurzprofil:** Kleiner Handyreparaturbetrieb mit zehn Teammitgliedern.
2. **Quellenlage/Vertrauen:** Mittel; direkte, aber sehr kurze Anfrage.
3. **Ausgangssituation:** Reparaturtracking und Belegdruck werden als Hauptanliegen genannt; Budgetgrenze 40 USD/Monat ([Quelle](https://www.reddit.com/r/smallbusiness/comments/eojjme/where_can_i_get_an_economical_pos_system_for_my/)).
4. **Drei Prozesse:** Geräteannahme, Reparaturstatus, Belegausgabe; konkrete Ist-Schritte fehlen.
5. **Hauptprozess:** Sicher belegt ist nur, dass Reparaturen verfolgt und Belege gedruckt werden müssen; aktueller Träger des Status ist unbekannt.
6. **Informationsfluss:** Kunde/Gerät → Reparaturauftrag → Team → Abschluss/Beleg; Felder, Übergaben und Speicherorte offen.
7. **Hilfsmittel:** Keine aktuelle Lösung belegt; Wunsch nach wirtschaftlichem POS.
8. **Reifegrad:** Nicht belastbar bewertbar; vorläufig 1/5 als Hypothese, nicht als Fakt.
9. **Physische Ordnung:** Gerät, Zubehör und Auftrag müssen eindeutig verbunden sein; aktuelle Methode unbekannt.
10. **Digitalisierungsreibung:** Geringes Budget und zehn Nutzende; Gerätezugang, Rollen und Schulung offen.
11. **Kernengpass:** Fehlende oder unzureichende Reparaturverfolgung, direkt berichtet.
12. **Fehlende Informationen:** Seriennummern, Zubehör, Diagnose, Teile, Status, Übergabe, Datenschutz, Kassenanforderungen.
13. **Top-3-Fragen:** Wie wird ein Gerät heute markiert? Welche Status brauchen alle zehn Personen? Was muss der Beleg enthalten?
14. **Verbesserungstreppe:** A Annahmecheckliste; B Auftrags-ID; C Rollen-/Statusboard; D Belegentwurf; E KI erst für Notiznormalisierung.
15. **Chancen:** 1) Geräteidentität, 2) Teamstatus, 3) konsistente Belege.
16. **Kleinste Verbesserung:** Nummerierter Gerätebeutel/Anhänger plus standardisiertes Annahmeformular.
17. **As-Is:** `Gerät → unbekannte Annahme → unzureichendes Tracking → Belegbedarf`.
18. **To-Be:** `ID + Zubehörcheck → Statusliste → Qualitätsfreigabe → Belegdruck`.
19. **Guardrails:** Keine Datenlöschung, Reparaturentscheidung oder Herausgabe ohne menschliche Prüfung; sensible Gerätedaten minimieren.
20. **Quellen:** Reddit-Beitrag; keine zweite fallbezogene Quelle.

## RB02-C04 – Reparaturbetrieb vor Wechsel von Garage zu Laden

1. **Kurzprofil:** Computer-/Handyreparatur und kundenspezifische PCs; Übergang vom Garagenbetrieb zum Ladenlokal.
2. **Quellenlage/Vertrauen:** Mittel; direkte Selbstauskunft.
3. **Ausgangssituation:** Rechnungen laufen über Billdu, Zahlungen über Bargeld und E-Transfer; mit dem Laden sollen Zubehörverkauf, Reparatur und POS/Inventar zusammenkommen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1ji66vh/expanding_from_garage_to_storefront_advice_needed/)).
4. **Drei Prozesse:** Reparaturannahme, Custom-PC-Auftrag, Zubehörverkauf/Bestand.
5. **Hauptprozess:** Der bestehende Rechnungs-/Zahlungsfluss ist benannt; die Reparaturstatusführung selbst wird nicht erklärt. Der Umzug erhöht Zahl und Art der Geschäftsobjekte.
6. **Informationsfluss:** Kunde → Rechnung; Zahlung → Bargeld/E-Transfer; geplanter Laden → Verkauf und Bestand. Abgleich zwischen Zahlung, Auftrag und Bestand offen.
7. **Hilfsmittel:** Billdu, Bargeld, E-Transfer belegt; zukünftiges POS nur Wunsch.
8. **Reifegrad:** 2/5, expert-derived: digitale Rechnungen, aber fragmentierte operative Daten.
9. **Physische Ordnung:** Reparaturgeräte, PC-Komponenten und Verkaufsware benötigen getrennte IDs/Lagerlogik.
10. **Digitalisierungsreibung:** Migration während Standortwechsel; Prozessdesign vor Toolwahl.
11. **Kernengpass:** Kommende Komplexität aus Reparatur, Build-to-order, Retail und mehreren Zahlungswegen.
12. **Fehlende Informationen:** Status, Seriennummern, Teileentnahme, Retouren, Kassenpflichten, Rollen.
13. **Top-3-Fragen:** Welche Objekte werden einzeln verfolgt? Wann wird Bestand reserviert? Wie wird Zahlung einem Auftrag zugeordnet?
14. **Verbesserungstreppe:** A Objektarten/IDs; B zentrale Auftragsliste; C Bestand und Auftrag verbinden; D Abgleichsentwürfe; E KI für Intake-Freitext.
15. **Chancen:** 1) Standortwechsel als Standardisierungsfenster, 2) Komponentenreservierung, 3) Zahlung-Auftrag-Abgleich.
16. **Kleinste Verbesserung:** Ein gemeinsames Nummernschema für Reparatur, Custom Build und Rechnung.
17. **As-Is:** `Kunde → Rechnung/Billdu → Bargeld oder E-Transfer; Reparaturstatus unbekannt`.
18. **To-Be:** `Auftrags-ID → Objekt/Teile → Status → Zahlungsabgleich → Ausgabe`.
19. **Guardrails:** Keine Bestands- oder Zahlungsbuchung ohne Nachweis; Standortwechsel nicht mit Vollmigration überladen.
20. **Quellen:** Reddit-Beitrag wie oben.

## RB02-C05 – Vermietung von Veranstaltungsausstattung

1. **Kurzprofil:** Kleiner Vermieter, der Veranstaltungsgegenstände teils liefert und aufbaut.
2. **Quellenlage/Vertrauen:** Hoch; detaillierte direkte Anforderungen und reale Statusbegriffe.
3. **Ausgangssituation:** Der Betrieb möchte Standort, Verfügbarkeit, Historie, Fotos/Beschreibung, Schäden und Status wie gepackt, vor Ort, schmutzig, geprüft und bereit verfolgen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1is84o5/software_for_rental_equipment_tracking_and/)).
4. **Drei Prozesse:** Reservierung/Verfügbarkeit, Kommissionierung/Lieferung, Rücknahme/Schadens- und Reinigungsprüfung.
5. **Hauptprozess:** Reservierung → Packen → Transport/Ort → Rücklauf → schmutzig → geprüft → bereit. Die Quelle liefert Statusbedarf, nicht den aktuellen Datenträger.
6. **Informationsfluss:** Auftrag → benötigte Objekte; Lager → Packstatus; Veranstaltung → Standort; Rücknahme → Schaden/Reinigung; Prüfung → Verfügbarkeit.
7. **Hilfsmittel:** Aktuelles System nicht genannt; Fotos und Statusfelder sind gewünschte Daten.
8. **Reifegrad:** Nicht sicher; 1–2/5 als Diagnosehypothese.
9. **Physische Ordnung:** Jedes identifizierbare Objekt oder Set braucht ID, Lagerplatz und Status; Verbrauchsmaterial muss getrennt werden.
10. **Digitalisierungsreibung:** Scans müssen an Lager, Fahrzeug und Veranstaltungsort funktionieren; Offlinebedarf ungeklärt.
11. **Kernengpass:** Verfügbarkeit ist ohne aktuellen Ort, Zustand und Rücklaufstatus nicht zuverlässig.
12. **Fehlende Informationen:** Einzel-ID versus Mengenartikel, aktuelle Listen, Verantwortliche, Offline, Schadensfreigabe, Packkontrolle.
13. **Top-3-Fragen:** Welche Artikel einzeln verfolgen? Wer ändert welchen Status? Wann gilt ein Rückläufer wieder als verfügbar?
14. **Verbesserungstreppe:** A Status/Lagerorte; B IDs und Packliste; C Reservierungs-/Rücklaufboard; D Konfliktwarnungen; E KI für Schadensnotizen, nie Schadensentscheidung.
15. **Chancen:** 1) Objektstandort, 2) Verfügbarkeitslogik, 3) Rücknahmequalität.
16. **Kleinste Verbesserung:** Feste Statusdefinitionen plus Rücknahmecheckliste für die wichtigsten Einzelobjekte.
17. **As-Is:** `Reservierung → Packen → Einsatz → Rücklauf; Ort/Zustand schwer sichtbar`.
18. **To-Be:** `Reservierung → ID-Packscan → Einsatzort → Rücknahmescan → Prüfung → bereit`.
19. **Guardrails:** Schaden, Ersatzforderung und Verfügbarkeit nach Prüfung durch Mitarbeitende; keine automatische Kundenschuldzuweisung.
20. **Quellen:** Reddit-Beitrag; Anbieterquellen ausgeschlossen.

## RB02-C06 – Stoffladen mit Altsoftware und Mengenbruchteilen

1. **Kurzprofil:** Kleiner Stoffhandel mit Retail, Arbeitsaufträgen und geplantem/verbundenem Onlinehandel.
2. **Quellenlage/Vertrauen:** Hoch; direkte, konkrete System- und Datenanforderungen.
3. **Ausgangssituation:** QuickBooks 9.0; Bestände werden in Yard-Bruchteilen geführt; Kundschafts-/Lieferantendaten sollen migriert und Verkauf, Arbeitsaufträge sowie E-Commerce unterstützt werden ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1llafnv/best_pos_for_fabric_store/)).
4. **Drei Prozesse:** Zuschnitt/Verkauf, Arbeitsauftrag, Bestands- und Datenmigration.
5. **Hauptprozess:** Stoffrolle/Bestand → Verkauf in Bruchteilen → Restmenge; parallele Arbeitsaufträge und Onlineverkäufe erhöhen Reservierungsbedarf.
6. **Informationsfluss:** Artikel/Rolle → Mengenbestand; Verkauf → Mengenabgang; Arbeitsauftrag → reservierte Menge; Altsoftware → Migration.
7. **Hilfsmittel:** QuickBooks 9.0 belegt; gewünschtes POS/E-Commerce noch nicht Ist.
8. **Reifegrad:** 2/5, expert-derived: digitaler Altbestand, aber fehlende geeignete Mengenlogik.
9. **Physische Ordnung:** Rolle, Partie/Farbe und Restlänge müssen mit Systembestand übereinstimmen.
10. **Digitalisierungsreibung:** Bruchteile, Zuschnitt und Alt-Datenmigration; Preisempfindlichkeit wird berichtet.
11. **Kernengpass:** Standard-Retaillogik bildet variable Zuschnittmengen und Arbeitsaufträge unzureichend ab.
12. **Fehlende Informationen:** Messmethode, Reststücke, Retouren, Reservierung, Barcodefähigkeit, Geräte.
13. **Top-3-Fragen:** Wird pro Rolle oder Artikel geführt? Wann wird Länge abgebucht? Wie werden Reststücke behandelt?
14. **Verbesserungstreppe:** A Mengeneinheiten/Regeln; B Rollen-ID; C Verkauf/Reservierung verbinden; D Niedrigbestandswarnung; E KI nur für Produktdatenhilfe.
15. **Chancen:** 1) Rollenbestand, 2) Reservierung, 3) sichere Migration.
16. **Kleinste Verbesserung:** Ein Pilot mit zehn Rollen: Anfangslänge, Zuschnitt, Rest und Verantwortlicher.
17. **As-Is:** `Altbestand → Zuschnitt/Verkauf → manuell problematische Restmenge`.
18. **To-Be:** `Rollen-ID → gemessener Zuschnitt → bestätigter Abgang → Restbestand`.
19. **Guardrails:** Migration mit Stichproben; keine automatische Bestandskorrektur oder Bestellung ohne Freigabe.
20. **Quellen:** Reddit-Beitrag.

## RB02-C07 – Boutique ohne SKU- und Scanroutine

1. **Kurzprofil:** Neu startende Boutique mit Clover Mini, aber ohne etabliertes Inventarsystem.
2. **Quellenlage/Vertrauen:** Mittel; direkte Selbstauskunft zum Einrichtungsproblem.
3. **Ausgangssituation:** Die Inhaberin möchte Google Sheets nutzen, weiß aber nicht, wie eigene SKUs, Etiketten und Scanwirkung aufzusetzen sind; Clover ist gekauft, aber noch nicht eingerichtet ([Quelle](https://www.reddit.com/r/smallbusiness/comments/iw7gwt/track_inventorycreate_and_use_skus/)).
4. **Drei Prozesse:** Artikelanlage, Etikettierung/Scan, Verkauf/Bestandsabgang.
5. **Hauptprozess:** Noch kein stabiler Ist-Prozess; das Problem liegt vor der Automatisierung in Datenmodell und Arbeitsregel.
6. **Informationsfluss:** Ware → Artikelstamm/SKU → Etikett → Scan → Verkauf → Bestand; heute nicht durchgängig eingerichtet.
7. **Hilfsmittel:** Gewünschte Google Sheets, vorhandener Clover Mini; Nutzung noch nicht belegt.
8. **Reifegrad:** 1/5, expert-derived.
9. **Physische Ordnung:** Jede verkaufbare Variante benötigt eindeutige Identifikation und Etikett; Bündel/Einzelstücke offen.
10. **Digitalisierungsreibung:** Fehlendes Grundwissen und Gefahr eines zu komplexen SKU-Schemas.
11. **Kernengpass:** Kein vereinbartes Artikel- und Identifikationsmodell.
12. **Fehlende Informationen:** Sortiment, Varianten, Lieferantencodes, Retouren, Inventur, Etikettendruck.
13. **Top-3-Fragen:** Welche Varianten ändern Preis/Bestand? Existieren Herstellerbarcodes? Wer legt neue Artikel an?
14. **Verbesserungstreppe:** A Artikelregeln; B Minimalstamm; C Verkauf-Abgang; D Inventurdifferenz-Review; E KI für Beschreibungsvorschläge.
15. **Chancen:** 1) saubere Stammdaten, 2) schneller Scan, 3) einfache Inventur.
16. **Kleinste Verbesserung:** 20-Artikel-Pilot mit fünf Pflichtfeldern und Testverkauf.
17. **As-Is:** `Ware → uneinheitliche/fehlende ID → Bestand unklar`.
18. **To-Be:** `Artikelregel → SKU/Barcode → Verkaufsscan → bestätigter Bestand`.
19. **Guardrails:** Keine SKU-Automatik ohne Dublettenprüfung; Bestand nicht aus ungeprüften Importen überschreiben.
20. **Quellen:** Reddit-Beitrag.

## RB02-C08 – Individuelle Textilproduktion mit WIP

1. **Kurzprofil:** Kleiner Hersteller individueller Kleidung für Künstler, Firmen, eigene Designs, E-Commerce und Events.
2. **Quellenlage/Vertrauen:** Hoch; detaillierte direkte Prozessbeschreibung.
3. **Ausgangssituation:** Rohlinge werden zu kundenspezifischen Produkten; made-to-order Shopify-Verkäufe sollen Komponenten verbrauchen; Einzelstücke brauchen Barcode/SKU; Zwischenstufen wie Tie-Dye vor Stickerei müssen verfolgt werden ([Quelle](https://www.reddit.com/r/smallbusiness/comments/18xyvaf/erp_or_inventory_management_for_custom_apparel/)).
4. **Drei Prozesse:** Auftrag/Variante, Komponentenverbrauch, Veredelungs-WIP.
5. **Hauptprozess:** Rohling → Reservierung → erste Veredelung → Zwischenbestand/WIP → weitere Veredelung → fertiges Einzelstück → Kanalverkauf.
6. **Informationsfluss:** Shopify/Event/Bulkauftrag → Variante; Stückliste → Rohling; Werkstatt → WIP-Status; Abschluss → Fertigbestand/Versand.
7. **Hilfsmittel:** Shopify belegt; gesuchte ERP-/Inventarlösung noch nicht Ist.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Rohlinge nach Variante, WIP-Behälter/Arbeitsplatz und fertige Einzelstücke brauchen unterscheidbare IDs.
10. **Digitalisierungsreibung:** Viele Varianten, seltene Einzelstücke und niedrige Zahlungsbereitschaft für komplexe Systeme.
11. **Kernengpass:** Ein Artikel verändert Identität und Wert über mehrere Arbeitsschritte; einfacher Zu-/Abgang reicht nicht.
12. **Fehlende Informationen:** Losgröße, Ausschuss, Nacharbeit, Arbeitsplatzgeräte, Prioritätsregel, Qualitätsfreigabe.
13. **Top-3-Fragen:** Wann wird Material reserviert/verbraucht? Welche WIP-Stufen sind entscheidend? Wird Einzel- oder Los-ID benötigt?
14. **Verbesserungstreppe:** A Varianten/Stufen; B WIP-Karte; C Auftrag-Komponente-Status; D Verbrauchsvorschlag; E KI für Freitextmapping.
15. **Chancen:** 1) WIP-Sichtbarkeit, 2) Komponentenbedarf, 3) Kanalübergreifende Priorität.
16. **Kleinste Verbesserung:** Drei definierte WIP-Zonen plus Auftragskarte mit Variante und nächstem Schritt.
17. **As-Is:** `Auftrag → Rohling → mehrere Veredelungen; Identität/Verbrauch schwer zusammenzuführen`.
18. **To-Be:** `Auftrags-ID → Komponentenreservierung → WIP-Scan je Stufe → Qualitätsfreigabe`.
19. **Guardrails:** Ausschuss, Nacharbeit und Freigabe menschlich; keine Materialbestellung ohne geprüften Bedarf.
20. **Quellen:** Reddit-Beitrag.

## RB02-C09 – Kleinstproduktion fermentierter Lebensmittel

1. **Kurzprofil:** Sehr kleiner Hersteller fermentierter Saucen und gepökelter Fleischprodukte.
2. **Quellenlage/Vertrauen:** Hoch; direkte Beschreibung der Produktionsdokumentation.
3. **Ausgangssituation:** Jeder Produktionsschritt wird detailliert protokolliert; Google Sheets dient als System, dieselben Daten sollen unterschiedlich dargestellt werden ([Quelle](https://www.reddit.com/r/smallbusiness/comments/r0e6ov/software_for_tracking_small_business_workflow/)).
4. **Drei Prozesse:** Chargenstart, Schrittprotokoll, Auswertung/Ansicht.
5. **Hauptprozess:** Charge → wiederholte Prozessschritte/Messungen → Protokoll in Sheets → Auswertung. Konkrete Messfelder werden nicht genannt.
6. **Informationsfluss:** Physische Charge → Mitarbeitereingabe → Zeile/Zelle → alternative Auswertungsansicht.
7. **Hilfsmittel:** Google Sheets belegt; Geräte, Papierhilfen und Sensoren unbekannt.
8. **Reifegrad:** 2/5, expert-derived: Daten existieren, Struktur/Ansichten begrenzen Nutzung.
9. **Physische Ordnung:** Chargen-/Behälter-ID muss mit Logeinträgen verbunden sein; aktuelles Labeling offen.
10. **Digitalisierungsreibung:** Erfassung während hygienischer/handwerklicher Arbeit; Bedienbarkeit am Produktionsort ist zu prüfen.
11. **Kernengpass:** Prozessdaten sind vorhanden, aber Darstellung und workflowgerechte Nutzung reichen nicht.
12. **Fehlende Informationen:** Pflichtmessungen, Verantwortliche, Korrekturen, Rückverfolgbarkeit, Offline, Geräte.
13. **Top-3-Fragen:** Wie wird Charge markiert? Welche Eingabe entsteht an welchem Schritt? Welche Ansicht braucht wer für welche Entscheidung?
14. **Verbesserungstreppe:** A Feld-/Schrittstandard; B mobile Eingabemaske; C Chargenstatus; D Erinnerungs-/Plausibilitätsentwurf; E KI nur für Notizklassifikation.
15. **Chancen:** 1) Charge-Daten-Verknüpfung, 2) rollenbezogene Ansichten, 3) fehlende Einträge sichtbar machen.
16. **Kleinste Verbesserung:** Eine eindeutige Chargen-ID in jedem Sheet-Eintrag und am Behälter.
17. **As-Is:** `Charge → viele Schritte → Google-Sheet-Protokoll → mühsame Sicht`.
18. **To-Be:** `Chargen-ID → schrittbezogene Eingabe → Status/Ansicht → menschliche Freigabe`.
19. **Guardrails:** Keine Qualitäts-, Hygiene- oder Freigabeentscheidung durch KI; regulatorische Anforderungen separat prüfen.
20. **Quellen:** Reddit-Beitrag; keine externen Compliance-Aussagen abgeleitet.

## RB02-C10 – Kleiner Misch- und Abfüllbetrieb

1. **Kurzprofil:** Betrieb mischt Bulk-Zutaten zu Endprodukten.
2. **Quellenlage/Vertrauen:** Mittel; direkte Beschreibung, wenige Organisationsdetails.
3. **Ausgangssituation:** QuickBooks-Inventar wird als ungeeignet beschrieben; die Bestandsgenauigkeit lässt sich mit dem Wachstum nicht mehr aufrechterhalten ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1cc2yhw/inventory_tracking_for_small_business_dealing_in/)).
4. **Drei Prozesse:** Rohstoffeingang, Mischung/Umwandlung, Fertigwarenbestand.
5. **Hauptprozess:** Bulk-Zutat → Entnahme → Mischung → Endprodukt → Bestand; aktuelle Buchungszeitpunkte fehlen.
6. **Informationsfluss:** Liefermenge → Rohbestand; Produktionsrezept → Verbrauch; Produktionsabschluss → Fertigmenge.
7. **Hilfsmittel:** QuickBooks belegt; weitere Tabellen/Etiketten unbekannt.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Gebinde, Charge und verbleibende Menge brauchen eindeutige Zuordnung.
10. **Digitalisierungsreibung:** Wiegen/Messen, Teilgebinde und zeitversetzte Buchungen.
11. **Kernengpass:** Umwandlung von Bulk-Rohstoffen in Endprodukte wird im Bestand nicht ausreichend genau abgebildet.
12. **Fehlende Informationen:** Rezept/Stückliste, Ausschuss, Chargen, Waagen, Buchungsrolle, Inventur.
13. **Top-3-Fragen:** Wann wird Verbrauch gebucht? Wie werden Teilgebinde gemessen? Welche Abweichung ist operativ relevant?
14. **Verbesserungstreppe:** A Einheiten/Rezepte; B Gebinde-ID; C Produktionsbuchung; D Differenzwarnung; E KI für Notizzuordnung.
15. **Chancen:** 1) Einheitenklarheit, 2) Verbrauch je Lauf, 3) Abweichungsprüfung.
16. **Kleinste Verbesserung:** Ein Pilotprodukt mit standardisiertem Soll-/Ist-Verbrauch.
17. **As-Is:** `Bulk-Rohstoff → Mischung → Endprodukt; Bestandsgenauigkeit sinkt`.
18. **To-Be:** `Gebinde-ID → bestätigte Entnahme → Laufabschluss → Soll/Ist-Review`.
19. **Guardrails:** Keine automatische Rezept-, Freigabe- oder Bestandskorrektur; Messwerte menschlich bestätigen.
20. **Quellen:** Reddit-Beitrag.

## RB02-C11 – Getränkeunternehmen mit manueller Doppelpflege

1. **Kurzprofil:** Kleines Getränkeunternehmen mit Distributor und geplantem Shopify-Direktvertrieb.
2. **Quellenlage/Vertrauen:** Hoch; konkrete Systeme und Medienbrüche.
3. **Ausgangssituation:** QuickBooks Simple Start; Distributorrechnungen werden manuell eingegeben; der Tabellenbestand kostet Produktivität und Genauigkeit; Shopify-D2C würde weitere Erfassung erzeugen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1ojaq6t/beverage_company_accountinginventory_software/)).
4. **Drei Prozesse:** Distributorabrechnung, Bestandsführung, neuer D2C-Auftrag.
5. **Hauptprozess:** Distributorbeleg → manuelle Buchhaltung; physischer Bestand → manuelle Tabelle; zusätzlicher Kanal → drohende weitere Doppelpflege.
6. **Informationsfluss:** Distributor → Rechnung → QuickBooks; Lager → Tabelle; Shopify → noch offener Abgleich.
7. **Hilfsmittel:** QuickBooks Simple Start und Spreadsheet belegt; Shopify ist Zielzustand.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Lagerzählung und verkaufsfähige Einheiten müssen kanalübergreifend eindeutig sein.
10. **Digitalisierungsreibung:** Veränderung bei laufendem Vertrieb; Produkt-/Einheitenstammdaten und Importmöglichkeiten sind nicht belegt.
11. **Kernengpass:** Dieselben Mengen-/Finanzinformationen müssen in getrennten Systemen gepflegt werden.
12. **Fehlende Informationen:** SKU, Lagerorte, Retouren, Distributorformat, Buchungsfrequenz, Rollen.
13. **Top-3-Fragen:** Was ist führend für Bestand? Welche Dokumente sind strukturiert exportierbar? Wann gilt Distributorverkauf als Bestandsabgang?
14. **Verbesserungstreppe:** A Datenhoheit; B standardisierter Import; C Kanalabgleich; D Abweichungswarteschlange; E KI für Dokumentvorerfassung.
15. **Chancen:** 1) Doppelpflege senken, 2) Kanalbestand sichtbar, 3) Prüfwarteschlange statt Blindimport.
16. **Kleinste Verbesserung:** Wöchentlicher standardisierter Distributor-zu-Bestands-Abgleich mit Ausnahmeliste.
17. **As-Is:** `Distributor → manuelle QB-Eingabe; Lager → Tabelle; D2C geplant`.
18. **To-Be:** `Kanalbeleg → strukturierter Entwurf → Prüfung → Bestand/Buchhaltung`.
19. **Guardrails:** Keine Buchung oder Bestandskorrektur ohne Belegprüfung; Schnittstellen nicht unterstellen.
20. **Quellen:** Reddit-Beitrag.

## RB02-C12 – Kleine Lebensmittelentwicklung vollständig in Sheets

1. **Kurzprofil:** Kleiner Lebensmittelentwickler und -hersteller.
2. **Quellenlage/Vertrauen:** Mittel; direkte, knappe Selbstauskunft.
3. **Ausgangssituation:** Es gibt keine Fachsoftware; Beschaffung, Fertigung, Lieferanten- und Bestandsinteressen laufen über Google Sheets ([Quelle](https://www.reddit.com/r/smallbusiness/comments/z0v2az/inventory_management_software/)).
4. **Drei Prozesse:** Beschaffung, Fertigung/WIP, Lieferantenverwaltung.
5. **Hauptprozess:** Lieferantenbedarf → Einkauf → Eingang → Fertigung → Bestand; die Tabellenstruktur und Buchungszeitpunkte sind nicht beschrieben.
6. **Informationsfluss:** Lieferant → Sheet; Einkauf → Sheet; Produktion → Sheet; Bestand → Entscheidung. Verantwortliche unbekannt.
7. **Hilfsmittel:** Google Sheets belegt; keine Fachsoftware.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Rohstoff, Charge, Lagerort und WIP brauchen eindeutige Schlüssel; aktuelle Kennzeichnung offen.
10. **Digitalisierungsreibung:** Ein Spreadsheet kann lokale Sonderlogik enthalten; Migration vor Prozessklärung wäre riskant.
11. **Kernengpass:** Ein generisches Tabellenwerk soll mehrere Objektarten und Lebenszyklen tragen.
12. **Fehlende Informationen:** Anzahl Tabellen, Versionen, Formeln, Chargen, Freigaben, Geräte, Datenqualität.
13. **Top-3-Fragen:** Welche Tabelle ist führend? Wo entstehen Mehrfacheingaben? Welche physische ID verbindet Ware und Zeile?
14. **Verbesserungstreppe:** A Datenmodell/Owner; B gemeinsame IDs; C WIP-/Bestandsstatus; D Ausnahmehinweise; E KI für Dokumententwurf.
15. **Chancen:** 1) Tabelleninventur, 2) Objekt-ID, 3) klare Freigabepunkte.
16. **Kleinste Verbesserung:** Datenlandkarte aller Sheets mit Owner, Zweck, Quelle und Aktualisierungszeitpunkt.
17. **As-Is:** `Beschaffung/Produktion/Lieferanten → mehrere Sheet-Funktionen → begrenzte Übersicht`.
18. **To-Be:** `definierte Quelle → Objekt-ID → gemeinsamer Status → geprüfte Ausnahmen`.
19. **Guardrails:** Keine pauschale Systemmigration; Formeln und regulatorisch relevante Aufzeichnungen einzeln prüfen.
20. **Quellen:** Reddit-Beitrag.

## RB02-C13 – Essenslieferdienst mit WhatsApp-zu-Tabelle

1. **Kurzprofil:** Kleiner Essenslieferdienst mit WhatsApp-Bestellungen.
2. **Quellenlage/Vertrauen:** Mittel; direkte Selbstauskunft, aber Beitrag beschreibt zugleich die selbst gebaute Lösung und kann Eigenwerbung sein.
3. **Ausgangssituation:** Bestellungen wurden manuell aus WhatsApp in Tabellen kopiert; der Autor baute danach eine automatische Übertragung ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1pui7l0/built_a_whatsapp_order_automation_system/)).
4. **Drei Prozesse:** Nachrichteneingang, Bestellübertragung, Liefer-/Produktionsliste.
5. **Hauptprozess:** WhatsApp-Nachricht → manuelles Lesen/Interpretieren → Tabellenzeile → weitere Bearbeitung; nachgelagerte Schritte sind nicht belegt.
6. **Informationsfluss:** Kunde → Chat; Inhaber → Sheet; Sheet → Betrieb. Änderungen/Stornos bleiben offen.
7. **Hilfsmittel:** WhatsApp und Tabellen belegt; die Eigenbaulösung ist Ziel-/Nachzustand, kein neutral evaluierter Ist-Beleg.
8. **Reifegrad:** Vorher 1–2/5; expert-derived.
9. **Physische Ordnung:** Verbindung von Bestellzeile, zubereiteter Einheit und Lieferung ist nicht beschrieben.
10. **Digitalisierungsreibung:** Freitext, Nachträge und unvollständige Adressen; genaue Häufigkeit unbekannt.
11. **Kernengpass:** Manuelle Übertragung zwischen unstrukturiertem Chat und strukturierter Liste.
12. **Fehlende Informationen:** Volumen, Pflichtfelder, Zahlungen, Storno, Cut-off, Lieferroute, Geräte.
13. **Top-3-Fragen:** Welche Pflichtdaten fehlen häufig? Wie werden Änderungen erkannt? Wer bestätigt die endgültige Bestellung?
14. **Verbesserungstreppe:** A Bestellformat; B Bestellentwurf; C bestätigter Status; D regelbasierte Übertragung mit Ausnahmen; E KI-Extraktion nur mit Review.
15. **Chancen:** 1) Pflichtfelder, 2) Änderungsverfolgung, 3) bestätigte Produktionsliste.
16. **Kleinste Verbesserung:** Standardisierte Chatvorlage plus eindeutige Bestellnummer in jeder Bestätigung.
17. **As-Is:** `WhatsApp-Freitext → manuelles Kopieren → Tabelle`.
18. **To-Be:** `Nachricht → strukturierter Entwurf → menschliche Bestätigung → Auftragsliste`.
19. **Guardrails:** Keine Bestellung, Adresse oder Zahlungsstatus ungeprüft übernehmen; Änderungsnachrichten nicht überschreiben.
20. **Quellen:** Reddit-Beitrag; behauptete Lösungseffekte nicht übernommen.

## RB02-C14 – Chemikalienlager mit Sheet und separatem Fotohandy

1. **Kurzprofil:** Kleines Lager, das 25–30 Palettensendungen pro Woche versendet.
2. **Quellenlage/Vertrauen:** Hoch; detaillierte direkte Beschreibung.
3. **Ausgangssituation:** Jede Bestellung mit Produktmengen und Chargennummern wird manuell in Google Sheets aktualisiert; ein separates Telefon enthält Fotos der Kundenaufträge. Kunden melden teils Fehlmengen, die der Betreiber bestreitet ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1udj3wa/inventory_management_system/)).
4. **Drei Prozesse:** Kommissionierung, Chargendokumentation, Versandnachweis/Reklamationsklärung.
5. **Hauptprozess:** Auftrag → Entnahme nach Produkt/Charge → manuelle Sheet-Aktualisierung → Fotos auf separatem Handy → Versand → eventuelle Reklamation.
6. **Informationsfluss:** Lagerobjekt → Sheet; gepackte Palette → Foto; Foto → separates Gerät; Reklamation → manuelle Suche/Abgleich.
7. **Hilfsmittel:** Google Sheets und separates Fototelefon belegt.
8. **Reifegrad:** 2/5, expert-derived: digitale Daten, aber getrennte Belegketten.
9. **Physische Ordnung:** Auftrag, Palette, Produkt, Menge, Charge und Foto brauchen gemeinsame Versand-ID.
10. **Digitalisierungsreibung:** Erfassung am Lagerort, Handschuhe/Bewegung und Netzabdeckung sind zu erfragen; nicht belegt.
11. **Kernengpass:** Mengen-/Chargendaten und Fotobeweis liegen in getrennten Systemen und werden manuell gepflegt.
12. **Fehlende Informationen:** Waage/Scan, Packfreigabe, Fotozeitpunkt, Nutzer, Korrekturen, Aufbewahrung.
13. **Top-3-Fragen:** Welche ID steht auf Palette und Foto? Wer bestätigt Menge/Charge? Wie wird eine Reklamation heute rekonstruiert?
14. **Verbesserungstreppe:** A Versand-ID/Fotoregel; B Scan-/Fotoablage je Auftrag; C Packstatus; D Differenzwarteschlange; E KI für Dokumentzuordnung, nicht Schuldfrage.
15. **Chancen:** 1) Nachweiskette, 2) Chargenabgleich, 3) schnellere Rekonstruktion.
16. **Kleinste Verbesserung:** Versand-ID gut sichtbar ins erste Foto und in jede relevante Sheet-Zeile aufnehmen.
17. **As-Is:** `Auftrag → Sheet-Eingabe + Fotos auf Zweithandy → Versand → manuelle Suche`.
18. **To-Be:** `Versand-ID → Pack-/Chargencheck → verknüpfte Fotos → Freigabe → Versand`.
19. **Guardrails:** Keine automatische Haftungs- oder Manipulationsannahme; Versandfreigabe und Reklamationsentscheidung menschlich.
20. **Quellen:** Reddit-Beitrag.

## RB02-C15 – Hausgerätereparatur trotz Onlinebuchung am Telefon

1. **Kurzprofil:** Stark ausgelasteter Hausgerätereparaturdienst.
2. **Quellenlage/Vertrauen:** Hoch; direkte Aussage mit konkreter Alltagssituation.
3. **Ausgangssituation:** Automatisierte Onlinebuchung existiert, doch Kunden rufen weiterhin an; der Inhaber verbringt ungefähr eine Stunde pro Morgen am Telefon, viele Anfragen kann der Betrieb nicht bedienen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/nhsk6t/has_anybody_with_a_service_business_tried_not/)).
4. **Drei Prozesse:** Anfragequalifikation, Terminbuchung, Ablehnung/Weiterleitung nicht erfüllbarer Fälle.
5. **Hauptprozess:** Kunde wählt Telefon statt Onlinebuchung → Inhaber klärt Gerät/Problem/Ort → prüft Machbarkeit → bucht oder lehnt ab.
6. **Informationsfluss:** Kunde → Telefonwissen beim Inhaber → Kalender/Entscheidung; Gründe für Nichtannahme werden nicht beschrieben.
7. **Hilfsmittel:** Online-Scheduling und Telefon belegt; konkretes System unbekannt.
8. **Reifegrad:** 3/5, expert-derived: digitaler Buchungskanal, aber kritische Qualifikation bleibt personengebunden.
9. **Physische Ordnung:** Ersatzteile/Geräte sind für diesen Quellenfall nicht beschrieben.
10. **Digitalisierungsreibung:** Kundenpräferenz Telefon und variable Reparierbarkeit; ein reines Buchungsformular löst Qualifikation nicht.
11. **Kernengpass:** Nicht die Terminablage, sondern die vorgelagerte Machbarkeitsprüfung bindet den Inhaber.
12. **Fehlende Informationen:** Ablehnungsgründe, Postleitzahl, Gerätemarken, Fehlerkategorien, Eskalationen, Mitarbeitende.
13. **Top-3-Fragen:** Welche drei Angaben entscheiden Annahme? Welche Fälle müssen persönlich geklärt werden? Kann ein Rückruf statt Sofortgespräch genügen?
14. **Verbesserungstreppe:** A Annahmekriterien; B kurzer Intake; C qualifizierte Rückrufliste; D regelbasierte Vorfilterung; E KI-Zusammenfassung mit menschlicher Entscheidung.
15. **Chancen:** 1) Vorqualifikation, 2) Rückrufbündelung, 3) transparente Ablehnung.
16. **Kleinste Verbesserung:** Telefonleitfaden und identische Pflichtfelder im Onlineformular.
17. **As-Is:** `Anruf → Inhaber fragt → Machbarkeit im Kopf → Termin/Ablehnung`.
18. **To-Be:** `Anfrage → Pflichtdaten → qualifizierte Liste → menschliche Annahme → Termin`.
19. **Guardrails:** Keine Reparaturzusage oder Sicherheitsdiagnose automatisieren; Sonderfälle an Menschen.
20. **Quellen:** Reddit-Beitrag.

## RB02-C16 – Mobile Hundepflege mit Papierkalender

1. **Kurzprofil:** Mobile Hundepflege mit Fahrzeiten und räumlich begrenztem Servicegebiet.
2. **Quellenlage/Vertrauen:** Mittel; Bericht aus dem Umfeld der Betreiberin, verbunden mit Toolentwicklung.
3. **Ausgangssituation:** Standardbuchungstools bilden Reisezeit, Servicegebiet und entfernungssensitive Preis-/Terminlogik nicht ab; die Betreiberin nutzt weiter einen Papierkalender und verliert Onlinebuchungen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1n7xg7x/calendly_wasnt_built_for_mobile_service/)). Eine weitere Diskussion bestätigt variable Servicedauer und Verkehr als Planungsproblem, jedoch nicht denselben Betrieb ([Kontext](https://www.reddit.com/r/smallbusiness/comments/t3n1yv/small_business_advice_mobile_pet_grooming/)).
4. **Drei Prozesse:** Anfrage/Ort, Termin- und Routenplanung, Preis-/Leistungsabstimmung.
5. **Hauptprozess:** Kunde fragt an → Ort/Leistung müssen bewertet werden → Papierkalender → Fahrt und Pflege. Onlinekanal passt nicht zu den Randbedingungen.
6. **Informationsfluss:** Kunde → Anfragekanal; Adresse/Leistung → Betreiberin; Betreiberin → Papierkalender; Route → tägliche Durchführung.
7. **Hilfsmittel:** Papierkalender; Calendly/Acuity wurden ausprobiert, nicht als aktueller Kernprozess belegt.
8. **Reifegrad:** 1/5, expert-derived.
9. **Physische Ordnung:** Fahrzeug, Verbrauchsmaterial und Hundedaten nicht beschrieben.
10. **Digitalisierungsreibung:** Fahrzeit und variable Dauer machen freie Slots kontextabhängig; Smartphone-Nutzung ist zu erfragen.
11. **Kernengpass:** Kalenderkapazität kann ohne Geografie und Leistungsdauer nicht korrekt beurteilt werden.
12. **Fehlende Informationen:** Gebietsgrenzen, Dauerregeln, Puffer, Storno, Geräte, Offline, Wiederholtermine.
13. **Top-3-Fragen:** Welche Ortsdaten reichen zur Entscheidung? Wie wird Dauer geschätzt? Wer darf einen vorgeschlagenen Slot bestätigen?
14. **Verbesserungstreppe:** A Gebiete/Dauern; B Anfrageformular; C manueller Routenblick; D Slotvorschlag; E KI nur zur Anfragezusammenfassung.
15. **Chancen:** 1) qualifizierte Anfrage, 2) realistische Puffer, 3) weniger Kanalverlust.
16. **Kleinste Verbesserung:** Anfragevorlage mit Postleitzahl, Hund/Leistung und Wunschfenster; Bestätigung bleibt manuell.
17. **As-Is:** `Anfrage → Papierkalender → manuelle Orts-/Dauerprüfung`.
18. **To-Be:** `Pflichtdaten → Routensicht → menschlich bestätigter Slot → Kalender`.
19. **Guardrails:** Termin nicht ohne Kapazitäts-/Routenprüfung bestätigen; keine Gesundheits- oder Verhaltensentscheidung automatisieren.
20. **Quellen:** Zwei Reddit-Diskussionen; nur erste als Fallbeleg.

## RB02-C17 – Salon mit vier nicht verbundenen Systemen

1. **Kurzprofil:** Salon mit Front Desk, mehreren Mitarbeitenden, Anzahlungen, Memberships und Kundennotizen.
2. **Quellenlage/Vertrauen:** Hoch; direkte, detaillierte System- und Übergabebeschreibung.
3. **Ausgangssituation:** Acuity für Buchung, Square für POS/Membership, HubSpot plus Google Docs für Notizen. Eine in Acuity gezahlte Anzahlung ist in Square nicht sichtbar; Front Desk prüft manuell. Notizen liegen über Tabs/Apps verteilt ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1k6clsc/best_salon_software_for_booking_scheduling_pos/)).
4. **Drei Prozesse:** Buchung/Anzahlung, Behandlung/Kundennotiz, Restzahlung.
5. **Hauptprozess:** Buchung in Acuity → Anzahlung → Termin → Notizen in separaten Systemen → Front Desk prüft Anzahlung → Restzahlung in Square.
6. **Informationsfluss:** Kunde → Acuity; Zahlungsteil → Acuity; Profil/Notiz → HubSpot/Docs; Front Desk → manueller Abgleich; Restzahlung → Square.
7. **Hilfsmittel:** Acuity, Square, HubSpot, Google Docs belegt.
8. **Reifegrad:** 3/5, expert-derived: viele digitale Funktionen, aber kein gemeinsamer Fall-/Kundendatensatz.
9. **Physische Ordnung:** Räume/Geräte sind als Ressourcen relevant, aber aktueller Umgang nicht belegt.
10. **Digitalisierungsreibung:** Datenmigration, Mitarbeiterschulung und unklare Datenhoheit; nicht jede Funktion rechtfertigt Systemwechsel.
11. **Kernengpass:** Zahlungs- und Kundenkontext ist über Anwendungen fragmentiert.
12. **Fehlende Informationen:** Volumen, Dubletten, Datenschutzrollen, Export, Räume, Formeln, Ausfallprozess.
13. **Top-3-Fragen:** Welche Ansicht braucht der Front Desk? Welche ID verbindet Buchung und Zahlung? Welche Notizen sind für wen erforderlich?
14. **Verbesserungstreppe:** A führende Systeme; B Abgleichfeld; C gemeinsame Tagesansicht; D Ausnahmehinweise; E KI für Notizzusammenfassung nur rollenbasiert.
15. **Chancen:** 1) Anzahlung-Restbetrag, 2) profilbezogene Notizen, 3) Tageskapazität.
16. **Kleinste Verbesserung:** Einheitliche Termin-/Kunden-ID und tägliche Ausnahmeliste für Anzahlungsabweichungen.
17. **As-Is:** `Acuity + Square + HubSpot/Docs → Front-Desk-Abgleich`.
18. **To-Be:** `Buchungs-ID → Zahlungs-/Notizsicht → Ausnahmeprüfung → Abschluss`.
19. **Guardrails:** Keine Behandlung, Rückerstattung oder sensible Notizfreigabe automatisieren; Rollen-/Datenschutzprüfung.
20. **Quellen:** Reddit-Beitrag.

## RB02-C18 – Kleiner Friseursalon mit Papierterminbuch

1. **Kurzprofil:** Kleiner Friseursalon.
2. **Quellenlage/Vertrauen:** Niedrig; sehr kurzer Bericht eines extern Unterstützenden.
3. **Ausgangssituation:** Termine werden auf Papier geführt ([Quelle](https://www.reddit.com/r/smallbusiness/comments/4dn5e5/im_working_with_a_small_hair_salon_that_uses_a/)).
4. **Drei Prozesse:** Terminannahme, Kalendereintrag, Tagesdurchführung; nur Papierplanung ist belegt.
5. **Hauptprozess:** Anfrage → Papierkalender → Termin. Kanäle, Bestätigung und Personalzuordnung fehlen.
6. **Informationsfluss:** Kunde → unbekannter Kanal → Papierterminbuch → Salonteam.
7. **Hilfsmittel:** Papierterminbuch; sonst nichts belegt.
8. **Reifegrad:** 0–1/5, expert-derived und unsicher.
9. **Physische Ordnung:** Stuhl-/Mitarbeiter-/Raumressourcen nicht beschrieben.
10. **Digitalisierungsreibung:** Ein digitaler Prozess darf die schnelle Annahme am Telefon/Tresen nicht behindern; Nutzungskontext unbekannt.
11. **Kernengpass:** Nur analoger Kalender ist belegt; ein tatsächlicher Engpass wird nicht ausdrücklich berichtet.
12. **Fehlende Informationen:** Fast alle Volumen-, Kanal-, Ressourcen- und Fehlerdaten.
13. **Top-3-Fragen:** Wer schreibt ein? Gibt es Doppelbuchungen/Lesefehler? Welche Geräte stehen während der Annahme bereit?
14. **Verbesserungstreppe:** A Kalenderregeln; B strukturierter Eintrag; C gemeinsame Sicht; D Erinnerung; E KI derzeit nicht begründbar.
15. **Chancen:** Nur Hypothesen: 1) Lesbarkeit, 2) gemeinsame Sicht, 3) Änderungsverlauf.
16. **Kleinste Verbesserung:** Papierbuch zunächst mit einheitlichen Feldern und Änderungskennzeichnung standardisieren.
17. **As-Is:** `Anfrage → Papierterminbuch`.
18. **To-Be:** `Anfrage → standardisierter Eintrag → bestätigte Änderung`; digital erst nach Geräteprüfung.
19. **Guardrails:** Keine automatische Terminbestätigung; niedrige Evidenz nicht als Problemnachweis verwenden.
20. **Quellen:** Ein kurzer Reddit-Beitrag.

## RB02-C19 – Einzelplatz-Spa mit Papier und WhatsApp

1. **Kurzprofil:** Spa mit nur einem Behandlungsplatz.
2. **Quellenlage/Vertrauen:** Niedrig; Zweitbericht eines Kunden, nicht der Betreiberin.
3. **Ausgangssituation:** Papierkalender und WhatsApp werden parallel genutzt; Doppelbuchungen werden berichtet, verfügbare Tools seien zu teuer oder überladen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1uckotf/hi_salon_owners_what_do_you_use_for_bookings_at/)).
4. **Drei Prozesse:** WhatsApp-Anfrage, Papiereintrag, Änderung/Doppelbuchung.
5. **Hauptprozess:** Chat → manueller Kalenderübertrag → Termin; parallele Nachrichten können den einzigen Platz kollidieren lassen.
6. **Informationsfluss:** Kunde → WhatsApp; Betreiberin → Papier; Papier → Tagesplan. Bestätigungsstatus unbekannt.
7. **Hilfsmittel:** WhatsApp und Papierkalender berichtet.
8. **Reifegrad:** 1/5, expert-derived.
9. **Physische Ordnung:** Ein Behandlungsplatz ist harte Kapazitätsgrenze.
10. **Digitalisierungsreibung:** Preis-/Komplexitätssensitivität und wahrscheinlich smartphonezentrierter Alltag; letzteres ist nicht belegt.
11. **Kernengpass:** Zwei Informationsorte ohne atomare Kapazitätsprüfung.
12. **Fehlende Informationen:** Zahl der Termine, Schreibberechtigte, Storno, Puffer, Gerät, Zahlungsprozess.
13. **Top-3-Fragen:** Wann gilt WhatsApp-Anfrage als bestätigt? Wer trägt ein? Welche minimale Monats-/Bedienlast ist akzeptabel?
14. **Verbesserungstreppe:** A Bestätigungsregel; B ein führender Kalender; C Änderungsstatus; D Erinnerungsentwurf; E KI nicht vorrangig.
15. **Chancen:** 1) Single source of truth, 2) Bestätigungsstatus, 3) Einfachheit.
16. **Kleinste Verbesserung:** In WhatsApp nie bestätigen, bevor der eine führende Kalender geprüft und eingetragen ist.
17. **As-Is:** `WhatsApp ↔ Papierkalender → mögliche Doppelbuchung`.
18. **To-Be:** `Anfrage → Kapazitätsprüfung → führender Eintrag → Bestätigung`.
19. **Guardrails:** Kein Slot ohne Prüfung; Zweitbericht vor Produktentscheidung durch Interview verifizieren.
20. **Quellen:** Reddit-Zweitbericht.

## RB02-C20 – Fahrschule mit vier Fahrlehrern und Abholorten

1. **Kurzprofil:** Übernommene Fahrschule mit vier Fahrlehrern; Unterricht sieben Tage pro Woche.
2. **Quellenlage/Vertrauen:** Hoch; direkte, konkrete Betriebsparameter.
3. **Ausgangssituation:** Fahrlehrer arbeiten an unterschiedlichen Tagen; Schüler werden zuhause oder an der Schule abgeholt; geerbtes DaySmart-System und Support werden als problematisch beschrieben ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1e6rxwd/alternative_to_daysmart/)).
4. **Drei Prozesse:** Fahrlehrer-Verfügbarkeit, Schülerbuchung, Abholort-/Fahrzeugplanung.
5. **Hauptprozess:** Schülerwunsch + Abholort → verfügbarer Fahrlehrer/Tag → Unterrichtsslot → Durchführung. Fahrzeugzuordnung ist nicht belegt.
6. **Informationsfluss:** Schüler → Termin/Ort; System → Fahrlehrerplan; Fahrlehrer → Durchführung. Änderungen/Leistungsnachweis offen.
7. **Hilfsmittel:** DaySmart als geerbtes System belegt.
8. **Reifegrad:** 3/5, expert-derived: Fachsoftware vorhanden, aber Passung/Support problematisch.
9. **Physische Ordnung:** Fahrlehrer, Fahrzeug und Abholort sind gekoppelte Ressourcen; Fahrzeugzahl unbekannt.
10. **Digitalisierungsreibung:** Migration eines laufenden Sieben-Tage-Plans; unterschiedliche Arbeitsmuster.
11. **Kernengpass:** Termin ist nur gültig, wenn Person, Zeit und Ort zusammenpassen; Systemunzufriedenheit erhöht Wechselrisiko.
12. **Fehlende Informationen:** Fahrzeuge, Lizenzen, Dauer, Puffer, Schülerfortschritt, Geräte, Offline.
13. **Top-3-Fragen:** Welche Ressource kollidiert am häufigsten? Wie werden Abholorte geprüft? Welche Daten müssen aus dem Altsystem erhalten bleiben?
14. **Verbesserungstreppe:** A Ressourcenregeln; B verlässliche Stammdaten; C kombinierte Planung; D Konfliktwarnung; E KI für Anfragezusammenfassung.
15. **Chancen:** 1) Mehrressourcenprüfung, 2) Migrationsklarheit, 3) mobile Tagesansicht.
16. **Kleinste Verbesserung:** Wöchentliche Ressourcenmatrix für Fahrlehrer, Tage und bekannte Abholzonen.
17. **As-Is:** `Schülerwunsch → DaySmart → manuelle Passungsprüfung/Supportproblem`.
18. **To-Be:** `Anfrage → Person+Ort+Zeit-Prüfung → Bestätigung → mobile Tagesliste`.
19. **Guardrails:** Keine Terminbestätigung ohne Ressourcenprüfung; regulatorische Ausbildungsentscheidungen menschlich.
20. **Quellen:** Reddit-Beitrag.

## RB02-C21 – Kampfsportschule mit manuellen Monatsbelastungen

1. **Kurzprofil:** Kampfsportschule in Übernahme/Modernisierung.
2. **Quellenlage/Vertrauen:** Mittel; direkte, kurze Selbstauskunft.
3. **Ausgangssituation:** Jeder Schüler wird monatlich manuell belastet; der Übernehmer sucht wiederkehrende Zahlungen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1kfxfme/taking_over_martial_arts_studio_looking_for/)).
4. **Drei Prozesse:** Mitgliedschaft, Monatsabrechnung, Zahlungsabweichung.
5. **Hauptprozess:** Mitgliederliste → monatliche Einzelbelastung → Zahlung/Fehler → manuelle Nacharbeit. Vertrags- und Anwesenheitslogik fehlt.
6. **Informationsfluss:** Mitgliedsdaten → Belastung; Zahlungsresultat → Betreiber; Abweichung → Nachfassen.
7. **Hilfsmittel:** Aktuelles Zahlungswerkzeug nicht genannt; wiederkehrende Zahlung ist Wunsch.
8. **Reifegrad:** 1–2/5, expert-derived.
9. **Physische Ordnung:** Kursraum-/Kapazität nicht belegt.
10. **Digitalisierungsreibung:** Übernahme erfordert korrekte Mitglieds-, Vertrags- und Zahlungsdaten; keine Blindmigration.
11. **Kernengpass:** Wiederkehrender Standardprozess wird pro Mitglied einzeln ausgeführt.
12. **Fehlende Informationen:** Anzahl Mitglieder, Tarife, Pausen, Kündigung, Einwilligung, Fehlzahlungen, Buchhaltung.
13. **Top-3-Fragen:** Welche Tarifvarianten existieren? Wer genehmigt Belastungen? Wie werden Pausen/Kündigungen abgebildet?
14. **Verbesserungstreppe:** A Vertrags-/Tarifregeln; B saubere Mitgliederliste; C Status je Abrechnungsperiode; D Belastungsentwurf; E KI nicht notwendig.
15. **Chancen:** 1) Stammdaten, 2) Ausnahmebehandlung, 3) nachvollziehbarer Monatslauf.
16. **Kleinste Verbesserung:** Monatsliste mit aktiv/pausiert/gekündigt und Vier-Augen-Freigabe vor Belastung.
17. **As-Is:** `Mitgliederliste → einzelne manuelle Monatsbelastung`.
18. **To-Be:** `geprüfter Status → Abrechnungslauf-Entwurf → Freigabe → Ausnahmen`.
19. **Guardrails:** Keine Belastung, Mahnung oder Vertragsänderung ohne Freigabe; Zahlungsdaten schützen.
20. **Quellen:** Reddit-Beitrag.

## RB02-C22 – Lokaler Nachhilfeanbieter mit zehn Tutoren

1. **Kurzprofil:** Rund 45 Kinder/Eltern pro Woche und zehn Tutoren.
2. **Quellenlage/Vertrauen:** Hoch; Inhaber beschreibt Wachstum und späteren Systemeinsatz.
3. **Ausgangssituation:** Terminierung, Kundenabrechnung und Tutorvergütung mussten koordiniert werden; später bündelte TutorCruncher diese Aufgaben, und monatliche Abrechnung reduzierte verspätete/fehlende Zahlungen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/aczvwy/growing_a_local_tutoring_business/)).
4. **Drei Prozesse:** Tutor-Schüler-Zuordnung, Leistungserfassung, Kundenabrechnung/Tutorzahlung.
5. **Hauptprozess:** Termin → Tutorleistung → Erfassung → Kundenrechnung → Tutorvergütung. Der genaue Vorher-Prozess ist nur teilweise rekonstruierbar.
6. **Informationsfluss:** Eltern/Schüler → Termin; Tutor → Leistungsdaten; System → Rechnung/Vergütung.
7. **Hilfsmittel:** TutorCruncher im späteren Zustand belegt; frühere Tools nicht vollständig genannt.
8. **Reifegrad:** Vorher unklar, später etwa 3/5; expert-derived.
9. **Physische Ordnung:** Räume/Materialien nicht beschrieben.
10. **Digitalisierungsreibung:** Zehn Tutoren müssen Leistung konsistent erfassen; mobile Geräte/Fristen offen.
11. **Kernengpass:** Eine erbrachte Einheit muss gleichzeitig Schüler, Tutor, Abrechnung und Vergütung zugeordnet werden.
12. **Fehlende Informationen:** Absagen, Nachweise, Korrekturen, Tarifvarianten, Datenschutz, aktuelle Probleme.
13. **Top-3-Fragen:** Was löst Rechnung und Honorar aus? Wer korrigiert eine Einheit? Wie werden No-shows behandelt?
14. **Verbesserungstreppe:** A Leistungsdefinition; B Einheit-ID; C Status; D Abrechnungsentwurf; E KI nur für Notizzusammenfassung.
15. **Chancen:** 1) einmalige Leistungserfassung, 2) Abrechnungsstatus, 3) Ausnahmebearbeitung.
16. **Kleinste Verbesserung:** Jede Einheit erhält Tutor, Schüler, Datum, Dauer und Freigabestatus.
17. **As-Is:** `Termin → Tutorleistung → getrennte Abrechnungs-/Vergütungsarbeit`.
18. **To-Be:** `Einheit-ID → Tutorbestätigung → Review → Rechnung + Honorarentwurf`.
19. **Guardrails:** Keine Zahlung oder Leistungsbewertung autonom; Daten Minderjähriger rollenbasiert schützen.
20. **Quellen:** Reddit-Beitrag; Lösung nicht als universelle Produktempfehlung behandelt.

## RB02-C23 – Solo-Routenbetrieb vor erster Einstellung

1. **Kurzprofil:** Kleiner mobiler Grundstücksreinigungsdienst vor Einstellung einer weiteren Person.
2. **Quellenlage/Vertrauen:** Mittel; direkte Frage mit konkreter Ist-Routenhilfe.
3. **Ausgangssituation:** Routen werden derzeit über MapQuest organisiert; der Betreiber fragt, wie Routen an Mitarbeitende gesendet und Fahrzeuge/Telefon geregelt werden sollen ([Quelle](https://www.reddit.com/r/smallbusiness/comments/r7qrri/how_do_i_hire_somebody_i_have_a_pooper_scooper/)).
4. **Drei Prozesse:** Routenplanung, Einsatzübergabe, Nachweis/Rückmeldung.
5. **Hauptprozess:** Kundenadressen → MapQuest-Route → Inhaber fährt; mit Einstellung entsteht Übergabe an Mitarbeiter. Nachweis ist nicht beschrieben.
6. **Informationsfluss:** Kundenliste → MapQuest; Route → bisher Inhaber, künftig Mitarbeiter; Rückmeldung → offen.
7. **Hilfsmittel:** MapQuest belegt; eigenes Fahrzeug/Telefon sind offene Entscheidungen.
8. **Reifegrad:** 1/5, expert-derived.
9. **Physische Ordnung:** Fahrzeug, Schlüssel/Zugang und Material sind mögliche Geschäftsobjekte, aber nicht belegt.
10. **Digitalisierungsreibung:** BYOD, Mobilfunk, Adressschutz und einfache Bedienung müssen vor Toolwahl geklärt werden.
11. **Kernengpass:** Personengebundene Route muss erstmals sicher an einen Mitarbeiter übergeben werden.
12. **Fehlende Informationen:** Kundenzahl, Frequenz, Zugangshinweise, Offline, Leistungsnachweis, Änderungen.
13. **Top-3-Fragen:** Welche Daten braucht der Mitarbeiter vor Ort? Wie meldet er erledigt/problematisch? Darf ein privates Telefon Kundendaten enthalten?
14. **Verbesserungstreppe:** A Routen-/Statusstandard; B Tagesliste; C Rückmeldestatus; D Routenentwurf; E KI nicht vorrangig.
15. **Chancen:** 1) klare Einsatzübergabe, 2) Datenschutz, 3) Erledigt-/Ausnahmefeedback.
16. **Kleinste Verbesserung:** Standardisierte Tagesroute mit minimalen Kundendaten und drei Rückmeldestatus.
17. **As-Is:** `Kundenadressen → MapQuest → Inhaberwissen`.
18. **To-Be:** `Tagesliste → Mitarbeiter → erledigt/Ausnahme → Review`.
19. **Guardrails:** Keine Arbeitgeberklassifikation, Überwachung oder Kundenzugangsfreigabe automatisieren; Rechtsfragen separat klären.
20. **Quellen:** Reddit-Beitrag.

## RB02-C24 – Hochzeits- und Event-DJ mit Adminlast

1. **Kurzprofil:** Kleines Hochzeits- und Event-DJ-Unternehmen.
2. **Quellenlage/Vertrauen:** Mittel; direkte, aber aggregierte Selbstauskunft.
3. **Ausgangssituation:** Verwaltung beansprucht mehr Zeit als Auftritte; genannt werden Anfragen, Nachfassen, Terminierung, Papierkram, Zahlungen und Kundenkommunikation ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1u3q2g0/what_takes_up_more_of_your_time_delivering_your/)).
4. **Drei Prozesse:** Lead/Angebot, Eventvorbereitung, Zahlung/Nachfassen.
5. **Hauptprozess:** Anfrage → Nachfassen → Termin/Vertrag/Papierkram → Zahlung → Eventkommunikation → Leistung. Konkrete Tools fehlen.
6. **Informationsfluss:** Kunde → Anfragen; Inhaber → Follow-up/Plan; Dokumente/Zahlung → Auftrag; Eventdetails → Durchführung.
7. **Hilfsmittel:** Papierkram wird genannt; digitale/analoge Werkzeuge unbekannt.
8. **Reifegrad:** Nicht belastbar, vorläufig 1–2/5.
9. **Physische Ordnung:** Technik-/Transportplanung ist plausibel, aber nicht belegt.
10. **Digitalisierungsreibung:** Stark individuelle Events; Standardisierung muss Kernfelder von kreativen Details trennen.
11. **Kernengpass:** Viele kleine Übergaben über den gesamten Kundenlebenszyklus liegen beim Inhaber.
12. **Fehlende Informationen:** Kanäle, Volumen, Vorlagen, Verträge, Equipment, Team, Zahlungsstatus.
13. **Top-3-Fragen:** Welche Information wird mehrfach angefragt? Welche Frist wird am häufigsten manuell verfolgt? Wo steht der aktuelle Auftragsstatus?
14. **Verbesserungstreppe:** A Event-Checkliste; B Auftragsakte; C Status/Fristen; D Erinnerungsentwürfe; E KI für Kommunikationsentwürfe.
15. **Chancen:** 1) ein Eventdatensatz, 2) Wiedervorlage, 3) Dokumentvollständigkeit.
16. **Kleinste Verbesserung:** Eine Eventakte mit Pflichtfeldern, nächster Aktion und Verantwortlichem.
17. **As-Is:** `Anfrage → Follow-ups/Papierkram/Zahlung/Kommunikation → Event`.
18. **To-Be:** `Event-ID → Checkliste + nächste Aktion → Freigaben → Durchführung`.
19. **Guardrails:** Keine vertragliche Zusage, Zahlungserinnerung oder Terminänderung autonom versenden.
20. **Quellen:** Reddit-Beitrag.

## RB02-C25 – Kunstmarkt-Verkäufer mit E-Transfer am Stand

1. **Kurzprofil:** Solo-Kunstverkäufer auf Wochenendmärkten in Kanada.
2. **Quellenlage/Vertrauen:** Hoch; direkte Beschreibung einer konkreten Verkaufssituation.
3. **Ausgangssituation:** Kunden tippen für E-Transfer E-Mail und Namen ein, während der Verkäufer gleichzeitig Ware verpackt; gesucht wird eine einfachere QR-gestützte Eingabe ([Quelle](https://www.reddit.com/r/smallbusiness/comments/14rwe4v/can_i_make_a_qr_code_to_make_etransfers_easier/)).
4. **Drei Prozesse:** Produktauswahl, Zahlungseingabe/Bestätigung, Verpackung/Übergabe.
5. **Hauptprozess:** Kunde wählt → Verkäufer verpackt → Kunde tippt Zahlungsdaten → Zahlung muss erkannt werden → Übergabe.
6. **Informationsfluss:** Verkäuferdaten → Kundentelefon; Betrag/Zahlung → Zahlungsdienst; Bestätigung → Verkäufer; Ware → Kunde.
7. **Hilfsmittel:** E-Transfer und Marktstand; weitere Kasse nicht belegt.
8. **Reifegrad:** 1–2/5, expert-derived.
9. **Physische Ordnung:** Ware und Zahlung müssen am schnellen Tresenmoment zugeordnet werden; aktuelle Artikel-IDs unbekannt.
10. **Digitalisierungsreibung:** Verkäuferhände sind mit Verpackung gebunden; Kundengeräte und Netzverbindung variieren.
11. **Kernengpass:** Zahlung erfordert manuelle Dateneingabe im Moment paralleler physischer Arbeit.
12. **Fehlende Informationen:** Verkaufsvolumen, Betragserfassung, Beleg, Inventar, Netzabdeckung, Rückerstattung.
13. **Top-3-Fragen:** Wie wird Zahlung bestätigt? Muss Artikelbestand sinken? Was passiert ohne Netz?
14. **Verbesserungstreppe:** A Zahlungs-/Übergaberegel; B statischer Kontakt-QR; C einfache Verkaufs-ID; D Abgleichsliste; E KI nicht erforderlich.
15. **Chancen:** 1) weniger Tipparbeit, 2) klare Zahlungsbestätigung, 3) Offline-Fallback.
16. **Kleinste Verbesserung:** QR nur für Empfängerdaten plus sichtbare Regel „Übergabe nach Bestätigung“; Betrag bleibt geprüft.
17. **As-Is:** `Ware wählen → Verkäufer verpackt || Kunde tippt Transferdaten → Bestätigung → Übergabe`.
18. **To-Be:** `Ware → QR-Kontakt → Betrag/Bestätigung → Übergabe + optionaler Verkaufsstrich`.
19. **Guardrails:** Keine Zahlungsbestätigung aus Screenshot oder Annahme ableiten; Rückerstattung menschlich.
20. **Quellen:** Reddit-Beitrag.

## RB02-C26 – Wachsender Schilderhersteller mit PDF-Aufträgen

1. **Kurzprofil:** Wachsender kleiner Schilderhersteller mit Projektsteuerung und Buchhaltung.
2. **Quellenlage/Vertrauen:** Hoch; direkte und detaillierte Beschreibung des Dokumenteneingangs.
3. **Ausgangssituation:** Aufträge und POs kommen als variierende, teils mehrseitige PDFs; Mitarbeitende prüfen sie und übertragen Daten manuell in Buchhaltung und Projektmanagement ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1iid94l/need_to_automate_data_extraction_from_orderpo/)).
4. **Drei Prozesse:** Dokumenteingang, Auftragsanlage, Buchhaltungs-/Projektübertragung.
5. **Hauptprozess:** PDF empfangen → Seiten prüfen → relevante Felder identifizieren → Daten in zwei Zielkontexte eingeben → Projekt fortführen.
6. **Informationsfluss:** Kunde → PDF; Mitarbeiter → Interpretation; PDF-Felder → Buchhaltung und Projektmanagement; Unklarheit → Rückfrage.
7. **Hilfsmittel:** PDF, Buchhaltungs- und Projektmanagementsystem belegt; konkrete Produkte nicht genannt.
8. **Reifegrad:** 2–3/5, expert-derived.
9. **Physische Ordnung:** Verbindung zu Material/Schilderobjekt ist wahrscheinlich, aber nicht beschrieben.
10. **Digitalisierungsreibung:** Layoutvarianz, Mehrseitigkeit, handschriftliche/gescannte Qualität möglich, aber nicht belegt; Feldkonfidenz muss sichtbar sein.
11. **Kernengpass:** Unstrukturierte externe Dokumente erzeugen doppelte manuelle Datenerfassung.
12. **Fehlende Informationen:** Dokumentvolumen, Pflichtfelder, Fehler, Zielsystem-Importe, Versionen, Freigabe.
13. **Top-3-Fragen:** Welche Felder sind in beiden Systemen gleich? Welche Abweichungen erfordern Rückfrage? Wie wird Dokumentversion erkannt?
14. **Verbesserungstreppe:** A Feldkatalog; B Erfassungsmaske; C Dokument-Auftrags-ID; D Extraktionsentwurf mit Konfidenz; E KI-Extraktion mit Review.
15. **Chancen:** 1) einmalige Vorprüfung, 2) Herkunftsnachweis, 3) Ausnahmen statt Vollautomatik.
16. **Kleinste Verbesserung:** Pflichtfeld-Checkliste mit Seiten-/Dokumentreferenz vor jeder Übertragung.
17. **As-Is:** `variable PDF → manuelle Prüfung → Buchhaltung + Projekttool`.
18. **To-Be:** `PDF → Feldentwurf + Quellenposition → Review → freigegebene Übergabe`.
19. **Guardrails:** Keine automatische Auftrags-, Preis- oder Buchungsfreigabe; Original-PDF und Korrekturspur erhalten.
20. **Quellen:** Reddit-Beitrag.

## RB02-C27 – Traditioneller Sanitärbetrieb vor Altsoftware-Aus

1. **Kurzprofil:** Kleiner Sanitärbetrieb mit sehr traditionellem Inhaber.
2. **Quellenlage/Vertrauen:** Hoch; direkte Aussage einer im Betrieb beteiligten Person.
3. **Ausgangssituation:** Wintac wird nicht mehr unterstützt; der Chef möchte ausdrücklich nur eine Datenbank, aus der Dispatches und ein Bericht gedruckt werden, und keine Telefon-, QuickBooks- oder Fahrzeugintegration ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1kyjfr9/need_software_for_small_plumbing_company/)).
4. **Drei Prozesse:** Kunden-/Auftragsdatenbank, Dispatch-Ausdruck, Standardbericht.
5. **Hauptprozess:** Büro erfasst Auftrag → druckt Dispatch → Außendienst arbeitet → Bericht wird erzeugt. Rückfluss vom Feld ist nicht beschrieben.
6. **Informationsfluss:** Kundenanruf → Datenbank; Datenbank → Papierdispatch; Feld → unbekannter Rückweg; Datenbank → Bericht.
7. **Hilfsmittel:** Wintac, Druckpapier; gewünschte Integrationen werden bewusst abgelehnt.
8. **Reifegrad:** 2/5, expert-derived: digitale Kerndaten plus papierbasierte Ausführung und geringe Veränderungsbereitschaft.
9. **Physische Ordnung:** Gedruckter Dispatch ist mobiles Arbeitsobjekt; Material/Fahrzeug nicht im Scope des Inhabers.
10. **Digitalisierungsreibung:** Adoption ist Hauptfaktor; ein funktionsreiches System würde den expliziten Bedarf verfehlen.
11. **Kernengpass:** Erhalt eines minimalen vertrauten Arbeitsablaufs nach Wegfall der Altsoftware.
12. **Fehlende Informationen:** Datenexport, Felder, Zahl Nutzer, Rückmeldung, Sicherung, Geräte, Berichtsinhalte.
13. **Top-3-Fragen:** Welche Wintac-Daten sind unverzichtbar? Was wird auf Dispatch handschriftlich ergänzt? Wer pflegt Abschlussdaten ein?
14. **Verbesserungstreppe:** A Minimalprozess sichern; B Datenmigration; C Status optional; D nur gewünschte Berichte; E KI derzeit nicht begründet.
15. **Chancen:** 1) Betriebsfortführung, 2) sichere Datenmigration, 3) spätere optionale Rückmeldung.
16. **Kleinste Verbesserung:** Export-/Feldinventur und Testdruck eines echten Dispatch vor jeder Systementscheidung.
17. **As-Is:** `Wintac → gedruckter Dispatch → Feld → Bericht`.
18. **To-Be:** `minimal migrierte Datenbank → identischer Druck → kontrollierter Rücklauf`.
19. **Guardrails:** Keine erzwungene Voll-Digitalisierung; Migration mit Backup, Stichprobe und Inhaberabnahme.
20. **Quellen:** Reddit-Beitrag.

## RB02-C28 – Sanitärbetrieb mit neun Beschäftigten und Belegzuordnung

1. **Kurzprofil:** Sanitärbetrieb mit neun Beschäftigten und QuickBooks.
2. **Quellenlage/Vertrauen:** Hoch; direkte, konkrete Zuordnungsanforderung.
3. **Ausgangssituation:** Belege sollen Konto, Service-/Baubereich sowie Kunde/Auftrag zugeordnet werden; ein getesteter Dienst unterstützte die Kundenzuordnung nicht ausreichend ([Quelle](https://www.reddit.com/r/smallbusiness/comments/ezh7vx/help_handling_all_these_f_receipts/)).
4. **Drei Prozesse:** Belegerfassung im Feld/Büro, Klassifikation, Jobkosten-Zuordnung.
5. **Hauptprozess:** Mitarbeiter kauft → Beleg gelangt ins Büro/System → Konto/Klasse/Kunde-Auftrag werden ergänzt → Buchung/Jobkosten.
6. **Informationsfluss:** Händlerbeleg → Mitarbeiter/Büro; Belegdaten → QuickBooks; Kontext Kunde/Auftrag → manuelle Ergänzung.
7. **Hilfsmittel:** QuickBooks und getestetes Entryless belegt; aktueller Belegtransport nicht vollständig beschrieben.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Papierbeleg muss mit Mitarbeiter, Einkauf und Auftrag verbunden bleiben.
10. **Digitalisierungsreibung:** Auftrag ist häufig nur im Kopf/auf Feldunterlagen bekannt; Geräte und Uploadpraxis unbekannt.
11. **Kernengpass:** Finanzdaten reichen nicht; operativer Auftragskontext muss nachträglich zugeordnet werden.
12. **Fehlende Informationen:** Belegweg, Verlust, Anzahl, Firmenkarten, Genehmigung, Steuerregeln, Geräte.
13. **Top-3-Fragen:** Wann kennt der Käufer die Job-ID? Wer prüft Konto/Klasse? Was passiert mit unlesbaren/mehrdeutigen Belegen?
14. **Verbesserungstreppe:** A Job-ID-Regel; B Foto/Upload mit Pflicht-ID; C Prüfwarteschlange; D Klassifikationsvorschlag; E KI nur als Vorschlag.
15. **Chancen:** 1) Beleg-Job-Verknüpfung, 2) zeitnahe Erfassung, 3) Ausnahmebearbeitung.
16. **Kleinste Verbesserung:** Job-ID beim Kauf auf Beleg notieren oder beim Foto verpflichtend auswählen.
17. **As-Is:** `Kauf → Beleg → nachträgliche Konto/Klasse/Kunde-Job-Zuordnung`.
18. **To-Be:** `Kauf + Job-ID → Belegentwurf → menschliche Klassifikationsprüfung → Buchung`.
19. **Guardrails:** Steuerliche Kategorien und Buchungen nicht autonom entscheiden; Originalbeleg erhalten.
20. **Quellen:** Reddit-Beitrag.

## RB02-C29 – Familien-Sanitärbetrieb mit extremer Personenabhängigkeit

1. **Kurzprofil:** Ehepaar führt Sanitärbetrieb; zwei weitere Techniker werden koordiniert.
2. **Quellenlage/Vertrauen:** Hoch; detaillierte direkte Rollenbeschreibung.
3. **Ausgangssituation:** Der Mann arbeitet im Feld, steuert Serviceanrufe und zwei Techniker; die Frau übernimmt Telefon, Terminierung, Abrechnung, Lohn, Marketing, Bewertungen, Follow-ups, Genehmigungen, Subunternehmer, Networking und Briefe; Arbeitstage beginnen sehr früh und enden spät ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1qle6zz/married_couple_running_a_business_together_and_i/)).
4. **Drei Prozesse:** Anfrage/Disposition, Auftrag zu Abrechnung, Genehmigungs-/Nachfassarbeit.
5. **Hauptprozess:** Anruf → Termin/Techniker → Feldarbeit → Rückmeldung → Rechnung/Nachfassen; parallele Genehmigungen/Subunternehmer hängen an der Büroinhaberin.
6. **Informationsfluss:** Kunde → Frau; Disposition → Mann/Techniker; Feld → Büro; Büro → Rechnung/Behörde/Subunternehmer. Konkrete Medien fehlen.
7. **Hilfsmittel:** Keine Systeme belegt; Telefon und Briefe werden genannt.
8. **Reifegrad:** Nicht belastbar; organisatorische Reife wichtiger als Toolgrad.
9. **Physische Ordnung:** Fahrzeuge/Material sind nicht beschrieben.
10. **Digitalisierungsreibung:** Kaum Zeit für Einführung; Wissen und Berechtigungen liegen bei zwei Personen.
11. **Kernengpass:** Zu viele Rollen, Übergaben und Wiedervorlagen ohne ersichtliche Vertretungsfähigkeit.
12. **Fehlende Informationen:** Systeme, Volumen, Prioritäten, wiederkehrende Fehler, Delegierbarkeit, Geräte.
13. **Top-3-Fragen:** Welche Aufgabe kann niemand vertreten? Welche Information wird täglich gesucht? Welche fünf Wiedervorlagen verursachen den meisten Druck?
14. **Verbesserungstreppe:** A Rollen-/Aufgabenliste; B gemeinsame Auftragsakte; C nächste Aktion/Owner; D Entwürfe/Reminder; E KI für Kommunikationsentwurf.
15. **Chancen:** 1) Vertretbarkeit, 2) Wiedervorlage, 3) Feld-Büro-Übergabe.
16. **Kleinste Verbesserung:** Gemeinsame Liste aller offenen Aufträge mit nächster Aktion, Termin und Verantwortlichem.
17. **As-Is:** `Kunde → Ehepaarwissen → Techniker/Feld → Frau bearbeitet viele Folgeprozesse`.
18. **To-Be:** `Auftrags-ID → Status + nächste Aktion + Owner → Feld/Büro-Freigaben`.
19. **Guardrails:** Keine Personal-, Zahlungs-, Genehmigungs- oder Kundenentscheidung autonom; Entlastung nicht mit parallelem Großprojekt gefährden.
20. **Quellen:** Reddit-Beitrag.

## RB02-C30 – Sanitärbüro als analoger Betriebsknoten

1. **Kurzprofil:** Kleines Sanitärunternehmen mit Büro, Technikern und älterer Kundschaft.
2. **Quellenlage/Vertrauen:** Hoch; detaillierte direkte Beschreibung der Büroaufgaben.
3. **Ausgangssituation:** Büro empfängt Kunden, Post, Lieferungen und Uniformanbieter; Techniker geben Belege, Schecks/Bargeld, Genehmigungen, Zertifikate, Sign-offs und Verträge ab. Ältere Kunden benötigen physische Kopien; Fax und Bankeinzahlungen gehören zum Ablauf ([Quelle](https://www.reddit.com/r/smallbusiness/comments/rb4veq/employee_keeps_missing_work_due_to_emergencies/)).
4. **Drei Prozesse:** Feldunterlagen-Rücklauf, Kundendokumente/Post, Zahlung/Bankeinzahlung.
5. **Hauptprozess:** Techniker/Fremde bringen physische Objekte/Dokumente → Büro sortiert und ordnet zu → Scan/Post/Fax/Bank/Weiterbearbeitung.
6. **Informationsfluss:** Feld/Kunde/Lieferant → physischer Büroeingang; Büro → Auftrag/Behörde/Bank/Kunde; Status stark personengebunden.
7. **Hilfsmittel:** Papier, Post, Fax, Schecks, Bargeld und physische Kopien belegt; Softwaresystem unbekannt.
8. **Reifegrad:** 1/5, expert-derived.
9. **Physische Ordnung:** Eingangskörbe, Originale, Geld und Auftragspapiere brauchen getrennte, kontrollierte Wege.
10. **Digitalisierungsreibung:** Manche Kunden brauchen Papier; Originale und Bargeld können nicht rein digital ersetzt werden.
11. **Kernengpass:** Eine Büroperson vermittelt viele heterogene physische und digitale Flüsse; Ausfall wirkt sofort.
12. **Fehlende Informationen:** Ablagen, Scans, Vertretung, Fristen, Zugriffe, Volumen, Verlustfälle.
13. **Top-3-Fragen:** Welche Eingangstypen haben Fristen? Welche Originale müssen erhalten bleiben? Was kann eine Vertretung ohne die Büroperson nicht finden?
14. **Verbesserungstreppe:** A Eingangskategorien; B Eingangsregister; C Status/Owner; D Erinnerungen; E KI für Dokumentklassifikation mit Review.
15. **Chancen:** 1) physisches Eingangssystem, 2) Vertretbarkeit, 3) Fristensicht.
16. **Kleinste Verbesserung:** Beschriftete Eingangszonen plus tägliches Register mit Auftrag, Typ, nächster Aktion und Verwahrort.
17. **As-Is:** `viele physische Eingänge → Büroperson → Post/Fax/Bank/Auftrag`.
18. **To-Be:** `Eingangszone → Register/ID → Owner + Frist → physisch/digitaler Abschluss`.
19. **Guardrails:** Bargeld, Schecks, Originale und rechtlich relevante Dokumente mit menschlicher Übergabe; keine automatische Entsorgung.
20. **Quellen:** Reddit-Beitrag.

## RB02-C31 – Fertiger mit fehlender WIP-/Stücklistenlogik

1. **Kurzprofil:** Kleiner Fertigungsbetrieb mit Zoho Books.
2. **Quellenlage/Vertrauen:** Mittel; direkte Anforderung, wenige Prozessdetails.
3. **Ausgangssituation:** Gesucht werden Bestandsplanung, WIP, Produktionsaufträge, Kosten und Stücklisten; Zoho Inventory wird als für Fertigung unzureichend bewertet ([Quelle](https://www.reddit.com/r/smallbusiness/comments/9qmyad/inventory_management_software_for_a_manufacturing/)).
4. **Drei Prozesse:** Materialplanung, Produktionsauftrag/WIP, Produktkosten.
5. **Hauptprozess:** Bedarf → Material → Produktionsauftrag → WIP → Fertigware → Kosten; aktuelle manuelle Hilfsmittel fehlen.
6. **Informationsfluss:** Auftrag/Plan → Materialbedarf; Werkstatt → WIP; Verbrauch/Zeit → Kosten; Abschluss → Bestand.
7. **Hilfsmittel:** Zoho Books belegt; gesuchte SaaS-Lösung ist kein Ist-Beleg.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Material, Auftrag und WIP müssen durch IDs/Lagerorte verbunden sein; aktuelle Praxis unbekannt.
10. **Digitalisierungsreibung:** Stücklisten- und Kostenlogik muss vor Systemwahl stabil sein.
11. **Kernengpass:** Buchhaltung bildet den physischen Transformationsprozess nicht ab.
12. **Fehlende Informationen:** Branche, Stückzahlen, Varianten, Ausschuss, Arbeitsplätze, Geräte, Buchungsdisziplin.
13. **Top-3-Fragen:** Welche WIP-Stufen steuern Entscheidungen? Wie stabil sind Stücklisten? Wann werden Verbräuche bestätigt?
14. **Verbesserungstreppe:** A Produkt-/Stufenmodell; B Produktionskarte; C WIP-Status; D Bedarfsvorschlag; E KI für Notizen.
15. **Chancen:** 1) Material-Auftrag-Verknüpfung, 2) WIP, 3) nachvollziehbare Kostenbasis.
16. **Kleinste Verbesserung:** Ein Pilotauftrag mit freigegebener Stückliste, Sollmenge, Istverbrauch und Abschlussstatus.
17. **As-Is:** `Buchhaltung + unklarer Fertigungsfluss → WIP/Kosten fehlen`.
18. **To-Be:** `Produktionsauftrag → Materialreservierung → WIP → bestätigter Abschluss`.
19. **Guardrails:** Keine Bestellung, Kostenfreigabe oder Qualitätsentscheidung autonom; Ist-Verbrauch bestätigen.
20. **Quellen:** Reddit-Beitrag.

## RB02-C32 – Luxus-Einzelhandel mit Kundenwissen im Gedächtnis

1. **Kurzprofil:** Kleiner Luxus-Einzelhandel mit vielen Stammkunden.
2. **Quellenlage/Vertrauen:** Mittel; direkte Selbstauskunft, keine unabhängige zweite Quelle.
3. **Ausgangssituation:** Käufe, Vorlieben, ausbleibende Besuche und abholbereite Bestellungen sind über WhatsApp, mehrere Tabellen und Mitarbeitergedächtnis verteilt; bei Weggang eines Mitarbeiters geht Wissen verloren ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1uq2mug/how_do_you_lot_keep_track_of_regular_customers/)).
4. **Drei Prozesse:** Kundenberatung, Sonderbestellung/Abholung, Beziehungsnachfassen.
5. **Hauptprozess:** Kundenkontakt → Notiz in Chat/Tabelle/Kopf → Bestellung/Reservierung → „bereit“ → Erinnerung oder Abholung.
6. **Informationsfluss:** Kunde → Mitarbeiter; Mitarbeiter → WhatsApp/Sheet/Gedächtnis; Teamwechsel → Wissensverlust.
7. **Hilfsmittel:** WhatsApp, mehrere Spreadsheets und Gedächtnis belegt.
8. **Reifegrad:** 2/5, expert-derived.
9. **Physische Ordnung:** Kundenspezifische/abholbereite Ware braucht Verbindung zum Kundenauftrag; Kennzeichnung unbekannt.
10. **Digitalisierungsreibung:** Datensparsamkeit und Akzeptanz im Verkaufsgespräch; persönliche Beziehung darf nicht zu unkontrollierter Datensammlung werden.
11. **Kernengpass:** Kunden- und Auftragswissen ist verteilt und personengebunden.
12. **Fehlende Informationen:** Einwilligungen, Kundenzahl, POS, Reservierungslabel, Geräte, Zugriffsrollen.
13. **Top-3-Fragen:** Welche Information ist betrieblich nötig? Wie wird abholbereite Ware markiert? Wer darf Vorlieben/Kontaktnotizen sehen?
14. **Verbesserungstreppe:** A Minimalfelder/Datenschutz; B Bestell-ID; C Teamstatus; D Erinnerungsentwurf; E KI nur auf freigegebenen Notizen.
15. **Chancen:** 1) Abholstatus, 2) Vertretbarkeit, 3) kontrollierte Kundenhistorie.
16. **Kleinste Verbesserung:** Gemeinsame Liste nur für offene Sonderbestellungen: ID, Kunde, Ware, Status, letzter Kontakt.
17. **As-Is:** `Kundenkontakt → WhatsApp + Sheets + Kopf → Bestellung/Abholung`.
18. **To-Be:** `Bestell-ID → offene Liste + Rollen → Kontaktentwurf → menschlicher Versand`.
19. **Guardrails:** Keine sensiblen Vorlieben ungeprüft speichern; keine automatische Kundenansprache oder Profilentscheidung.
20. **Quellen:** Reddit-Beitrag.

## RB02-C33 – Hautpflegemarke mit persönlichem WhatsApp als Servicezentrale

1. **Kurzprofil:** Kleine Online-Hautpflegemarke; öffentlich nur durch einen Freund beschrieben.
2. **Quellenlage/Vertrauen:** Niedrig; Zweitbericht, daher nur Hypothesenquelle.
3. **Ausgangssituation:** Ein persönlicher WhatsApp-Account bearbeitet laut Bericht Bestellfragen, Trackinglinks, Beschwerden und Warenkorbnachfassen; parallel werden Bestellungen gepackt und Anzeigen gesteuert ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1s53txb/my_friend_runs_her_business_from_one_whatsapp/)).
4. **Drei Prozesse:** Supportanfrage, Versandstatus, Beschwerde/Nachfassen.
5. **Hauptprozess:** Nachricht → persönliche Sichtung → Suche nach Bestellkontext → Antwort/Tracking/Beschwerdebearbeitung. Volumenangaben sind nicht unabhängig geprüft.
6. **Informationsfluss:** Kunde → persönliches Telefon; Telefon → Inhaberwissen; Shop/Tracking → manuelle Antwort.
7. **Hilfsmittel:** WhatsApp auf persönlichem Telefon berichtet; weitere Systeme nicht sicher.
8. **Reifegrad:** 1–2/5, expert-derived und unsicher.
9. **Physische Ordnung:** Packauftrag und Nachricht müssen über Bestell-ID verbunden sein; heutige Praxis nicht belegt.
10. **Digitalisierungsreibung:** Persönliches Gerät, Datenschutz, fehlende Vertretung und parallele Packarbeit.
11. **Kernengpass:** Ein privater Kanal bündelt mehrere Falltypen ohne sichtbare Zuständigkeit oder Status.
12. **Fehlende Informationen:** Primärbestätigung, tatsächliches Volumen, Team, Shopdaten, Einwilligung, Antwortzeiten.
13. **Top-3-Fragen:** Ist der Bericht korrekt? Welche Nachrichtentypen brauchen Shopdaten? Wer kann bei Abwesenheit übernehmen?
14. **Verbesserungstreppe:** A Falltypen/ID; B getrennte Geschäftsinbox; C Status/Owner; D Antwortentwurf; E KI mit Eskalation.
15. **Chancen:** 1) Kanaltrennung, 2) Bestellkontext, 3) Vertretbarkeit.
16. **Kleinste Verbesserung:** Geschäftliche Nummer/Inbox und Pflichtangabe der Bestellnummer bei bestellbezogenen Anfragen.
17. **As-Is:** `Kunde → persönliches WhatsApp → Inhaber sucht/antwortet während Packarbeit`.
18. **To-Be:** `Geschäftsinbox → Falltyp/Bestell-ID → Owner → Antwortfreigabe`.
19. **Guardrails:** Zweitbericht verifizieren; Beschwerden, Erstattungen und Gesundheitsfragen nicht automatisch entscheiden.
20. **Quellen:** Reddit-Zweitbericht.

## RB02-C34 – Dienstleistungsbetrieb mit manuellem Monatsabschluss

1. **Kurzprofil:** Kleiner Betrieb; Branche in der Quelle nicht genannt.
2. **Quellenlage/Vertrauen:** Mittel; direkte Selbstauskunft zu konkreten Buchhaltungsaufgaben, aber unvollständiges Profil.
3. **Ausgangssituation:** Monatlich werden Banktransaktionen kopiert, E-Mail-Belege gesucht und Rechnungen/Zahlungen abgeglichen; trotz Scanner, Bankfeeds und VA kehrt die Person zu Excel zurück ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1noa6lt/anyone_else_lose_their_mind_doing_bookkeeping/)).
4. **Drei Prozesse:** Bankdatenübernahme, Belegsuche, Rechnungs-/Zahlungsabgleich.
5. **Hauptprozess:** Bankbewegung → Beleg in E-Mail/anderen Orten suchen → Rechnung/Zahlung zuordnen → Excel/Kategorisierung.
6. **Informationsfluss:** Bank → Transaktion; E-Mail → Beleg; Rechnungssystem → Forderung; Inhaber → manueller Match in Excel.
7. **Hilfsmittel:** Excel, E-Mail, ausprobierte Scanner/Bankfeeds/VA belegt.
8. **Reifegrad:** 2/5, expert-derived: viele digitale Quellen, aber kein stabiler Abgleich.
9. **Physische Ordnung:** Papierbelege möglich, aber nicht ausdrücklich belegt.
10. **Digitalisierungsreibung:** Frühere Lösungen scheiterten offenbar an Kategorisierung/Passung; genaue Gründe sind zu erfragen.
11. **Kernengpass:** Beleg, Rechnung und Zahlung besitzen keinen verlässlichen gemeinsamen Schlüssel.
12. **Fehlende Informationen:** Branche, Volumen, Systeme, Konten, Belegarten, Buchhalterrolle, Fehlerquote.
13. **Top-3-Fragen:** Welche Matches sind eindeutig? Wo fehlt eine Rechnungs-/Referenznummer? Warum wurden Bankfeed/Scanner aufgegeben?
14. **Verbesserungstreppe:** A Referenzregeln; B Eingangssammelpunkt; C Matchstatus; D Matchvorschlag; E KI für Belegextraktion mit Review.
15. **Chancen:** 1) Beleg-Inbox, 2) Referenzschlüssel, 3) Ausnahmeliste.
16. **Kleinste Verbesserung:** Einheitlicher digitaler Belegeingang und wöchentliche statt monatliche Zuordnung.
17. **As-Is:** `Bank + E-Mail + Rechnungen → Suche/Excel-Match`.
18. **To-Be:** `Beleg-Inbox + Referenz → Matchvorschlag → menschliche Prüfung → Abschluss`.
19. **Guardrails:** Steuerliche Kategorien und Buchungen nicht autonom; fehlende Belege nicht erfinden.
20. **Quellen:** Reddit-Beitrag.

## RB02-C35 – Kleines Brewpub mit Finanzsicht aus mehreren Werkzeugen

1. **Kurzprofil:** Kleines Brewpub mit mehreren Partnern; Bericht stammt von einem Angehörigen.
2. **Quellenlage/Vertrauen:** Niedrig; Zweitbericht, Zahlen und Aufwand nicht unabhängig verifiziert.
3. **Ausgangssituation:** QuickBooks und Tabellen werden genutzt, um Menüverkäufe, Biermargen, Forderungen und Cashflow zu verstehen; der Bericht nennt über 20 Stunden monatlich ([Quelle](https://www.reddit.com/r/smallbusiness/comments/1l1sa9g/how_are_you_getting_financial_info_about_your/)).
4. **Drei Prozesse:** Verkaufsdatenaufbereitung, Margenbetrachtung, Forderungs-/Cashflowübersicht.
5. **Hauptprozess:** Daten aus Betrieb/QuickBooks → Tabellenaufbereitung → Partner versuchen Kennzahlen zu verstehen → Entscheidungen. Exakte Datenquellen fehlen.
6. **Informationsfluss:** POS/Buchhaltung (teilweise angenommen) → QuickBooks/Sheets → Partner. Nur QuickBooks/Sheets und Analyseziele sind berichtet.
7. **Hilfsmittel:** QuickBooks und Spreadsheets berichtet.
8. **Reifegrad:** 2–3/5, expert-derived und unsicher.
9. **Physische Ordnung:** Zutaten-/Fass-/Menübestand nicht im Quellenbeleg beschrieben.
10. **Digitalisierungsreibung:** Kennzahlen benötigen einheitliche Artikel-, Kosten- und Periodenlogik; Datenqualität unbekannt.
11. **Kernengpass:** Finanz-/Betriebsinformationen müssen manuell zusammengeführt und interpretiert werden.
12. **Fehlende Informationen:** Primärbestätigung, POS, Kontenplan, Rezeptkosten, Aktualität, Rollen, Entscheidungsbedarf.
13. **Top-3-Fragen:** Welche Entscheidung wird zu spät getroffen? Welche Quelle ist je Kennzahl führend? Welche Daten werden manuell kopiert?
14. **Verbesserungstreppe:** A Kennzahlendefinition; B Datenquellenkarte; C periodische geprüfte Ansicht; D Abweichungshinweise; E KI nur zur Erläuterung belegter Zahlen.
15. **Chancen:** 1) Kennzahlenklarheit, 2) weniger Kopieren, 3) nachvollziehbare Quellen.
16. **Kleinste Verbesserung:** Für drei Entscheidungen je eine Kennzahl mit Definition, Quelle, Owner und Aktualisierungsrhythmus dokumentieren.
17. **As-Is:** `QuickBooks + Tabellen → manuelle Finanzanalyse → Partnerentscheidung`.
18. **To-Be:** `definierte Quellen → geprüfte Kennzahlenansicht → Abweichungsreview → Entscheidung`.
19. **Guardrails:** Keine Finanz-, Preis- oder Beschaffungsentscheidung autonom; Zweitbericht vor Einsatz verifizieren.
20. **Quellen:** Reddit-Zweitbericht.

---

---

# Gesamtanalyse A–J

## A. Branchenmatrix

| Cluster | Fälle | Neue Erkenntnis für AI Start Map |
|---|---:|---|
| Physische Einzelobjekte/Reparatur | C01–C05 | Auftrag und Gegenstand brauchen dauerhafte gemeinsame Identität; physischer Ort kann Status tragen. |
| Handel/Produktion/Lager | C06–C14, C31 | Mengeneinheiten, Varianten, Charge, WIP und Umwandlung sind vor Automatisierung zu modellieren. |
| Mobile/Terminbetriebe | C15–C24 | Verfügbarkeit hängt oft von Ort, Dauer, Person und Ressource ab; ein freier Kalenderslot genügt nicht. |
| Handwerk/Büro/Dokument | C26–C30, C34 | Papier bleibt wegen Feldarbeit, Originalen, Kundschaft oder Übergaben Teil des Sollprozesses. |
| Kundenwissen/Finanzsicht | C32–C35 | Digitale Daten können trotzdem fragmentiert, personengebunden oder entscheidungsfern sein. |

## B. Wiederkehrende Prozessmuster

1. **Objekt–Auftrag–Status:** Reparaturgegenstand, Mietobjekt, Rolle, Charge, Palette oder Kundensonderbestellung.
2. **Unstrukturierter Eingang → strukturierter Datensatz:** WhatsApp, Telefon, PDF, Papierbeleg.
3. **Physische Transformation/WIP:** Rohling oder Rohstoff verändert Form und Bestandsidentität.
4. **Mehrressourcen-Termin:** Person + Ort + Fahrzeug/Platz + Dauer.
5. **Feld–Büro-Rücklauf:** Papier, Foto, Beleg, Zahlung oder Leistungsbestätigung kommt zeitversetzt zurück.
6. **Wiederkehrender Verwaltungslauf:** Monatsbelastung, Vergütung, Buchhaltung, Kennzahlen.

## C. Informationsmuster

- Gemeinsame Schlüssel fehlen: Bestellnummer, Job-ID, Chargen-ID oder Versand-ID.
- Derselbe Sachverhalt liegt in Chat, Tabelle, Fachanwendung, Fotoordner und Gedächtnis.
- Status wird indirekt über Ablageort, Papierstapel oder die Person dargestellt, die „es weiß“.
- Digitale Inseln sind nicht automatisch höhere Prozessreife: Der Salon mit vier Apps hat weiterhin manuelle Zahlungsprüfung.
- „Noch offen“ und „bereits erledigt“ werden selten explizit unterschieden; eine nächste Aktion mit Owner fehlt.

## D. Analogitätsmuster

| Muster | Nutzen heute | Risiko/Schwäche | Realistischer erster Schritt |
|---|---|---|---|
| Papierkarte am Objekt | schnell, sichtbar, werkstattnah | Verlust, keine Fernsicht | robuste ID + Pflichtfelder; Papier darf bleiben |
| Physische Zone/Stapel | Status ohne Eingabe | nicht eindeutig, keine Historie | benannte Zonen + täglicher Abgleich |
| Papierkalender | schnell und vertraut | parallele Kanäle, Änderungsverlauf | ein führender Kalender + Bestätigungsregel |
| Separates Fotohandy | einfacher Beleg | Suche und Zuordnung | Auftrags-ID im Foto/Ordner |
| Fahrer-/Inhaberwissen | flexibel | nicht vertretbar | Tagesliste + Ausnahmefeedback |
| Original/Post/Fax | kundenseitig oder rechtlich nötig | Fristen und Verwahrort | Eingangsregister statt erzwungener Abschaffung |

## E. Einführungsbarrieren

1. **Zeitmangel:** Personenabhängige Betriebe können kein Großprojekt tragen.
2. **Explizite Funktionsablehnung:** C27 zeigt, dass „mehr Funktionen“ Adoption verschlechtern kann.
3. **Unpassende Datenmodelle:** Yard-Bruchteile, Chargen, WIP und Routenlogik passen nicht in generische Tools.
4. **Geräte-/Arbeitsumgebung:** Werkstatt, Lager, Fahrzeug oder Marktstand brauchen andere Eingaben als ein Büro.
5. **Migrationsrisiko:** Altsoftware, Tabellenformeln und Papierhistorien dürfen nicht blind ersetzt werden.
6. **Kosten-/Komplexitätssensitivität:** C03, C08 und C19 nennen Budget oder Überfrachtung direkt.

## F. Gerätematrix

| Arbeitsumgebung | Wahrscheinlicher geeigneter Träger | Vor Einführung zwingend prüfen |
|---|---|---|
| Annahmetresen | PC/Tablet + Druck/Label | Platz, Geschwindigkeit, parallele Nutzer |
| Werkbank | Papier/robustes Label + optional Scan | Hände, Schmutz, Handschuhe, Strom/Netz |
| Lager | Mobilgerät/Scanner + sichtbare Zonen | Offline, Reichweite, Etikettenhaltbarkeit |
| Fahrzeug/Außendienst | Smartphone + kurze Statusauswahl | BYOD, Datenschutz, Netz, Ablenkung |
| Marktstand | Kunden- und Verkäufertelefon | Netz, Zahlungsbestätigung, Offline-Fallback |
| Papierbüro | Scanner/PC + physische Eingangszonen | Originalpflicht, Verwahrort, Vertretung |

Die Matrix ist expert-derived; konkrete Geräte müssen je Betrieb erfragt werden.

## G. Interview-Fragenbibliothek

**Objektidentität:** Woran erkennt eine fremde Vertretung eindeutig Auftrag und Gegenstand? Welche ähnlichen Gegenstände können verwechselt werden? Was bleibt physisch am Objekt?

**Status:** Welche fünf Zustände lösen wirklich eine andere Handlung aus? Wird Status heute durch Ort, Zettel, Chat oder Erinnerung dargestellt? Wer darf ihn ändern?

**Informationsfluss:** Wo wird dieselbe Information erneut eingegeben? Welcher Datensatz ist führend? Welche Information entsteht zuerst im Gespräch oder auf Papier?

**Mobilität/Geräte:** Welches Gerät ist im Moment der Datenerfassung tatsächlich erreichbar? Funktioniert der Ablauf ohne Netz? Wie viele Sekunden darf eine Eingabe dauern?

**Freigabe:** Welche Entscheidung verändert Preis, Termin, Zahlung, Qualität, Vertrag oder Kundenanspruch? Wer muss sie bestätigen? Was darf nur als Entwurf erscheinen?

**Adoption:** Welche heutige 20-Sekunden-Handlung darf nicht langsamer werden? Welche Funktion wird ausdrücklich nicht gewünscht? Wer kann den Prozess vertreten?

## H. Reifegradlogik

- **0:** Kein stabiler Datensatz; zuerst Ordnung, IDs, Statussprache.
- **1:** Einzelne digitale Werkzeuge; zuerst führenden Datensatz und Pflichtfelder klären.
- **2:** Tabellen/Apps mit Medienbrüchen; zuerst gemeinsame IDs und Ausnahmeprozess.
- **3:** Fachsystem vorhanden; zuerst Integrationsbedarf nicht unterstellen, sondern Datenhoheit/Exports prüfen.
- **4:** Strukturierte, verbundene Prozesse; regelbasierte Automatisierung mit Monitoring möglich.
- **5:** KI kann auf messbarer Prozessqualität assistieren; autonome Entscheidungen bleiben domänenspezifisch begrenzt.

Bewertung erfolgt hybrid und evidenzbasiert anhand transparenter Rubrics und belegter Eingaben, nicht „deterministisch“ aus unsicheren Beobachtungen.

## I. RAG-Lückenanalyse gegenüber dem bisherigen Stand

Dieser Batch erweitert vor allem: physische Statuszonen, Objekt-/Auftragsidentität, WIP-Transformation, Bruchmengeneinheiten, Foto-Nachweisketten, Papier als legitimer Sollbestandteil, Minimalmigration bei digitaler Ablehnung, mobile Mehrressourcenplanung und personengebundene Büro-Hubs.

Bewusst nicht als neue Nutzerfakten übernommen wurden: konkrete Zeit-/Kostenwerte aus Vergleichsfällen, nicht belegte Geräte, vermutete Schnittstellen, Rechts-/Compliance-Anforderungen und Anbieterbehauptungen. Ähnliche Fälle dürfen beim Retrieval nicht alle Top-k-Plätze belegen.

**Retrieval-Regel:** maximal zwei `case_evidence`-Chunks je `pattern_id`; zusätzlich mindestens ein `diagnostic_pattern` oder `interview_question_pattern` und mindestens ein `automation_guardrail`. `source_strength=low` darf keine alleinige Grundlage für eine Empfehlung sein.

## J. Nächste Research-Runde

1. Deutsche Primärinterviews oder Handwerkskammer-Fälle zu Schuhmacher, Textilreinigung, Uhr-/Schmuck- und Instrumentenreparatur.
2. Detaillierte Werkstattfälle zu Zusatzschäden, Preisänderung und Abholung durch Dritte.
3. Offline-/BYOD-Realität in Gartenpflege, Schädlingsbekämpfung und Hausmeisterdiensten.
4. Floristik/Catering mit Rezeptur, Verderb, kurzfristigen Änderungen und Lieferfenstern.
5. Kleine Bildungs-/Pflege-nahe Organisationen mit Papiernachweisen, ohne medizinische Entscheidungsunterstützung.
6. Für alle niedrigen Zweitberichte: Primärquelle oder direktes Interview vor Korpus-Hochstufung.

