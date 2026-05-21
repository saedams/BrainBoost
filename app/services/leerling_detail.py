from flask import render_template
from app.models.leerling import Leerling


class LeerlingDetailService:
    """
    Service voor het ophalen van alle data die de leerling detail pagina nodig heeft.
    """

    def __init__(self, leerling_id):
        self.leerling = Leerling.from_id(leerling_id)

    def get_context(self):
        resultaten = self.leerling.get_resultaten()
        fouten = self.leerling.get_fouten()
        categorieen = self.leerling.group_fouten_by_categorie(fouten)
        uitleg, advies = self.leerling.get_advies(resultaten)

        return {
            "leerling": self.leerling,
            "resultaten": resultaten,
            "fouten": fouten,
            "categorieen": categorieen,
            "zwak_onderwerp": self.leerling.find_zwak_onderwerp(resultaten)[0],
            "uitleg": uitleg,
            "advies": advies,
        }


class LeerlingDetailController:
    """
    Controller voor de leerling detail route.
    """

    def __init__(self, leerling_id):
        self.service = LeerlingDetailService(leerling_id)

    def render(self):
        context = self.service.get_context()
        return render_template("leerlingdetail.html", **context)
