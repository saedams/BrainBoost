from flask import render_template
from app.db import execute_query
from app.models.leerling import Leerling
from app.services.fout_analyse_service import FoutAnalyseService


class LeerlingDetailService:
    """
    Service voor het ophalen van alle data die de leerling detail pagina nodig heeft.
    """

    def __init__(self, leerling_id):
        self.leerling = Leerling.from_id(leerling_id)
        self.foutanalyse_service = FoutAnalyseService()

    def get_score_info(self):
        query = "SELECT SUM(score) AS total_score, SUM(max_score) AS total_max FROM student_answer WHERE student_id = ?"
        result = execute_query(query, (self.leerling.id,))
        score_info = {
            "average_score": None,
            "trend": [],
            "has_answer_scores": False,
            "score_message": "Geen scoregegevens beschikbaar."
        }

        if result and isinstance(result, list):
            row = result[0]
            total_score = row.get("total_score") or 0
            total_max = row.get("total_max") or 0
            if total_max:
                score_info["average_score"] = round((float(total_score) / float(total_max)) * 10, 1)
                score_info["has_answer_scores"] = True
                score_info["score_message"] = "Gebaseerd op gemaakte opdrachten."

        score_info["trend"] = self.get_score_trend()
        return score_info

    def get_score_trend(self, max_points=6):
        query = "SELECT score, max_score FROM student_answer WHERE student_id = ? ORDER BY created_at ASC"
        rows = execute_query(query, (self.leerling.id,))
        trend = []
        if rows and isinstance(rows, list):
            for row in rows[-max_points:]:
                score = row.get("score") or 0
                max_score = row.get("max_score") or 1
                try:
                    score = float(score)
                    max_score = float(max_score)
                except (TypeError, ValueError):
                    score = 0.0
                    max_score = 1.0
                trend.append(round((score / max_score) * 10, 1) if max_score else 0.0)
        return trend

    def get_foutanalyse_data(self):
        return self.foutanalyse_service.get_fout_analyse_dashboard_data(self.leerling.id).to_dict()

    def get_context(self):
        resultaten = self.leerling.get_resultaten()
        fouten = self.leerling.get_fouten()
        categorieen = self.leerling.group_fouten_by_categorie(fouten)
        uitleg, advies = self.leerling.get_advies(resultaten)
        foutanalyse = self.get_foutanalyse_data()
        score_info = self.get_score_info()

        return {
            "leerling": self.leerling,
            "resultaten": resultaten,
            "fouten": fouten,
            "categorieen": categorieen,
            "zwak_onderwerp": self.leerling.find_zwak_onderwerp(resultaten)[0],
            "uitleg": uitleg,
            "advies": advies,
            "foutanalyse": foutanalyse,
            "score_info": score_info,
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
