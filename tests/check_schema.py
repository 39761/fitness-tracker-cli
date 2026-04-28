# tests/check_schema.py
# Aufruf:  # tests/check_schema.py
#
# # Aufruf vom Hauptpfad: python -m tests.check_schema

import sqlite3
import os


def run_schema_check():
    print("--- Starte erweiterten Schema-Check ---")

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # Pfad-Handling
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SCHEMA_PATH = os.path.join(BASE_DIR, "..", "schema.sql")

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        cursor.executescript(schema_sql)
        print("Erfolg: 'schema.sql' ist syntaktisch korrekt.")

        # 1. Tabellen-Vollständigkeit prüfen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tabellen = [t[0] for t in cursor.fetchall()]
        erwartet = ["benutzer", "trainings", "dauerlauf_details", "sprint_details", "krafttraining_uebungen"]

        for t in erwartet:
            if t in tabellen:
                print(f"Tabelle '{t}': OK")
            else:
                print(f"Tabelle '{t}': FEHLT!")

        # 2. Spezifischer Spalten-Check für 'wertung'
        if "trainings" in tabellen:
            cursor.execute("PRAGMA table_info('trainings');")
            spalten = [s[1] for s in cursor.fetchall()]
            if "wertung" in spalten:
                print("Spalte 'wertung' in Tabelle 'trainings' gefunden.")
            else:
                print("Spalte 'wertung' FEHLT in Tabelle 'trainings'!")

        # 3. Kaskaden-Prüfung (Dein Loop war gut, hier etwas präziser)
        cursor.execute("PRAGMA foreign_key_list('trainings');")
        fks = cursor.fetchall()
        # Index 2 ist die Parent-Tabelle, Index 6 ist on_delete
        if any(fk[2] == 'benutzer' and fk[6] == 'CASCADE' for fk in fks):
            print("Check: ON DELETE CASCADE (benutzer -> trainings) erfolgreich erkannt.")
        else:
            print("⚠Warnung: CASCADE-Regel für benutzer -> trainings nicht gefunden.")

    except sqlite3.Error as e:
        print(f"SQL-Fehler: {e}")
    except FileNotFoundError:
        print(f"Datei nicht gefunden unter: {SCHEMA_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    run_schema_check()