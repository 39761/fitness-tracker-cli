# cli.py
# Aufruf mit python cli.py


import os
import sys
from datetime import datetime

from tabulate import tabulate

from models import Dauerlauf, Sprint, Krafttraining, Uebung
from repository import TrainingRepository


class FitnessCLI:
    """Verantwortlich für die Benutzeroberfläche des Fitness-Trackers. Verarbeitet
    und validiert Benutzereingaben, dient als Schnittstelle zwischen Benutzer und TrainingRepository.
    """

    def __init__(self):
        self.repo = TrainingRepository()
        self._aktiver_nutzer_id = None
        self._aktiver_nutzer_name = None

    @property
    def aktiver_nutzer_id(self):
        """Ermöglicht den Lesezugriff auf die ID des aktiven Nutzers von außen."""
        return self._aktiver_nutzer_id

    @property
    def aktiver_nutzer_name(self):
        """Ermöglicht den Lesezugriff auf den Namen des aktiven Nutzers von außen."""
        return self._aktiver_nutzer_name

    def _clear(self):
        """Leert das Terminal-Fenster, damit Header und Menü immer ganz oben erscheinen."""
        os.system("cls" if os.name == "nt" else "clear")

    def _header(self, titel):
        """Zeigt ganz oben im Terminal-Fenster Benutzername und -ID an."""
        self._clear()
        print("=" * 40)
        print(f"{titel:^40}")
        print("=" * 40)
        if self.aktiver_nutzer_name:
            print(
                f"Aktueller Nutzer: {self.aktiver_nutzer_name} (ID: {self.aktiver_nutzer_id})\n"
            )

    def _input_int(self, prompt, allow_zero=False):
        """Erzwingt die Eingabe einer positiven Ganzzahl durch den Benutzer und fragt
        nach, bis eine gültige Eingabe erfolgt ist."""
        while True:
            try:
                raw_input = input(prompt).strip()
                val = int(raw_input)

                if val < 0:
                    print("Bitte geben Sie eine positive Zahl ein.")
                    continue

                if val == 0 and not allow_zero:
                    print("Eingabe darf nicht 0 sein.")
                    continue

                return val
            except ValueError:
                print("Bitte geben Sie eine positive Ganzzahl ein.")

    def _input_float(self, prompt):
        """Erzwingt die Eingabe einer positiven Fließkommazahl durch den Benutzer.
        Fragt nach, bis eine gültige Eingabe erfolgt ist.
        Akzeptiert die Verwendung von Punkten und Kommata."""
        while True:
            try:
                # .replace erlaubt dem Nutzer auch das deutsche Komma
                val = float(input(prompt).replace(",", "."))
                if val > 0:
                    return val
                print("Bitte einen Wert größer als 0 eingeben.")
            except ValueError:
                print("Bitte eine Zahl eingeben (z.B. 10.5).")

    def _input_date(self, prompt):
        """Ermöglicht flexible Datumseingabe (mit/ohne Trenner) für bessere UX.
        Akzeptiert verschiedene Trennzeichen: '2026-04-27', '20260427' oder '2026.04.27'.
        """
        while True:
            val = input(prompt).strip().replace("-", "").replace(".", "")
            if not val:
                return datetime.now().strftime("%Y-%m-%d")

            # Prüfen, ob es genau 8 Ziffern sind (z.B. 20260427)
            if len(val) == 8 and val.isdigit():
                formatted = f"{val[:4]}-{val[4:6]}-{val[6:]}"
                try:
                    # Validierung des Datums (verhindert 20261345)
                    clean_date = datetime.strptime(formatted, "%Y-%m-%d")
                    return clean_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass  # Geht zur Fehlermeldung unten

            print("Ungültig. Bitte JJJJMMDD oder JJJJ-MM-DD nutzen.")

    def _input_time(self, prompt):
        """Ermöglicht schnelle Uhrzeiteingabe ohne Sonderzeichen.
        Akzeptiert HHMM, HH:MM oder HH.MM und validiert die Logik."""
        while True:
            val = input(prompt).strip().replace(":", "").replace(".", "")
            if not val:
                return datetime.now().strftime("%H:%M")

            # Prüfen auf 4 Ziffern (z.B. 1830)
            if len(val) == 4 and val.isdigit():
                formatted = f"{val[:2]}:{val[2:]}"
                try:
                    # Validierung (verhindert 25:99)
                    clean_time = datetime.strptime(formatted, "%H:%M")
                    return clean_time.strftime("%H:%M")
                except ValueError:
                    pass

            print("Ungültig. Bitte HHMM oder HH:MM nutzen.")

    def benutzer_verwalten(self):
        """
        Bietet ein interaktives Menü zur Verwaltung der Benutzerprofile.

        Zeigt die Profile an und ermöglicht den Benutzerwechsel, das Erstellen neuer und das
        Löschen bestehender Nutzer. Erzwingt die Auswahl eines Nutzers, bevor in das Hauptmenü
        gewechselt werden kann.
        Beim Löschen eines Benutzers wird eine Sicherheitsabfrage durchgeführt, um irrtümliches
        Löschen zu verhindern.

        Verwendet TrainingRepository für persistente Änderungen.
        """
        while True:
            self._header("BENUTZER VERWALTEN")
            users = self.repo.get_alle_benutzer()

            if users:
                print(tabulate(users, headers=["ID", "Name"], tablefmt="psql"))
            else:
                print("Keine Benutzer vorhanden.")

            print(
                "\n[n] Neu anlegen | [ID] Wählen | [d ID] Löschen | [q] Zurück [x] Beenden"
            )
            wahl = input("\nAuswahl > ").lower()

            if wahl == "q" and self._aktiver_nutzer_id:
                break
            elif wahl == "n":
                name = input("Name: ").strip()
                if name:
                    self.repo.add_benutzer(name)
                    print(f"Benutzer {name} angelegt.")
                else:
                    print("Name darf nicht leer sein.")
                input("[Enter]")
            elif wahl.startswith("d "):
                try:
                    target_id = int(wahl.split()[1])
                    # Den Namen für die Abfrage finden
                    user_to_delete = next(
                        (u[1] for u in users if u[0] == target_id), None
                    )

                    if user_to_delete:
                        confirm = input(
                            f"️Soll '{user_to_delete}' (ID: {target_id}) wirklich gelöscht werden? Alle Trainings gehen verloren! (j/n): "
                        ).lower()
                        if confirm == "j":
                            self.repo.loesche_benutzer(target_id)
                            print(f"Benutzer '{user_to_delete}' gelöscht.")
                            # Falls der aktive Nutzer gelöscht wurde, Reset
                            if target_id == self._aktiver_nutzer_id:
                                self._aktiver_nutzer_id, self._aktiver_nutzer_name = (
                                    None,
                                    None,
                                )
                        else:
                            print("Abbruch. Benutzer wurde nicht gelöscht.")
                    else:
                        print("ID nicht gefunden.")
                except (ValueError, IndexError):
                    print("Ungültiges Format. Nutzen Sie 'd ID' (z.B. 'd 1').")
            elif wahl == "x":
                print("Programm wird beendet...")
                sys.exit()
            else:
                try:
                    u_id = int(wahl)
                    match = [u for u in users if u[0] == u_id]
                    if match:
                        self._aktiver_nutzer_id, self._aktiver_nutzer_name = match[0]
                        break
                except ValueError:
                    pass

    def hauptmenue(self):
        """
        Dient als Navigationszentrale des Fitness-Trackers.

        Beinhaltet die Hauptschleife der CLI.
        Ermöglicht dem Benutzer das Aufrufen der spezifischen Methoden:
        Aufzeichnen, Anzeigen, Analysieren und Löschen von Trainings.
        Ermöglicht den Wechsel zur Benutzerverwaltung und das Beenden des Programms.
        """

        while True:
            self._header("FITNESS-TRACKER CLI v1.0")
            print("1. Neues Training aufzeichnen")
            print("2. Trainings anzeigen (Tag/Gesamt)")
            print("3. Analyse & Statistiken")
            print("4. Training löschen")
            print("5. Benutzer wechseln / anlegen")
            print("0. Beenden")

            wahl = input("\nAuswahl > ")

            if wahl == "1":
                self.training_aufzeichnen()
            elif wahl == "2":
                self.trainings_anzeigen()
            elif wahl == "3":
                self.analyse_menue()
            elif wahl == "4":
                self.training_loeschen()
            elif wahl == "5":
                self.benutzer_verwalten()
            elif wahl == "0":
                break

    def training_aufzeichnen(self):
        """
        Dient der Aufzeichnung eines Trainings durch den Benutzer.

        Ermöglicht die Wahl zwischen verschiedenen Arten von Trainings:
        Dauerlauf, Sprint und Krafttraining.
        Fragt allgemeine Daten ab: Datum, Uhrzeit und Dauer des Trainings.
        Je nach Auswahl werden Trainingsspezifische Daten abgefragt.
        Bei Wahl von "Krafttraining" können innerhalb einer interaktiven Schleife
        einzelne Übungskomponenten gewählt und auch frei hinzugefügt werden.

        Das fertige Objekt wird über TrainingRepository dauerhaft gespeichert.
        """
        self._header("NEUES TRAINING")
        print("1. Dauerlauf | 2. Sprint | 3. Krafttraining | 0. Abbrechen")
        wahl = input("\nAuswahl > ")
        if wahl == "0":
            return

        datum = self._input_date("Datum (JJJJ-MM-DD) [Enter für Heute]: ")
        uhrzeit = self._input_time("Uhrzeit (HH:MM) [Enter für Jetzt]: ")
        dauer = self._input_int("Dauer (Min): ")

        params = {
            "nutzer_id": self.aktiver_nutzer_id,
            "datum": datum,
            "uhrzeit": uhrzeit,
            "dauer_min": dauer,
        }

        if wahl == "1":
            training = Dauerlauf(
                distanz_km=self._input_float("Distanz (km): "),
                hf_mittel=self._input_int("Mittlere Herzfrequenz (0 für Skip): ", allow_zero=True)
                or None,
                **params,
            )
        elif wahl == "2":
            training = Sprint(
                anzahl=self._input_int("Sprints: "),
                max_kmh=self._input_float("Max km/h: "),
                **params,
            )
        elif wahl == "3":
            training = Krafttraining(**params)
            print("\n--- ÜBUNGEN HINZUFÜGEN ---")

            # Liste der Standardübungen
            standards = ["Bankdrücken", "Kniebeugen", "Kreuzheben"]

            while True:
                print("\nWähle eine Übung:")
                for i, st in enumerate(standards, 1):
                    print(f"{i}. {st}")
                print("m. Manuelle Eingabe")
                print("q. Fertig / Beenden")

                ue_wahl = input("\nAuswahl > ").lower()

                if ue_wahl == "q":
                    break

                # Name bestimmen
                if ue_wahl == "1":
                    name = standards[0]
                elif ue_wahl == "2":
                    name = standards[1]
                elif ue_wahl == "3":
                    name = standards[2]
                elif ue_wahl == "m":
                    while True:
                        name = input("Name der Übung: ").strip()
                        if name:
                            break
                        print("Name darf nicht leer sein.")
                else:
                    print("Ungültige Wahl. Bitte 1, 2, 3, m oder q eingeben.")
                    input("[Enter]")  # Gibt dem Nutzer Zeit, den Fehler zu lesen
                    continue

                # Details abfragen
                s = self._input_int("Sätze: ")
                w = self._input_int("Wiederholungen: ")
                g = self._input_float("Gewicht in kg: ")

                training.add_uebung(Uebung(name, s, w, g))
                print(f"{name} hinzugefügt.")
        else:
            return

        self.repo.training_speichern(training)
        input("\nGespeichert! [Enter]")

    def trainings_anzeigen(self):
        """
        Dient der Einsicht in gespeicherte Trainingsdaten.

        Ermöglicht die Auswahl der Anzeige aller Trainings oder der Trainings an
        einem frei wählbaren Datum. Ausgaben werden als Tabellen aufbereitet. Von
        der Ansicht aus ist ein direkter Wechsel zur Detailansicht eines einzelnen
        Trainings möglich.

        Enthalten ist eine robuste Validierung der Benutzereingaben für Datum und ID.
        """
        while True:
            self._header("TRAININGS ANZEIGEN")
            while True:  # Eingabevalidierung
                datum_input = input(
                    "Datum (JJJJ-MM-DD) oder [Enter] für alle | [q] Zurück: "
                ).lower()

                if datum_input == "q":
                    return  # zurück zum Hauptmenü

                if datum_input == "":
                    datum = None
                    break
                else:
                    try:
                        # Validierung des Formats
                        datetime.strptime(datum_input, "%Y-%m-%d")
                        datum = datum_input
                        break
                    except ValueError:
                        print("Ungültiges Format. Bitte JJJJ-MM-DD nutzen.")
                        input("[Enter]")

            res = self.repo.get_trainings_benutzer(
                self.aktiver_nutzer_id, datum if datum else None
            )

            if not res:
                print("\nKeine Trainings gefunden.")
                input("[Enter] Weiter")
                continue

            print(
                "\n"
                + tabulate(
                    res,
                    headers=["ID", "Typ", "Datum", "Min", "Wertung"],
                    tablefmt="psql",
                )
            )

            print("\nOptionen: [ID] für Details | [Enter] Neue Suche | [q] Zurück")
            wahl = input("Auswahl > ").lower()

            if wahl == "q":
                break
            elif not wahl:
                continue

            try:
                t_id = int(wahl)
                if any(t[0] == t_id for t in res):
                    self.details_ausgeben(t_id)
                else:
                    print(f"ID {t_id} nicht in der Liste gefunden.")
                    input("[Enter] Weiter")
            except ValueError:
                print("Ungültige Eingabe.")
                input("[Enter] Weiter")

    def details_ausgeben(self, t_id: int):
        """Hilfsmethode zur formatierten Ausgabe der Details."""
        data = self.repo.get_training_details(t_id)
        if not data:
            print("Details konnten nicht geladen werden.")
            return

        self._header(f"DETAILS: {data['Typ']} (ID: {t_id})")

        # Krafttraining-Übungen separat als Tabelle anzeigen
        if data["Typ"] == "Krafttraining" and "Übungen" in data:
            print(
                tabulate(
                    data["Übungen"],
                    headers=["Übung", "Sätze", "Wdh", "kg"],
                    tablefmt="pqsl",
                )
            )
        else:
            # Andere Trainings als Liste anzeigen
            for key, val in data.items():
                print(f"{key:15}: {val}")

        input("\n[Enter] Zurück zur Liste")

    def analyse_menue(self):
        """
        Dient der Wahl verschiedener Methoden zur statistischen Auswertung der Trainings
        und somit des Trainingsfortschrittes eines Benutzers.

        Analyse-Optionen:
        1. Übersicht über die Trainings der Kalenderwoche
        2. Volumen-Progression der Krafttrainings
        3. Pace-Entwicklung für Dauerlauftrainings

        Es werden jeweils die entsprechenden Rohdaten über TrainingRepository abgerufen,
        spezifische Berechnungen vorgenommen und die Daten in tabellarische Form überführt.
        """

        while True:
            self._header("ANALYSE UND STATISTIKEN")
            print("1. Wochen-Zusammenfassung (KW)")
            print("2. Kraft-Volumen Progression")
            print("3. Pace-Entwicklung (Laufen)")
            print("0. Zurück")
            wahl = input("\nAuswahl > ")

            if wahl == "1":
                data = self.repo.get_uebersicht_kw()
                print(
                    "\n"
                    + tabulate(
                        data,
                        headers=["KW", "Anzahl", "Min gesamt", "Wertung gesamt"],
                        tablefmt="psql",
                    )
                )
            elif wahl == "2":
                data = self.repo.get_volumen_progression()
                print(
                    "\n"
                    + tabulate(
                        data, headers=["Datum", "Volumen (kg)"], tablefmt="psql"
                    )
                )
            elif wahl == "3":
                data = self.repo.get_dauerlauf_pace()
                fmt = []
                for d, dist, min, p in data:
                    # Prüfen, ob Pace vorhanden ist (nicht None)
                    if p is not None:
                        minuten = int(p)
                        sekunden = int((p - minuten) * 60)
                        pace_str = f"{minuten}:{sekunden:02d}"
                    else:
                        pace_str = "0:00"

                    fmt.append([d, dist, min, pace_str])

                print(
                    "\n"
                    + tabulate(
                        fmt, headers=["Datum", "km", "Min", "Pace"], tablefmt="psql"
                    )
                )
            elif wahl == "0":
                break
            input("\n[Enter] für zurück zum Analyse-Menü")

    def training_loeschen(self):
        """
        Dient dem Löschen von spezifischen Trainingseinheiten aus der Datenbank.

        Zeigt eine Übersicht der gespeicherten Trainings des aktiven Benutzers an.
        Vor dem Löschen wird eine Sicherheitsabfrage durchgeführt und geprüft, ob
        die ID tatsächlich zu einem Training des Benutzers gehört.
        """

        while True:
            self._header("TRAINING LÖSCHEN")

            # 1. Übersicht über vorhandene Trainings anzeigen
            res = self.repo.get_trainings_benutzer(self.aktiver_nutzer_id)

            if not res:
                print("Keine Trainings zum Löschen vorhanden.")
                input("\n[Enter] Zurück")
                break

            print(tabulate(res, headers=["ID", "Typ", "Datum", "Min"], tablefmt="psql"))

            print("\nGib die ID des Trainings ein, das gelöscht werden soll.")
            print("[q] Abbrechen / Zurück")

            wahl = input("\nAuswahl > ").lower()

            if wahl == "q":
                break

            try:
                t_id = int(wahl)
                # Prüfen, ob die eingegebene ID in der Liste des Nutzers vorkommt
                if any(t[0] == t_id for t in res):
                    bestaetigung = input(
                        f"ID {t_id} wirklich unwiderruflich löschen? (j/n): "
                    ).lower()
                    if bestaetigung == "j":
                        self.repo.loesche_training(t_id)
                        print(f"Training {t_id} gelöscht.")
                        input("[Enter] Weiter")
                else:
                    print(
                        f"ID {t_id} gehört nicht zu deinen Trainings oder existiert nicht."
                    )
                    input("[Enter] Erneut versuchen")
            except ValueError:
                print("Bitte gib eine gültige ID oder 'q' ein.")
                input("[Enter] Erneut versuchen")


if __name__ == "__main__":
    cli = FitnessCLI()
    cli.benutzer_verwalten()
    cli.hauptmenue()
