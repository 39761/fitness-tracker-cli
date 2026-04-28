# Fitness-Tracker CLI

Ein Python-basiertes Command-Line-Interface zur Dokumentation und Analyse sportlicher Leistungen. Das Tool wurde mit Fokus auf eine modulare Architektur (**Separation of Concerns**) und eine optimierte Benutzererfahrung bei der Dateneingabe entwickelt.

## Key Features

* **Multi-User-System:** Verwaltung getrennter Profile mit individuellen Trainingsverläufen.
* **Differenzierte Trainingsarten:** Spezifische Erfassung für Dauerlauf, Sprint und Krafttraining.
* **Intelligentes Scoring:** Automatische Berechnung einer "Wertung" basierend auf Leistungsparametern (z. B. Kraft-Volumen oder Pace beim Laufen).
* **Analyse-Tools:** Fortschrittsberichte über Wochen-Zusammenfassungen, Volumen-Progression und Pace-Entwicklung.
* **Datenintegrität:** Einsatz von SQLite mit Foreign Key Constraints und robuster Eingabevalidierung.

## Tech Stack

* **Sprache:** Python 3.x
* **Datenbank:** SQLite3
* **Bibliotheken:** `tabulate` (CLI-Formatierung), `pytest` (Testing)

---

## Schnellstart für Reviewer

Um das Projekt ohne manuelles Eintippen von Daten sofort testen zu können, ist ein Demo-Skript enthalten:

1.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Demo-Daten generieren:**
    ```bash
    python setup_testdata.py
    ```
    *Erstellt eine `fitness.db` mit einem aktiven Nutzer ("Max Mustermann") und Beispiel-Trainings.*
3.  **Anwendung starten:**
    ```bash
    python cli.py
    ```

---

## Projektstruktur

* `cli.py`: Präsentationsschicht & Menüführung.
* `repository.py`: Data Access Layer (Kapselung der SQL-Logik).
* `models.py`: Domänenmodelle & Geschäftslogik (OOP).
* `schema.sql`: Initiales Datenbank-Design (DDL) inklusive Relationen und Cascades.
* `setup_testdata.py`: Utility-Skript zur schnellen Generierung einer Testumgebung.
* `requirements.txt`: Liste der externen Abhängigkeiten für eine einfache Installation.
* `tests/`: Verzeichnis mit Unit- und Integrationstests zur Sicherstellung der Code-Qualität.

---

## Design-Entscheidungen (Highlights)

### UX-Optimierung (Nummernblock-Eingabe)
Besonderes Augenmerk liegt auf der Effizienz der Dateneingabe. Die Validierungsmethoden in der `cli.py` bereinigen Trennzeichen automatisch. Das erlaubt die Eingabe von Datum und Uhrzeit ohne Sonderzeichen (z. B. `20260427` statt `2026-04-27`), was die Nutzung über den Nummernblock massiv beschleunigt.

### Datenintegrität & Kaskadierung
Durch konsequente Nutzung von `FOREIGN KEY` Constraints und `ON DELETE CASCADE` im Datenbankschema wird sichergestellt, dass beim Löschen eines Benutzers oder Trainings keine verwaisten Einträge in den Detail-Tabellen verbleiben.

### Defensive Programmierung
Alle numerischen Eingaben werden auf logische Korrektheit geprüft (z. B. Ausschluss von Nullwerten bei Divisionen), um Laufzeitfehler wie `ZeroDivisionError` oder `TypeError` bei der Analyse-Berechnung zu verhindern.

---

## Testing

Die Testsuite im Ordner `tests/` stellt die Stabilität der Kernfunktionen sicher:

* `test_models.py`: Unit-Tests für die Berechnungslogik (Scoring-Formeln).
* `test_repository.py`: Datenbank-Tests (CRUD-Operationen und Joins).
* `test_integration.py`: Überprüfung des Zusammenspiels zwischen Repository und Modellen.
* `check_schema.py`: Validierung der aktuellen Tabellenstruktur gegen die `schema.sql`.

**Tests ausführen:**
```bash
python -m pytest tests/ -v
```

---

## Lizenz

Dieses Projekt wurde zu Bildungszwecken im Rahmen eines Portfolios erstellt.
Frei zur Nutzung und Modifikation.
