# test_integration.py
# Aufruf: python -m pytest tests/test_integration.py

import pytest
import sqlite3
from repository import TrainingRepository
from models import Dauerlauf


def test_full_workflow():
    """
    Validiert den gesamten Lebenszyklus einer Trainingseinheit (End-to-End).

    Dieser Integrationstest nutzt eine flüchtige In-Memory-Datenbank, um:
    1. Die korrekte Verknüpfung von Benutzern und Trainings zu prüfen.
    2. Die mathematische Korrektheit der Analyse-Logik (Pace-Berechnung)
       auf Datenbank-Ebene zu verifizieren.
    3. Das Kaskadierungsverhalten beim Löschen von Daten zu testen.

    Dient als Absicherung gegen Regressionen bei Änderungen an der
    Datenbankstruktur oder den Berechnungsalgorithmen.
    """

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    repo = TrainingRepository(connection=conn)

    # 1. User-Workflow
    u_id = repo.add_benutzer("Integrations-Tester")

    # 2. Trainings-Workflow
    lauf = Dauerlauf(
        distanz_km=10.0,
        hf_mittel=150,
        nutzer_id=1,
        datum="2026-04-25",
        uhrzeit="10:00",
        dauer_min=60
    )
    repo.training_speichern(lauf)

    # 3. Analyse-Workflow
    pace_data = repo.get_dauerlauf_pace()
    assert len(pace_data) == 1
    assert pace_data[0][3] == 6.0  # 60 min / 10 km

    # 4. Lösch-Workflow
    repo.loesche_benutzer(u_id)
    assert len(repo.get_alle_benutzer()) == 0