# Fitness-Tracker CLI

Ein Python-basiertes Command-Line-Interface zur Dokumentation und Analyse sportlicher Leistungen. Das Tool wurde mit Fokus auf eine modulare Architektur (**Separation of Concerns**), objektorientiertes Design und eine effiziente Benutzerführung bei der Dateneingabe entwickelt.

## Key Features

* **Multi-User-System:** Verwaltung getrennter Profile mit individuellen Trainingsverläufen.
* **Differenzierte Trainingsarten:** Spezifische Erfassung für Dauerlauf, Sprint und Krafttraining.
* **Objektorientiertes Domänenmodell:** Einsatz von abstrakten Basisklassen, Vererbung und Komposition zur Modellierung der Trainingsarten.
* **Intelligentes Scoring:** Automatische Berechnung einer Wertung basierend auf Leistungsparametern (Dauerlauf-Geschwindigkeit, Sprint-Maximalgeschwindigkeit und Krafttrainings-Volumen).
* **Analyse-Tools:** Fortschrittsberichte über Wochen-Zusammenfassungen, Volumen-Progression und Pace-Entwicklung.
* **Datenintegrität:** Einsatz von SQLite mit `FOREIGN KEY` Constraints, `ON DELETE CASCADE` und robuster Eingabevalidierung.
* **Testbare Architektur:** Klare Trennung zwischen CLI, Geschäftslogik und Persistenzschicht zur Unterstützung der automatisierten Tests.
* **[In Planung] Web-Schnittstelle (API):** Erweiterbarkeit durch geplante REST-API auf Basis von FastAPI.

## Tech Stack

* **Sprache:** Python 3.x
* **Datenbank:** SQLite3
* **Bibliotheken:** `tabulate` (CLI-Formatierung), `pytest` (Testing)
* **Modellierung & Dokumentation:** PlantUML
* **[In Planung] Zusätzliche Bibliotheken:** `FastAPI` (REST-API) und `Pydantic` (Datenvalidierung)

---

## Schnellstart

**Voraussetzungen:** Python 3.x, `pip`

Um das Projekt ohne manuelles Erfassen von Trainingsdaten direkt testen zu können, ist ein Skript zur Generierung relationaler Demo-Daten enthalten.

1. **Repository klonen und Abhängigkeiten installieren**
    ```bash
    git clone https://github.com/39761/fitness-tracker-cli
    cd cv_training_app
    pip install -r requirements.txt
    ```

2. **Demo-Daten generieren**
    ```bash
    python setup_testdata.py
    ```

    Dadurch wird lokal eine `fitness.db` mit Beispielstrukturen und Trainingsdaten erzeugt.

3. **Anwendung starten**
    ```bash
    python cli.py
    ```

---

## Projektstruktur

```text
cv_training_app/
│   cli.py                        # Präsentationsschicht und Menüführung des CLI
│   models.py                     # Objektorientiertes Domänenmodell & Geschäftslogik
│   repository.py                 # Data Access Layer / SQLite-Kommunikation
│   schema.sql                    # SQL-DDL inkl. Relationen und Cascades
│   setup_testdata.py             # Generierung relationaler Demo-Daten
│   requirements.txt              # Externe Projektabhängigkeiten
│   README.md                     # Projektdokumentation
│
├───docs
│       architecture.puml         # PlantUML-Quelle des Sequenzdiagramms für den Programmablauf
│       models.puml               # PlantUML-Quelle des Klassendiagramms für das Domänenmodell
│       *.svg                     # Gerenderte Diagramme
│
└───tests
        check_schema.py           # Validierung der Live-Datenbank gegen schema.sql
        test_integration.py       # Integrationstests für Repository & Modelle
        test_models.py            # Unit-Tests der Berechnungslogik
        test_repository.py        # Tests der Datenbankoperationen
```

---

## Design-Entscheidungen (Highlights)

### Schichtenarchitektur & Separation of Concerns

Die Anwendung trennt Benutzeroberfläche (`cli.py`), Geschäftslogik (`models.py`) und Persistenz (`repository.py`) konsequent voneinander.  
Dadurch bleiben Komponenten unabhängig testbar und Erweiterungen — beispielsweise eine zukünftige Web-API — können ohne tiefgreifende Änderungen integriert werden.

### Objektorientiertes Domänenmodell

Die Trainingsarten basieren auf einer abstrakten Basisklasse `Training`.  
Spezialisierungen wie `Dauerlauf`, `Sprint` und `Krafttraining` implementieren eigene Berechnungslogiken für Trainingswertungen.

Für Krafttraining wird zusätzlich das Prinzip der **Komposition** genutzt:  
Ein `Krafttraining` aggregiert mehrere `Uebung`-Objekte mit eigenem Trainingsvolumen.

### UX-Optimierung der Dateneingabe

Die CLI erlaubt flexible Eingaben für Datum und Uhrzeit ohne Sonderzeichen.  
Dadurch können viele Eingaben effizient über den Nummernblock erfolgen:

* `20260427` → `2026-04-27`
* `1830` → `18:30`

Zusätzlich akzeptiert die numerische Eingabe sowohl Punkte als auch deutsche Kommata (`10,5`).

### Datenintegrität & Kaskadierung

Durch konsequente Nutzung von `FOREIGN KEY` Constraints und `ON DELETE CASCADE` wird sichergestellt, dass beim Löschen von Benutzern oder Trainings keine verwaisten Datensätze verbleiben.

### Defensive Programmierung

Numerische Eingaben werden validiert, um fehlerhafte Zustände und Laufzeitfehler zu verhindern:

* Verhinderung negativer Werte
* Schutz vor Division durch Null
* Datums- und Uhrzeitvalidierung
* Typvalidierung für numerische Eingaben

---

## Architektur & Dokumentation

Die Systemarchitektur und das Domänenmodell wurden zusätzlich mit PlantUML dokumentiert.

### Domänenmodell (Klassendiagramm)

Das Klassendiagramm visualisiert die objektorientierte Struktur der Anwendung mit:

* abstrakter Basisklasse
* Vererbung der Trainingsarten
* Komposition innerhalb des Krafttrainings
* Aggregation der Trainings pro Benutzer

![Klassendiagramm](./docs/models.svg)

### System-Ablauf (Sequenzdiagramm)

Das Sequenzdiagramm zeigt den Datenfluss zwischen:

* Benutzeroberfläche (`CLI`)
* Repository-Schicht
* SQLite-Datenbank

Die CLI kommuniziert dabei ausschließlich über das Repository mit der Persistenzschicht.

![Sequenzdiagramm](./docs/architecture.svg)

---

## Testing

Die Testsuite im Ordner `tests/` überprüft zentrale Komponenten der Anwendung automatisiert.

### Enthaltene Tests

* `test_models.py`
  * Unit-Tests der Wertungs- und Berechnungslogik

* `test_repository.py`
  * CRUD-Operationen
  * Datenbankzugriffe
  * Relationen und Joins
  * Fremdschlüssel-Constraints und Löschkaskade
  
* `test_integration.py`
  * Zusammenspiel von Repository und Domänenmodellen

* `check_schema.py`
  * Validierung der tatsächlichen Tabellenstruktur gegen `schema.sql`

### Tests ausführen

```bash
python -m pytest tests/ -v
```

---

## Hinweise zum Projektstatus

Dieses Projekt entstand als Lern- und Portfolio-Projekt mit Fokus auf:

* objektorientierte Softwareentwicklung
* relationale Datenmodellierung
* Testbarkeit
* saubere Schichtenarchitektur
* defensive Eingabevalidierung

Die geplante Erweiterung um eine REST-API wurde architektonisch bereits berücksichtigt, ist jedoch noch nicht implementiert.

---

## Lizenz

Dieses Projekt wurde zu Bildungs- und Portfoliozwecken erstellt.

Freie Nutzung und Modifikation für Lernzwecke.
