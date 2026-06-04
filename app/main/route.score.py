"""
Score module voor Brain Boost

Dit bestand heeft de route voor het score dashboard en haalt data op.
"""

from flask import render_template, session
from app.db import execute_query
from app.main import bp
from app.utils.student_helper import get_current_leerling_id

DEFAULT_USER_ID = 1

# Hier zijn de klassen voor de data die we gebruiken
# Dit is een klasse voor een vak score
class SubjectScore:
    """
    Een vak score met naam en cijfer.
    """

    def __init__(self, name, score, change=0):
        self.name = name
        self.score = score
        self.change = change

    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            "change": self.change
        }

# Dit is een klasse voor alle data van het dashboard
class DashboardData:
    """
    Alle data voor het dashboard.
    """

    def __init__(self, average_score=0, monthly_change=0, trend=None, subjects=None, error_message=None):
        self.average_score = average_score
        self.monthly_change = monthly_change
        self.trend = trend or [0, 0, 0, 0, 0, 0]
        self.subjects = subjects or []
        self.error_message = error_message

    def to_dict(self):
        return {
            "average_score": self.average_score,
            "monthly_change": self.monthly_change,
            "trend": self.trend,
            "subjects": [subject.to_dict() for subject in self.subjects],
            "error_message": self.error_message
        }

# Hier is de service klasse voor scores
# Deze klasse haalt data op en doet berekeningen
class ScoreService:
    """
    Service voor scores ophalen en berekenen.
    """

    def fetch_scores(self, user_id):
        """
        Haalt resultaten op uit de student_answer tabel via question en subject.
        """
        query = """
        SELECT s.name AS subject_name,
               SUM(sa.score) AS total_score,
               SUM(sa.max_score) AS total_max
        FROM student_answer sa
        JOIN question q ON sa.question_id = q.id
        JOIN subject s ON q.subject_id = s.id
        WHERE sa.student_id = ?
        GROUP BY s.name
        ORDER BY s.name
        """

        try:
            rows = execute_query(query, (user_id,))
        except Exception as exc:
            print(f"[score] SQL query error for leerling_id={user_id}: {exc}")
            return [], [], 0.0, f"SQL query problem: {exc}"

        if not rows:
            return [], [], 0.0, f"Geen studentgegevens gevonden voor leerling_id={user_id}."

        subjects = []
        overall_score = 0.0
        overall_max = 0.0

        for row in rows:
            total_score = row.get("total_score") or 0
            total_max = row.get("total_max") or 0
            try:
                total_score = float(total_score)
                total_max = float(total_max)
            except (TypeError, ValueError):
                total_score = 0.0
                total_max = 0.0

            subject_score = round((total_score / total_max) * 10, 1) if total_max else 0.0
            subjects.append(SubjectScore(
                name=row.get("subject_name", "Onbekend"),
                score=subject_score
            ))

            overall_score += total_score
            overall_max += total_max

        average_score = round((overall_score / overall_max) * 10, 1) if overall_max else 0.0
        return subjects, self.fetch_recent_trend(user_id), average_score, None

    def fetch_recent_trend(self, user_id, max_points=6):
        """
        Haalt de meest recente antwoorden op voor de trendgrafiek.
        """
        query = """
        SELECT sa.score, sa.max_score
        FROM student_answer sa
        WHERE sa.student_id = ?
        ORDER BY sa.created_at ASC
        """

        try:
            rows = execute_query(query, (user_id,))
        except Exception as exc:
            print(f"[score] trend query error for leerling_id={user_id}: {exc}")
            return [0] * max_points

        trend = []
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

        if not trend:
            return [0] * max_points

        return trend

    def calculate_average(self, scores):
        """
        Berekent gemiddelde.
        """
        return round(sum(scores) / len(scores), 1) if scores else 0.0

    def prepare_trend(self, scores, max_points=6):
        """
        Maakt trend data klaar.
        """
        if not scores:
            return [0] * max_points

        trend = scores[-max_points:]
        if len(trend) < max_points:
            trend = [0] * (max_points - len(trend)) + trend
        return trend

    def get_dashboard_data(self, user_id=DEFAULT_USER_ID):
        """
        Haalt alle data voor dashboard.
        """
        subjects, trend_scores, average, error_message = self.fetch_scores(user_id)
        trend = self.prepare_trend(trend_scores)

        return DashboardData(
            average_score=average,
            monthly_change=0,
            trend=trend,
            subjects=subjects,
            error_message=error_message
        )

# Hier is de controller voor het dashboard
# Deze zorgt voor de route en rendering
class ScoreController:
    """
    Controller voor score dashboard.
    """

    def __init__(self):
        self.service = ScoreService()

    def render_dashboard(self, user_id=None):
        """
        Rendert de dashboard pagina.
        """
        # Bepaal leerling ID centraal (url > query > session > demo)
        user_id = get_current_leerling_id(user_id)

        data = self.service.get_dashboard_data(user_id)
        return render_template("score.html", data=data.to_dict())

# Maak een controller aan
controller = ScoreController()

class ScoreRoutes:
    """Object-georiënteerde router voor het score-dashboard."""

    def __init__(self, blueprint):
        self.bp = blueprint
        self.register_routes()

    def register_routes(self):
        self.bp.add_url_rule("/score", endpoint="score", view_func=self.score)
        self.bp.add_url_rule("/score/<int:user_id>", endpoint="score_with_id", view_func=self.score)

    def score(self, user_id=None):
        """Route voor score dashboard."""
        return controller.render_dashboard(user_id)

ScoreRoutes(bp)


