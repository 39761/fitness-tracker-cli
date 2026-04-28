# Aufruf: python -m pytest -s tests/test_models.py

from models import Benutzer, Dauerlauf, Sprint, Krafttraining, Uebung

def test_representation():
    """
        Überprüft die textuelle Objektdarstellung (String-Repräsentation) der Domänenmodelle.

        Dieser Test zeigt visuell, ob die '__repr__'-Methoden der Klassen Benutzer,
        Dauerlauf, Sprint, Krafttraining und Übung aussagekräftige Informationen für
        das Debugging liefern. Er simuliert zudem die Aggregation von verschiedenen
        Trainingseinheiten innerhalb eines Benutzer-Objekts, um die korrekte
        Verschachtelung der Datenstrukturen zu demonstrieren.
        """

    print("--- Starte Repräsentations-Test ---\n")

    # 1. Benutzer erstellen
    user = Benutzer(name="Max Mustermann", nutzer_id=1)

    # 2. Verschiedene Trainingsarten erstellen
    lauf = Dauerlauf(
        distanz_km=10.5,
        hf_mittel=145,
        nutzer_id=1,
        datum="2026-04-21",
        uhrzeit="18:00",
        dauer_min=60,
        training_id=101
    )

    sprint = Sprint(
        anzahl=10,
        max_kmh=32.5,
        nutzer_id=1,
        datum="2026-04-22",
        uhrzeit="10:00",
        dauer_min=30,
        training_id=102
    )

    # 3. Krafttraining mit Übungen erstellen
    kraft = Krafttraining(
        nutzer_id=1,
        datum="2026-04-23",
        uhrzeit="17:00",
        dauer_min=90,
        training_id=103
    )
    kraft.add_uebung(Uebung("Bankdrücken", 3, 10, 60.0))
    kraft.add_uebung(Uebung("Kniebeugen", 4, 8, 80.0))

    # 4. Trainings dem Benutzer zuordnen
    user.add_training(lauf)
    user.add_training(sprint)
    user.add_training(kraft)

    # --- Die Ausgabe (Hier siehst du deine __repr__ Methoden in Aktion) ---
    print(f"Benutzer-Objekt: {user}")
    print("\nTrainings-Historie des Benutzers:")
    for t in user.trainings:
        print(f"  - {t}")

        # Falls es ein Krafttraining ist, zeige auch die Übungen darin
        if isinstance(t, Krafttraining):
            for u in t.uebungen:
                print(f"      * {u}")