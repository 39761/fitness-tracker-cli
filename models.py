# models.py

from abc import ABC, abstractmethod
from datetime import datetime, time
from typing import List, Optional, Any


class Training(ABC):
    """
    Repräsentiert ein generisches Training.

    Args:
        nutzer_id (int): Identifikationsnr des Nutzers.
        datum (datetime): Datum des Trainings (YYY-MM-DD).
        uhrzeit (time): Uhrzeit des Trainingsbeginns.
        dauer_min (int): Trainingsdauer in min.
        training_id (Optional[int]): Datenbank-ID, wird nach Speichern bestimmt.
    """

    def __init__(
        self,
        nutzer_id: int,
        datum: datetime,
        uhrzeit: time,
        dauer_min: int,
        training_id: Optional[int] = None,
    ):
        self.nutzer_id = nutzer_id
        self.datum = datum
        self.uhrzeit = uhrzeit
        self.dauer_min = dauer_min
        self.training_id = training_id

    @abstractmethod
    def berechne_wertung(self) -> float:
        """
        Berechnet eine relativen Belastungswertung, der als Maß für die Trainingsleistung dient.

        Returns:
            float: Trainings-Wertung.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} ID={self.training_id} Datum={self.datum}>"


class Dauerlauf(Training):
    """
    Repräsentiert eine Ausdauertrainingseinheit (Laufen).

    Args:
        distanz_km (float): Zurückgelegte Strecke in Kilometern.
        hf_mittel (int) : Durchschnittliche Herzfrequenz
    """

    def __init__(
        self, distanz_km: float, hf_mittel: Optional[int] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.distanz_km = distanz_km
        self.hf_mittel = hf_mittel

    def berechne_wertung(self) -> float:
        """Berechnet den Wertung auf Grundlage von Laufdistanz und Geschwindigkeit."""
        dauer_h = self.dauer_min / 60

        geschwindigkeit = self.distanz_km / dauer_h if dauer_h > 0 else 0

        return self.distanz_km * geschwindigkeit

    def __repr__(self):
        return f"Dauerlauf({self.distanz_km}km, ID={self.training_id})"


class Sprint(Training):
    """
    Repräsentiert eine Trainingsintervalleinheit (Sprints).

    Args:
        anzahl (int): Anzahl der Sprints
        max_kmh (float): Erreichte Höchstgeschwindigkeit während der Trainingseinheit
    """

    def __init__(self, anzahl: int, max_kmh: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.anzahl = anzahl
        self.max_kmh = max_kmh

    def berechne_wertung(self) -> float:
        """Berechnet die Wertung auf Grundlage der Anzahl der Sprints und der
        erreichten Höchstgeschwindigkeit."""
        return self.anzahl * self.max_kmh

    def __repr__(self):
        return f"Sprint({self.anzahl} Sprints, {self.max_kmh}km/h)"


class Uebung:
    """
    Komponente eines Krafttrainings

    Args:
        name (str): Bezeichnung der Übung
        saetze (int): Anzahl der Sätze
        wdh (int): Anzahl der Wiederholungen innerhalb der Sätze
        gewicht (float): Das bei den Wiederholungen verwendete Gewicht
    """

    def __init__(self, name: str, saetze: int, wdh: int, gewicht: float):
        self.name = name
        self.saetze = saetze
        self.wdh = wdh
        self.gewicht = gewicht

    @property
    def volumen(self) -> float:
        """Berechnet das Volumen der Übung für spätere Berechnung des Wertungs."""
        return self.saetze * self.wdh * self.gewicht

    def __repr__(self):
        return f"Uebung('{self.name}', {self.saetze}, {self.wdh}, {self.gewicht})"


class Krafttraining(Training):
    """Repräsentiert eine Einheit Krafttraining als Aggregation mehrerer Übungen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uebungen: List[Uebung] = []

    def add_uebung(self, uebung: Uebung):
        self.uebungen.append(uebung)

    def berechne_wertung(self) -> float:
        """Berechnet die Wertung auf Grundlage des Gesamtvolumens aller Übungen"""
        return (
            sum(u.volumen for u in self.uebungen) / 20
        )  # Divisor sorgt für Skalierung

    def __repr__(self):
        return f"Krafttraining({len(self.uebungen)} Übungen, ID={self.training_id})"


class Benutzer:
    """Repräsentiert einen Benutzer (bzw. ist die Aggregation der Trainings dieses Benutzers)."""

    def __init__(self, name: str, nutzer_id: Optional[int] = None):
        self.name = name
        self.nutzer_id = nutzer_id
        self.trainings: List[Training] = []

    def add_training(self, training: Training):
        self.trainings.append(training)

    def __repr__(self):
        return f"Benutzer('{self.name}', ID={self.nutzer_id}, Trainings={len(self.trainings)})"
