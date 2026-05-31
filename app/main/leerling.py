from flask import render_template, redirect, url_for, flash
from app.db import execute_query
from app.models.leerling import Leerling
from app.services.fout_analyse_service import FoutAnalyseService


class LeerlingDetailService:
    """Service voor het ophalen van data voor de leerling-detailpagina."""

    def __init__(self, leerling_id):
        self.leerling = Leerling.from_id(leerling_id)
        self.foutanalyse_service = FoutAnalyseService()

    def get_score_info(self):
        query = """
        SELECT
            SUM(sa.score) AS total_score,
            SUM(sa.max_score) AS total_max
        FROM student_answer sa
        JOIN question q ON sa.question_id = q.id
        JOIN subject s ON q.subject_id = s.id
        WHERE sa.student_id = ?
        """
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
        zwak_onderwerp, _ = self.leerling.find_zwak_onderwerp(resultaten)
        foutanalyse = self.get_foutanalyse_data()
        score_info = self.get_score_info()

        return {
            "leerling": self.leerling,
            "resultaten": resultaten,
            "fouten": fouten,
            "categorieen": categorieen,
            "zwak_onderwerp": zwak_onderwerp,
            "uitleg": uitleg,
            "advies": advies,
            "foutanalyse": foutanalyse,
            "score_info": score_info,
        }


class LeerlingDetailController:
    """Controller voor de leerling detail route."""

    def __init__(self, leerling_id):
        self.service = LeerlingDetailService(leerling_id)

    def render(self):
        context = self.service.get_context()
        return render_template("leerlingdetail.html", **context)

class LeerlingRoutes:
    """Object-georiënteerde router voor leerling-gerelateerde pagina's."""

    def __init__(self, blueprint):
        self.bp = blueprint
        self.register_routes()

    def register_routes(self):
        self.bp.add_url_rule("/leerlingen", endpoint="leerlingen", view_func=self.leerlingen)
        self.bp.add_url_rule("/leerling", endpoint="leerling_redirect", view_func=self.leerling_redirect)
        self.bp.add_url_rule(
            "/leerling/<int:leerling_id>",
            endpoint="leerling_detail",
            view_func=self.leerling_detail
        )

    def leerlingen(self):
        """Overzicht van alle leerlingen."""
        leerlingen = execute_query("SELECT id, naam, klas FROM leerling")
        klassen = sorted({l.get("klas") for l in leerlingen if l.get("klas") is not None})
        return render_template(
            "leerlingen.html",
            leerlingen=leerlingen,
            klassen=klassen
        )
        
    def leerling_redirect(self):
        """Redirect naar overzicht als geen ID is opgegeven."""
        return redirect(url_for('main.leerlingen'))

    def leerling_detail(self, leerling_id):
        """Detailpagina van één leerling."""
        try:
            controller = LeerlingDetailController(leerling_id)
            return controller.render()
        except ValueError:
            flash(f"Leerling met id {leerling_id} niet gevonden", "error")
            return redirect(url_for('main.leerlingen'))
        except Exception as exc:
            print(f"❌ Fout in leerling_detail route: {exc}")
            flash("Er ging iets mis bij het laden van de leerling.", "error")
            return redirect(url_for('main.leerlingen'))
