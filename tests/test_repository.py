# tests/test_repository.py
# Aufruf: python -m pytest tests/test_repository.py -v

import sqlite3

import pytest

from models import Dauerlauf, Krafttraining, Uebung, Sprint
from repository import TrainingRepository


@pytest.fixture
def repo():
    """Erstellt eine In-Memory Verbindung, die während des Tests offen bleibt."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")

    repository = TrainingRepository(connection=conn)    # Übergibt die offene Verbindung an das Repo.
    repository.add_benutzer("Test User")      # Erstellt einen Standard-Benutzer, damit die Foreign Keys funktionieren
    return repository

def test_save_dauerlauf(repo):
    # 1. Objekt erstellen
    lauf = Dauerlauf(
        distanz_km = 10.0,
        hf_mittel = 150,
        nutzer_id = 1,
        datum = "2026-04-25",
        uhrzeit = "10:00",
        dauer_min = 50
    )

    # 2. Speichern
    repo.training_speichern(lauf)

    # 3. Datenbank-Prüfung
    with repo._get_connection() as conn:
        # Basisdaten prüfen
        res = conn.execute("SELECT typ, dauer_min, datum FROM trainings").fetchone()
        assert res is not None
        assert res[0] == "Dauerlauf"
        assert res[1] == 50
        assert res[2] == "2026-04-25"

        # Spezifische Details prüfen
        detail = conn.execute("SELECT distanz_km, hf_mittel FROM dauerlauf_details").fetchone()
        assert detail is not None
        assert detail[0] == 10.0
        assert detail[1] == 150

def test_save_sprint(repo):
    # 1. Objekt erstellen
    sprint = Sprint(
        anzahl = 10,
        max_kmh = 32.5,
        nutzer_id = 1,
        datum = "2026-04-26",
        uhrzeit = "11:00",
        dauer_min = 20
    )

    # 2. Speichern
    repo.training_speichern(sprint)

    # 3. Datenbank-Prüfung
    with repo._get_connection() as conn:
        # Basisdaten prüfen
        res = conn.execute("SELECT typ, nutzer_id FROM trainings").fetchone()
        assert res is not None
        assert res[0] == "Sprint"
        assert res[1] == 1

        # Spezifische Details prüfen
        detail = conn.execute("SELECT anzahl, max_kmh FROM sprint_details").fetchone()
        assert detail is not None
        assert detail[0] == 10
        assert detail[1] == 32.5

def test_save_krafttraining(repo):
    # 1. Objekt erstellen
    kraft = Krafttraining(
        nutzer_id=1,
        datum="2026-04-25",
        uhrzeit="12:00",
        dauer_min=60
    )
    kraft.add_uebung(Uebung(name="Bankdrücken", saetze=3, wdh=10, gewicht=60.0))
    kraft.add_uebung(Uebung(name="Kniebeugen", saetze=4, wdh=8, gewicht=80.0))

    # 2. Speichern
    repo.training_speichern(kraft)

    # 3. Datenbank-Prüfung
    with repo._get_connection() as conn:
        # Basisdaten prüfen
        res = conn.execute("SELECT typ FROM trainings").fetchone()
        assert res[0] == "Krafttraining"

        # Übungen (Details) prüfen
        cursor = conn.execute("SELECT name, gewicht FROM krafttraining_uebungen ORDER BY name")
        uebungen = cursor.fetchall()

        assert len(uebungen) == 2
        # Da wir nach Name sortiert haben: Bankdrücken kommt vor Kniebeugen
        assert uebungen[0][0] == "Bankdrücken"
        assert uebungen[0][1] == 60.0
        assert uebungen[1][0] == "Kniebeugen"
        assert uebungen[1][1] == 80.0

def test_analysis_tools(repo):
    # 1. Daten für Volumen-Test (Kraft)
    kraft = Krafttraining(nutzer_id=1, datum="2026-04-20", uhrzeit="10:00", dauer_min=60)
    # Volumen: 3 * 10 * 50kg = 1500kg
    kraft.add_uebung(Uebung(name="Bankdrücken", saetze=3, wdh=10, gewicht=50.0))
    repo.training_speichern(kraft)

    # 2. Daten für Pace-Test (Laufen)
    # 10km in 50 Min = 5.0 min/km
    lauf = Dauerlauf(distanz_km=10.0, hf_mittel=150, nutzer_id=1, datum="2026-04-21", uhrzeit="10:00", dauer_min=50)
    repo.training_speichern(lauf)

    # --- Prüfung Volumen ---
    volumen_data = repo.get_volumen_progression()
    assert len(volumen_data) == 1
    # volumen_data[0] ist ein Tuple: (Datum, Volumen)
    assert volumen_data[0][1] == 1500.0

    # --- Prüfung Pace ---
    pace_data = repo.get_dauerlauf_pace()
    assert len(pace_data) == 1
    # pace_data[0] ist ein Tuple: (Datum, Distanz, Dauer, Pace)
    assert pace_data[0][3] == 5.0

    # --- Prüfung Wochen-Zusammenfassung ---
    summary = repo.get_uebersicht_kw()
    assert len(summary) >= 1
    assert summary[0][1] == 2  # Kraft + Lauf
    # Wertung: 75.0 (Kraft) + 120.0 (Lauf: 10km * 12km/h) = 115.0
    assert summary[0][3] == 195.0


def test_training_wertung_speichern_und_zusammenfassung(repo):
    """Prüft die Speicherung der Wertung und die Aggregation in der KW-Übersicht."""
    # 1. Setup: Ein Sprint und ein Dauerlauf für denselben Zeitraum anlegen
    # Sprint: 10 * 30 = 300.0
    sprint = Sprint(anzahl=10, max_kmh=30.0, nutzer_id=1, datum="2026-04-25", uhrzeit="10:00", dauer_min=20)
    # Dauerlauf: 10km * 12km/h (60/50*10) = 120.0
    lauf = Dauerlauf(distanz_km=10.0, hf_mittel=150, nutzer_id=1, datum="2026-04-25", uhrzeit="12:00", dauer_min=50)

    repo.training_speichern(sprint)
    repo.training_speichern(lauf)

    # 2. Einzelprüfung in der DB
    with repo._get_connection() as conn:
        res = conn.execute("SELECT wertung FROM trainings WHERE typ='Sprint'").fetchone()
        assert res[0] == 300.0

    # 3. Prüfung der Wochen-Zusammenfassung (KW Übersicht)
    summary = repo.get_uebersicht_kw()

    assert len(summary) >= 1
    # Jetzt stimmt die Erwartung: 2 Trainings in dieser Woche
    assert summary[0][1] == 2
    # Gesamtdauer: 20 + 50 = 70
    assert summary[0][2] == 70
    # Gesamtwertung: 300.0 + 120.0 = 420.0
    assert summary[0][3] == 420.0

def test_user_management(repo):
    """Prüft das Anlegen, Abrufen und loeschen von Benutzern."""
    # 1. Benutzer anlegen
    u_id = repo.add_benutzer("Max Mustermann")
    assert u_id > 0

    # 2. Benutzer abrufen
    users = repo.get_alle_benutzer()
    # Erwartet werden 2: Der "Test User" aus der Fixture + "Max Mustermann"
    assert len(users) == 2

    # 3. Benutzer loeschen
    repo.loesche_benutzer(u_id)
    users_after = repo.get_alle_benutzer()
    assert len(users_after) == 1  # Der Fixture-User bleibt übrig


def test_cascade_delete_training(repo):
    """Prüft, ob beim loeschen eines Trainings auch die Details (Dauerlauf) verschwinden."""
    # 1. Setup: Training mit Details speichern
    lauf = Dauerlauf(distanz_km=12.0, hf_mittel=140, nutzer_id=1, datum="2026-04-20", uhrzeit="18:00", dauer_min=60)
    repo.training_speichern(lauf)

    # ID holen (es ist das erste Training)
    with repo._get_connection() as conn:
        t_id = conn.execute("SELECT id FROM trainings").fetchone()[0]

        # Check: Details sind da
        assert conn.execute("SELECT COUNT(*) FROM dauerlauf_details").fetchone()[0] == 1

        # 2. Training loeschen
        repo.loesche_training(t_id)

        # 3. Check: Sowohl Basis als auch Details müssen weg sein
        assert conn.execute("SELECT COUNT(*) FROM trainings").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM dauerlauf_details").fetchone()[0] == 0


def test_cascade_delete_user_complete(repo):
    """Prüft, ob beim loeschen eines Users ALLES (Trainings + Details) gelöscht wird."""
    # 1. Setup: User, Training und Krafttraining-Übungen
    u_id = repo.add_benutzer("Spezial-User")
    kraft = Krafttraining(nutzer_id=u_id, datum="2026-04-21", uhrzeit="10:00", dauer_min=30)
    kraft.add_uebung(Uebung(name="Squats", saetze=3, wdh=10, gewicht=100.0))
    repo.training_speichern(kraft)

    # 2. Benutzer loeschen
    repo.loesche_benutzer(u_id)

    # 3. Check: Tabellen müssen leer sein
    with repo._get_connection() as conn:
        # Es bleibt 1 Benutzer übrig (der aus der Fixture)
        assert conn.execute("SELECT COUNT(*) FROM benutzer").fetchone()[0] == 1
        # Aber die Trainings und Übungen des gelöschten Users müssen weg sein
        assert conn.execute("SELECT COUNT(*) FROM trainings").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM krafttraining_uebungen").fetchone()[0] == 0


def test_get_trainings_benutzer(repo):
    """Prüft, ob die Filterung nach Nutzer und Datum im Repo korrekt funktioniert."""
    # 1. Setup: Zwei User, verschiedene Trainings
    u1 = repo.add_benutzer("Nutzer 1")
    u2 = repo.add_benutzer("Nutzer 2")

    # Training für Nutzer 1
    repo.training_speichern(Dauerlauf(distanz_km=5.0,
        hf_mittel = 140,
        nutzer_id = u1,
        datum = "2026-05-01",
        uhrzeit = "10:00",
        dauer_min = 30
    ))
    # Training für Nutzer 2
    repo.training_speichern(Dauerlauf(
        distanz_km = 10.0,
        hf_mittel = 150,
        nutzer_id = u2,
        datum = "2026-05-01",
        uhrzeit = "11:00",
        dauer_min = 50
    ))
    # Training für Nutzer 1 an anderem Datum
    repo.training_speichern(Dauerlauf(distanz_km = 2.0,
        hf_mittel = 120,
        nutzer_id = u1,
        datum = "2026-05-02",
        uhrzeit = "9:00",
        dauer_min = 15
    ))

    # 2. Test: Alle Trainings von User 1
    alle_u1 = repo.get_trainings_benutzer(u1)
    assert len(alle_u1) == 2
    assert len(alle_u1[0]) == 5

    # 3. Test: Nur Trainings von User 1 an einem bestimmten Datum
    # Sicherstellen, dass wir das richtige Training im Filter-Resultat prüfen
    filter_u1 = repo.get_trainings_benutzer(u1, datum="2026-05-01")
    assert len(filter_u1) == 1
    # Index 2 ist das Datum, Index 1 der Typ
    assert filter_u1[0][2] == "2026-05-01"
    assert filter_u1[0][1] == "Dauerlauf"


def test_get_training_details(repo):
    """Prüft, ob die spezifischen Details (z.B. Distanz) korrekt geladen werden."""
    # Setup: Ein Training mit Details speichern
    lauf = Dauerlauf(distanz_km=10.0, hf_mittel=150, nutzer_id=1, datum="2026-04-25", uhrzeit="10:00", dauer_min=60)
    repo.training_speichern(lauf)

    # Die ID des gerade gespeicherten Trainings holen
    with repo._get_connection() as conn:
        t_id = conn.execute("SELECT id FROM trainings ORDER BY id DESC LIMIT 1").fetchone()[0]

    # Test: Details abrufen
    details = repo.get_training_details(t_id)

    assert details is not None
    assert details["Typ"] == "Dauerlauf"
    assert details["Distanz (km)"] == 10.0
    assert "Pace (min/km)" in details
    assert details["Herzfrequenz (Mittel)"] == 150