from __future__ import annotations

import subprocess
from pathlib import Path


from app.schemas import customer_plain_text


ROOT = Path(__file__).resolve().parents[1]


def test_unsubstantiated_benefit_claim_is_removed_without_word_replacement() -> None:
    text = (
        "Eine Vorgangsakte reduziert Suchzeit und Nacharbeit. "
        "Du siehst danach den geprüften Eintrag."
    )
    assert customer_plain_text(text) == "Du siehst danach den geprüften Eintrag."


def test_real_address_with_musterstrasse_is_not_confused_with_pattern_language() -> None:
    text = "Lieferung an Frau Müller, Musterstraße 5."
    assert customer_plain_text(text) == text


def test_old_slogan_and_wrong_name_are_absent_from_tracked_files() -> None:
    slogan = subprocess.run(
        [
            "git",
            "grep",
            "-n",
            "Ordnen · mit KI unterst\u00fctzen · sp\u00e4ter automatisieren",
            "--",
            "app/templates",
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    wrong_name = subprocess.run(
        ["git", "grep", "-ni", "-w", "Da" + "ria"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    assert slogan.returncode == 1, slogan.stdout
    assert wrong_name.returncode == 1, wrong_name.stdout
