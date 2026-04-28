# repository.py

import os
import sqlite3

from models import Training, Dauerlauf, Sprint, Krafttraining


class TrainingRepository:
    """
    Verantwortlich für das dauerhafte Speichern von Daten mittels SQLite.

    Dient als Schnittstelle zwischen der Benutzeroberfläche FitnessCLI und der
    SQL-Datenbank fitness.db. Kapselt alle Datenbankzugriffe, initialisiert das Schema
    für die SQL-Tabellen und stellt sicher, dass die Fremdschlüssel-Prüfung aktiv ist.
    """

    def __init__(self, db_path="fitness.db", connection=None):
        """
        Initialisiert das Repository und stellt die Datenbank bereit.

        Args:
        db_path (str): Pfad zur SQLite-Datenbankdatei.
        connection: Optionale bestehende Verbindung (primär für In-Memory-Tests genutzt).
        """

        self.db_path = db_path
        self._shared_conn = connection
        self._init_db()

    def _get_connection(self):
        """
        Öffnet die Datenbank (zum Lesen und Schreiben).
        Sorgt dafür, dass die Fremdschlüssel-Unterstützung bei Verbindungsaufbau aktiviert wird.
        Diese ist in SQLite standardmäßig deaktiviert.
        """

        if (
            self._shared_conn
        ):  # Für :memory: Tests geben wir die geteilte Verbindung zurück
            return self._shared_conn

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """
        Liest aus 'schema.sql' die Struktur der Datenbank ein und erstellt die Tabellen.

        Ermittelt den Pfad zur Schema-Datei relativ zum Modulstandort, um eine robuste
        Initialisierung unabhängig davon, in welchem Verzeichnis in der Konsole sich der
        Benutzer befindet. Löst einen FileNotFoundError aus, falls die Datei fehlt.
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, "schema.sql")

        with self._get_connection() as conn:
            try:
                with open(
                    schema_path, "r", encoding="utf-8"
                ) as f:  # öffnet schema.sql im Lesemodus. with sorgt für das automatische Schließen, macht f.close() und conn.close() am Ende überflüssig
                    conn.executescript(
                        f.read()
                    )  # execute() führt einen SQL-Befehl aus, executescript kann mehrere ausführen
                    print("Tabellen erfolgreich initialisiert!")
                conn.commit()  # Änderungen dauerhaft speichern
            except FileNotFoundError:
                # Falls die Datei doch woanders liegt, hilft uns diese Fehlermeldung
                print(f"\nFEHLER: schema.sql wurde nicht gefunden unter: {schema_path}")
                raise

    def training_speichern(self, training: Training):
        """
        Persistiert ein Trainingsobjekt in der Datenbank fitness.db.

        Speichet die allgemeinen Daten werden in der Tabelle 'trainings'.
        Speichert die von der Trainingsart abhängigen Daten in eigenen Tabellen.

        Verwendet Parameterized Queries zum Schutz gegen SQL-Injection und stellt
        durch die Nutzung der lastrowid die korrekte Verknüpfung der Tabellen sicher.
        Verhindert das Speichern einer nicht unterstützen Traingsart durch TypeError.
        """

        with self._get_connection() as conn:
            cursor = (
                conn.cursor()
            )  # Während conn die Datenbank für uns öffnet, nimmt cursor die SQL-Befehle entgegen und führt sie aus.

            # 1. Basisdaten in 'trainings'
            cursor.execute(
                "INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung) VALUES (?, ?, ?, ?, ?, ?)",  # Hier setzt squlite die Werte ein. Die Fragezeichen sind Platzhalter. Sie verhindern SQL-Injektion: Das böswillige Nutzer SQL-Befehle z. B. in die Übungsnamen schreiben.
                (
                    training.nutzer_id,
                    training.__class__.__name__,
                    str(training.datum),
                    str(training.uhrzeit),
                    training.dauer_min,
                    training.berechne_wertung(),
                ),
            )
            t_id = (
                cursor.lastrowid
            )  # t_id wird zum Verknöüfen mit dem folgenden if-Blocks verwendet

            # 2. Spezifische Daten für die verschiedenen Arten von Trainings:

            if isinstance(training, Dauerlauf):
                cursor.execute(
                    "INSERT INTO dauerlauf_details (training_id, distanz_km,  hf_mittel) VALUES (?, ?, ?)",
                    (t_id, training.distanz_km, training.hf_mittel),
                )

            elif isinstance(training, Sprint):
                cursor.execute(
                    "INSERT INTO sprint_details (training_id, anzahl, max_kmh) VALUES (?, ?, ?)",
                    (t_id, training.anzahl, training.max_kmh),
                )

            elif isinstance(training, Krafttraining):
                for u in training.uebungen:
                    cursor.execute(
                        "INSERT INTO krafttraining_uebungen (training_id, name, saetze, wdh, gewicht) VALUES (?, ?, ?, ?, ?)",
                        (t_id, u.name, u.saetze, u.wdh, u.gewicht),
                    )

            else:
                # Bietet Schutz vor Klassen, die in models.py hinzugefügt, aber in dieser Methode vergessen wurden
                raise TypeError(f"Unbekannter Trainingstyp: {type(training).__name__}")

            conn.commit()

    def get_trainings_benutzer(self, nutzer_id: int, datum: str = None):
        """Holt alle Trainings eines Nutzers, optional gefiltert nach Datum."""
        query = "SELECT id, typ, datum, dauer_min, wertung FROM trainings WHERE nutzer_id = ?"
        params = [nutzer_id]
        if datum:
            query += " AND datum = ?"
            params.append(datum)

        with self._get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def get_volumen_progression(self):
        """Berechnet das Gesamtvolumen (Sätze * Wdh * Gewicht) pro Krafttraining-Session."""
        query = """
            SELECT t.datum, SUM(k.saetze * k.wdh * k.gewicht) as volumen
            FROM trainings t
            JOIN krafttraining_uebungen k ON t.id = k.training_id
            GROUP BY t.id
            ORDER BY t.datum ASC
        """
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    def get_dauerlauf_pace(self):
        """Holt Dauer und Distanz für alle Dauerläufe und berechnet die Pace."""
        query = """
            SELECT t.datum, d.distanz_km, t.dauer_min,
                   (CAST(t.dauer_min AS REAL) / d.distanz_km) as pace
            FROM trainings t
            JOIN dauerlauf_details d ON t.id = d.training_id
            ORDER BY t.datum ASC
        """
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    def get_uebersicht_kw(self):
        """Aggregiert Anzahl der Trainings, Gesamtdauer und Gesamtwertung pro Kalenderwoche."""
        query = """
            SELECT strftime('%Y-%W', datum) as woche,
                   COUNT(id) as anzahl_trainings,
                   SUM(dauer_min) as gesamt_min,
                   ROUND(SUM(wertung), 1) as gesamt_wertung
            FROM trainings
            GROUP BY woche
            ORDER BY woche DESC
        """
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    def get_training_details(self, training_id: int):
        """Holt alle spezifischen Details zu einer Training-ID."""
        with self._get_connection() as conn:
            # 1. Typ bestimmen
            res = conn.execute(
                "SELECT typ FROM trainings WHERE id = ?", (training_id,)
            ).fetchone()
            if not res:
                return None

            typ = res[0]
            details = {"Typ": typ}

            # 2. Spezifische Daten je nach Typ laden
            if typ == "Dauerlauf":
                # Hol dir Dauer (aus trainings) und Distanz/Puls (aus Details) in einem Rutsch
                row = conn.execute(
                    """
                                SELECT d.distanz_km, d.hf_mittel, t.dauer_min 
                                FROM dauerlauf_details d
                                JOIN trainings t ON d.training_id = t.id
                                WHERE d.training_id = ?
                            """,
                    (training_id,),
                ).fetchone()

                if row:
                    distanz, puls, dauer = row[0], row[1], row[2]
                    details["Distanz (km)"] = distanz
                    details["Puls (Mittel)"] = puls

                    # Pace sicher in Python berechnen (verhindert Division durch Null)
                    if distanz > 0:
                        details["Pace (min/km)"] = round(dauer / distanz, 2)
                    else:
                        details["Pace (min/km)"] = 0

            elif typ == "Sprint":
                row = conn.execute(
                    "SELECT anzahl, max_kmh FROM sprint_details WHERE training_id = ?",
                    (training_id,),
                ).fetchone()
                if row:
                    details["Anzahl Sprints"] = row[0]
                    details["Max km/h"] = row[1]

            elif typ == "Krafttraining":
                rows = conn.execute(
                    "SELECT name, saetze, wdh, gewicht FROM krafttraining_uebungen WHERE training_id = ?",
                    (training_id,),
                ).fetchall()
                details["Übungen"] = rows  # Liste von Übungen für tabulate

            return details

    def add_benutzer(self, name: str) -> int:
        """Legt einen neuen Benutzer an und gibt die generierte ID zurück."""
        query = "INSERT INTO benutzer (name) VALUES (?)"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (name,))
            conn.commit()
            return cursor.lastrowid

    def get_alle_benutzer(self):
        """Holt eine Liste aller registrierten Benutzer."""
        query = "SELECT id, name FROM benutzer ORDER BY id ASC"
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    def loesche_training(self, training_id: int):
        """
        Löscht ein Training anhand der ID.
        Durch 'ON DELETE CASCADE' im SQL (Foreign Keys) werden die Details automatisch mitgelöscht.
        """
        query = "DELETE FROM trainings WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (training_id,))
            conn.commit()

    def loesche_benutzer(self, user_id: int):
        """Löscht einen Benutzer und alle zugehörigen Trainings."""
        query = "DELETE FROM benutzer WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (user_id,))
            conn.commit()