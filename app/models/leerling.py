from app.db import execute_query


class Leerling:
    """
    Modelklasse voor een leerling.

    Deze klasse bevat basisgegevens en helpermethodes om
    resultaten en foutinformatie op te halen.
    """

    def __init__(self, id, naam, klas=None, email=None, wachtwoord_hash=None):
        self.id = id
        self.naam = naam
        self.klas = klas
        self.email = email
        self.wachtwoord_hash = wachtwoord_hash

    @classmethod
    def from_id(cls, leerling_id):
        rows = execute_query("SELECT * FROM leerling WHERE id = ?", (leerling_id,))
        if not rows:
            raise ValueError(f"Leerling met id {leerling_id} niet gevonden")
        row = rows[0]
        return cls(
            id=row.get("id"),
            naam=row.get("naam"),
            klas=row.get("klas"),
            email=row.get("email"),
            wachtwoord_hash=row.get("wachtwoord_hash")
        )

    def get_resultaten(self):
        return execute_query(
            "SELECT onderwerp, score FROM resultaat WHERE leerling_id = ?",
            (self.id,)
        )

    def get_fouten(self):
        return execute_query(
            "SELECT categorie, subcategorie, aantal FROM fout WHERE leerling_id = ?",
            (self.id,)
        )

    def group_fouten_by_categorie(self, fouten):
        categorieen = {}
        for fout in fouten:
            categorie = fout.get("categorie") or "Onbekend"
            categorieen.setdefault(categorie, []).append(fout)
        return categorieen

    def find_zwak_onderwerp(self, resultaten):
        if not resultaten:
            return None, None

        laagste_score = None
        zwak_onderwerp = None
        for resultaat in resultaten:
            score = resultaat.get("score")
            if score is None:
                continue
            if laagste_score is None or score < laagste_score:
                laagste_score = score
                zwak_onderwerp = resultaat.get("onderwerp")

        return zwak_onderwerp, laagste_score

    def get_advies(self, resultaten):
        zwak_onderwerp, laagste_score = self.find_zwak_onderwerp(resultaten)
        if zwak_onderwerp is None:
            return (
                "Geen resultaten gevonden om te analyseren.",
                "Voeg eerst resultaten toe om persoonlijke feedback te tonen."
            )

        if laagste_score < 50:
            uitleg = f"Leerling scoort laag op {zwak_onderwerp}."
            advies = f"Oefen extra met {zwak_onderwerp} en kijk terug naar de gemaakte fouten."
        elif laagste_score < 70:
            uitleg = f"Leerling heeft ruimte voor verbetering in {zwak_onderwerp}."
            advies = f"Besteed meer aandacht aan {zwak_onderwerp} en werk met oefenopgaven."
        else:
            uitleg = f"Leerling haalt goede resultaten, maar {zwak_onderwerp} kan nog beter."
            advies = f"Blijf oefenen op {zwak_onderwerp} om het niveau verder te verhogen."

        return uitleg, advies

    def to_dict(self):
        return {
            "id": self.id,
            "naam": self.naam,
            "klas": self.klas,
            "email": self.email,
        }
