-- schema.sql

CREATE TABLE IF NOT EXISTS benutzer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nutzer_id INTEGER NOT NULL,
    typ TEXT NOT NULL,
    datum TEXT NOT NULL,
    uhrzeit TEXT NOT NULL,
    dauer_min INTEGER NOT NULL,
    wertung REAL,
    FOREIGN KEY (nutzer_id) REFERENCES benutzer (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dauerlauf_details (
    training_id INTEGER PRIMARY KEY,
    distanz_km REAL NOT NULL,
    hf_mittel INTEGER,
    FOREIGN KEY (training_id) REFERENCES trainings (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sprint_details (
    training_id INTEGER PRIMARY KEY,
    anzahl INTEGER NOT NULL,
    max_kmh REAL NOT NULL,
    FOREIGN KEY (training_id) REFERENCES trainings (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS krafttraining_uebungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    saetze INTEGER NOT NULL,
    wdh INTEGER NOT NULL,
    gewicht REAL NOT NULL,
    FOREIGN KEY (training_id) REFERENCES trainings (id) ON DELETE CASCADE
);