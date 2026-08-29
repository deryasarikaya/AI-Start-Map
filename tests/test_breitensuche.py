"""Die zweite Abrufsicht: starke lokale Treffer.

**Warum es sie gibt.** Die Punktesumme über alle Absätze belohnt, was
sich durch die ganze Erzählung zieht. Für den Hauptengpass ist das
richtig. Für die Breite des Zielbilds ist es genau falsch herum: Ein
Bedarf, den der Kunde **einmal genau** beschreibt, verliert gegen ein
Thema, das er zwölfmal beiläufig streift.

Gemessen am Heizungsfall: DP-01, DP-03 und DP-05 führen je einen Absatz
mit Werten um 0,6 an — und landen in der Gesamtrangfolge auf den Plätzen
8, 9 und 10. Der Schnitt liegt bei drei.
"""

from __future__ import annotations

import numpy as np

from app import rag_service


def _muster(kennung: str) -> rag_service.KnowledgeChunk:
    return rag_service.KnowledgeChunk(
        chunk_id=kennung,
        chunk_type="diagnostic_pattern",
        title=f"Muster {kennung}",
        content=f"Muster {kennung}",
        source_file="test",
        metadata={"chunk_id": kennung},
    )


def _treffer(zeilen: list[list[float]], chunks: list[rag_service.KnowledgeChunk]):
    """Absatzweise Trefferwerte, wie FAISS sie liefert."""

    werte = np.array(zeilen, dtype="float32")
    plaetze = np.array([list(range(len(chunks)))] * len(zeilen), dtype="int64")
    return werte, plaetze


def test_a_pattern_that_leads_one_paragraph_survives_a_low_total() -> None:
    """**Ein starker lokaler Treffer geht nicht mehr verloren.**

    Muster B führt nur den zweiten Absatz an und käme in der Punktesumme
    nie durch. Genau dieser Fall liess beim Heizungsfall die
    Einsatzdokumentation und die Morgenübersicht verschwinden.
    """

    chunks = [_muster("DP-A"), _muster("DP-B")]
    # Absatz 1: A führt. Absatz 2: B führt, fast genauso stark.
    werte, plaetze = _treffer([[0.70, 0.40], [0.50, 0.66]], chunks)

    breite = rag_service._breitenkandidaten(werte, plaetze, chunks, [chunks[0]])

    assert [c.chunk_id for c in breite] == ["DP-B"]


def test_a_weak_local_hit_does_not_get_in() -> None:
    """**Breiter ist nicht dasselbe wie besser.**

    Wer nur deshalb einen Absatz anführt, weil dort sonst nichts passt,
    beschreibt keinen Bedarf. Ohne diese Schwelle wäre die Breitensuche
    bloss eine längere Liste — und jede Messung danach sähe besser aus,
    ohne dass das Ergebnis besser wäre.
    """

    chunks = [_muster("DP-A"), _muster("DP-SCHWACH")]
    # Der zweite Absatz wird mit 0,30 angeführt - weit unter dem Besten.
    werte, plaetze = _treffer([[0.70, 0.20], [0.10, 0.30]], chunks)

    breite = rag_service._breitenkandidaten(werte, plaetze, chunks, [chunks[0]])

    assert breite == ()


def test_the_focus_patterns_are_not_repeated_as_breadth() -> None:
    """Was schon im Fokus steht, macht die Breite nicht breiter."""

    chunks = [_muster("DP-A"), _muster("DP-B")]
    werte, plaetze = _treffer([[0.70, 0.40], [0.50, 0.66]], chunks)

    breite = rag_service._breitenkandidaten(
        werte, plaetze, chunks, [chunks[0], chunks[1]]
    )

    assert breite == ()


def test_breadth_stays_within_its_limit() -> None:
    """Der Deckel hält, auch wenn viele Muster stark sind.

    Ohne ihn wäre die Breitensuche ein zweiter Weg, alles vorzuschlagen.
    """

    viele = [_muster(f"DP-{n:02d}") for n in range(1, 10)]
    # Jedes Muster führt genau einen Absatz an, alle etwa gleich stark.
    zeilen = []
    for n in range(len(viele)):
        zeile = [0.60] * len(viele)
        zeile[n] = 0.68
        zeilen.append(zeile)
    werte, plaetze = _treffer(zeilen, viele)

    breite = rag_service._breitenkandidaten(werte, plaetze, viele, [])

    assert len(breite) == rag_service.BREITE_HOECHSTENS


def test_breadth_is_ordered_the_same_way_every_time() -> None:
    """Zwei Läufe über denselben Text liefern dieselbe Reihenfolge.

    Sonst wären zwei Messungen nicht vergleichbar — und genau das
    Vergleichen ist der Zweck.
    """

    chunks = [_muster("DP-A"), _muster("DP-B"), _muster("DP-C")]
    werte, plaetze = _treffer(
        [[0.70, 0.30, 0.30], [0.30, 0.62, 0.30], [0.30, 0.30, 0.66]], chunks
    )

    zuerst = rag_service._breitenkandidaten(werte, plaetze, chunks, [chunks[0]])
    danach = rag_service._breitenkandidaten(werte, plaetze, chunks, [chunks[0]])

    assert [c.chunk_id for c in zuerst] == [c.chunk_id for c in danach]
    # Nach bestem Absatzwert, nicht nach Reihenfolge im Index.
    assert [c.chunk_id for c in zuerst] == ["DP-C", "DP-B"]


def test_breadth_candidates_do_not_force_a_family() -> None:
    """**Kandidaten sind Vorschläge, keine Auswahl.**

    Die Breitensuche erweitert nur, was dem Planner zur Wahl steht. Was
    er tatsächlich wählt, entscheidet er fachlich — und der ganze
    freigegebene Katalog steht ihm ohnehin offen.
    """

    from app import solution_catalog

    # Der Katalog kennt jede Familie, unabhaengig von jedem Abruf.
    waehlbar = set(solution_catalog.katalog())

    assert "SF-03" in waehlbar
    assert "SF-09" in waehlbar
