# setup_testdata.py
# Aufruf: python setup_testdata.py

import os
import sqlite3


def setup_demo_data():
    db_name = "fitness.db"

    # 1. Alte DB löschen für einen sauberen Neustart
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Alte Datenbank '{db_name}' wurde entfernt.")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 2. Schema erstellen (Tabellen)
    print("Erstelle Tabellen...")
    cursor.executescript("""
        CREATE TABLE benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nutzer_id INTEGER,
            typ TEXT,
            datum TEXT,
            uhrzeit TEXT,
            dauer_min INTEGER,
            wertung REAL,
            FOREIGN KEY(nutzer_id) REFERENCES benutzer(id) ON DELETE CASCADE
        );

        CREATE TABLE dauerlauf_details (
            training_id INTEGER PRIMARY KEY,
            distanz_km REAL,
            hf_mittel INTEGER,
            FOREIGN KEY(training_id) REFERENCES trainings(id) ON DELETE CASCADE
        );

        CREATE TABLE sprint_details (
            training_id INTEGER PRIMARY KEY,
            anzahl INTEGER,
            max_kmh REAL,
            FOREIGN KEY(training_id) REFERENCES trainings(id) ON DELETE CASCADE
        );

        CREATE TABLE krafttraining_uebungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_id INTEGER,
            name TEXT,
            saetze INTEGER,
            wdh INTEGER,
            gewicht REAL,
            FOREIGN KEY(training_id) REFERENCES trainings(id) ON DELETE CASCADE
        );
    """)

    # 3. Test-Benutzer anlegen
    cursor.execute("INSERT INTO benutzer (name) VALUES (?)", ("Max Mustermann",))
    u_id = cursor.lastrowid

    # 4. Musterdaten für Trainings generieren
    print("Generiere Musterdaten...")

    # --- Dauerlauf ---
    # 10km in 50 Min = 12 km/h -> Wertung 120.0
    cursor.execute("""
        INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung)
        VALUES (?, 'Dauerlauf', '2026-04-20', '10:00', 50, 120.0)
    """, (u_id,))
    t_id = cursor.lastrowid
    cursor.execute("INSERT INTO dauerlauf_details VALUES (?, 10.0, 155)", (t_id,))

    # --- Sprint ---
    # 10 Sprints * 32.5 km/h = 325.0
    cursor.execute("""
        INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung)
        VALUES (?, 'Sprint', '2026-04-22', '18:30', 20, 325.0)
    """, (u_id,))
    t_id = cursor.lastrowid
    cursor.execute("INSERT INTO sprint_details VALUES (?, 10, 32.5)", (t_id,))

    # --- Krafttraining ---
    # Bankdrücken: 3 * 10 * 60 = 1800kg
    # Kniebeugen: 3 * 12 * 80 = 2880kg
    # Gesamtvolumen: 4680kg / 100 = 46.8 Wertung
    cursor.execute("""
        INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung)
        VALUES (?, 'Krafttraining', '2026-04-24', '17:00', 60, 234)
    """, (u_id,))
    t_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO krafttraining_uebungen (training_id, name, saetze, wdh, gewicht) VALUES (?, ?, ?, ?, ?)",
        (t_id, "Bankdrücken", 3, 10, 60.0))
    cursor.execute(
        "INSERT INTO krafttraining_uebungen (training_id, name, saetze, wdh, gewicht) VALUES (?, ?, ?, ?, ?)",
        (t_id, "Kniebeugen", 3, 12, 80.0))

    conn.commit()
    conn.close()
    print("\nErfolg: 'fitness.db' wurde mit Musterdaten erstellt.")
    print("Du kannst jetzt 'python cli.py' starten und den Nutzer 'Max Mustermann' wählen.")


if __name__ == "__main__":
    setup_demo_data()