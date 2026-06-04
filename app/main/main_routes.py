import json
import traceback

from flask import render_template, session, redirect, url_for, request, flash, jsonify
from app.db import execute_query
from app.services.beheersing_niveau_service import BeheersingNiveauService, controller
from app.services.widget_service import WidgetService
from app.utils.student_helper import get_current_leerling_id


class MainRoutes:
    """Registratie van hoofdroutes in een OOP-routerklasse."""

    def __init__(self, blueprint):
        self.bp = blueprint
        self.register_routes()

    def register_routes(self):
        self.bp.add_url_rule("/", endpoint="index", view_func=self.index)
        self.bp.add_url_rule("/over-mij", endpoint="about_me", view_func=self.about_me)
        self.bp.add_url_rule("/home", endpoint="home", view_func=self.home)
        self.bp.add_url_rule("/aanbevelingen", endpoint="aanbevelingen", view_func=self.aanbevelingen)
        self.bp.add_url_rule("/oefenen-opgaven", endpoint="oefenen_opgaven", view_func=self.oefenen_opgaven)
        self.bp.add_url_rule(
            "/oefenen-opgaven/resultaat",
            endpoint="oefenen_opgaven_resultaat",
            view_func=self.oefenen_opgaven_resultaat,
            methods=["POST"]
        )
        self.bp.add_url_rule("/beheersingsniveau", endpoint="beheersingsniveau", view_func=self.beheersingsniveau)
        self.bp.add_url_rule(
            "/beheersingsniveau/<int:leerling_id>",
            endpoint="beheersingsniveau_with_id",
            view_func=self.beheersingsniveau
        )
        self.bp.add_url_rule("/beheersing-niveau", endpoint="beheersing_niveau", view_func=self.beheersing_niveau)
        self.bp.add_url_rule(
            "/_debug_current_leerling",
            endpoint="_debug_current_leerling",
            view_func=self._debug_current_leerling
        )

    def index(self):
        """Homepage - Redirect naar dashboard."""
        return redirect(url_for('main.home'))

    def about_me(self):
        """About pagina."""
        return render_template("zelfportret.html")

    def home(self):
        try:
            leerling_id = get_current_leerling_id(None)

            try:
                service = BeheersingNiveauService()
                fa = service.get_beheersing_niveau_dashboard_data(leerling_id)
                if hasattr(fa, 'to_dict'):
                    fa_dict = fa.to_dict()
                elif isinstance(fa, dict):
                    fa_dict = fa
                else:
                    fa_dict = {}

                fouten = []
                for subject, info in fa_dict.get('mistakes_by_subject', {}).items():
                    if not isinstance(info, dict):
                        continue
                    fouten.append({
                        'categorie': subject,
                        'percentage': info.get('percentage', 0),
                        'details': info.get('mistakes', [])
                    })
                aanbeveling = fa_dict.get('recommendation', 'Blijf oefenen!')
            except Exception as e:
                print(f"⚠️ Fout bij BeheersingNiveauService: {e}")
                fouten = []
                aanbeveling = "Oefenen maakt perfect!"

            skills = [
                {"name": "Tijdsbeheer", "score": 4, "trend": "up"},
                {"name": "Concentratie", "score": 3, "trend": "flat"},
                {"name": "Nauwkeurigheid", "score": 4, "trend": "up"},
                {"name": "Probleemoplossend", "score": 5, "trend": "up"},
            ]

            if fouten:
                gemiddelde_score = round(
                    10 - (sum(f["percentage"] for f in fouten) / len(fouten)) / 10, 1
                )
            else:
                gemiddelde_score = 7.4

            trend_scores = [6, 6.5, 6.2, 7]

            widget_service = WidgetService()
            widgets = widget_service.get_available_widgets(leerling_id)
            visible_widget_slugs = {widget.slug for widget in widgets if widget.selected}

            session_user = session.get("user")
            if isinstance(session_user, dict):
                user_name = session_user.get("name") or session_user.get("email") or "Jouw Naam"
            else:
                user_name = session_user or "Jouw Naam"

            user_initials = "".join([part[0].upper() for part in str(user_name).split() if part])[:2] or "JN"

            user = {
                "name": user_name,
                "initials": user_initials,
            }

            return render_template(
                "home.html",
                fouten=fouten[:3],
                aanbeveling=aanbeveling,
                skills=skills,
                gemiddelde_score=gemiddelde_score,
                trend_scores=trend_scores,
                user=user,
                visible_widget_slugs=visible_widget_slugs,
            )
        except Exception as e:
            print(f"❌ Fout in home route: {e}")
            traceback.print_exc()
            flash(f"Fout: {str(e)}", "error")
            return redirect(url_for('main.index'))

    def aanbevelingen(self):
        """Render the recommendations page for students with tips."""
        menu_items = [
            {"name": "Dashboard", "url": url_for('main.index'), "active": False},
            {"name": "Aanbevelingen", "url": url_for('main.aanbevelingen'), "active": True},
        ]

        user = {
            "name": session.get("user", "Gast"),
            "role": session.get("role", "leerling")
        }

        try:
            exercises = execute_query("SELECT id, title, description, duration FROM exercises")
        except Exception:
            exercises = []

        cards = []
        for e in exercises:
            if not isinstance(e, dict):
                continue
            cards.append({
                "title": e.get("title", "Onbekend"),
                "description": e.get("description", "Geen beschrijving"),
                "time": e.get("duration", 10),
                "exercises": 10,
                "color": "primary"
            })

        if not cards:
            cards = [
                {"title": "Vermijd Haastige Conclusies", "description": "Lees alle antwoordopties goed voordat je kiest.", "time": 15, "exercises": 12, "color": "red"},
                {"title": "Sleutelwoorden Herkennen", "description": "Oefen met markeren van belangrijke woorden.", "time": 10, "exercises": 8, "color": "purple"},
                {"title": "Tijdsplanning Verbeteren", "description": "Leer beter je tijd in delen zodat je op tijd klaar bent.", "time": 20, "exercises": 15, "color": "blue"},
            ]

        completed = [
            {"title": "Concentratie Oefeningen", "score": 8.5},
            {"title": "Tijdsbeheer Basis", "score": 7.8},
        ]

        upcoming = [
            {"title": "Nieuwe Oefeningen: Nauwkeurigheid"},
            {"title": "Nieuwe Oefeningen: Spelling"},
        ]

        return render_template(
            "aanbevelingen.html",
            menu_items=menu_items,
            subtitle="Persoonlijke oefeningen en aanbevelingen om te verbeteren",
            user=user,
            cards=cards,
            completed=completed,
            upcoming=upcoming,
            cta_text="Start nu met oefenen"
        )

    def ensure_oefenopgaven_table(self):
        execute_query("""
            CREATE TABLE IF NOT EXISTS oefenopgaven_result (
                id INT NOT NULL AUTO_INCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                score INT NOT NULL,
                total_answered INT NOT NULL,
                incorrect_answers TEXT NOT NULL,
                PRIMARY KEY(id)
            )
        """)

    def save_oefenopgaven(self, score, total_answered, incorrect_answers):
        self.ensure_oefenopgaven_table()
        execute_query(
            """
            INSERT INTO oefenopgaven_result (score, total_answered, incorrect_answers)
            VALUES (?, ?, ?)
            """,
            (score, total_answered, json.dumps(incorrect_answers, ensure_ascii=False))
        )

    def oefenen_opgaven(self):
        return render_template("oefenen_opgaven.html")

    def oefenen_opgaven_resultaat(self):
        data = request.get_json() or {}
        score = int(data.get("score", 0))
        total_answered = int(data.get("total_answered", 0))
        incorrect_answers = data.get("incorrect_answers", [])
        self.save_oefenopgaven(score, total_answered, incorrect_answers)
        return jsonify({"ok": True})

    def beheersingsniveau(self, leerling_id=None):
        if leerling_id is None:
            leerling_id = request.args.get("leerling_id", type=int)
        if leerling_id is None:
            leerling_id = session.get("leerling_id", 1)

        subject_id = request.args.get("subject_id", type=int)
        return controller.render_dashboard(leerling_id, subject_id)

    def beheersing_niveau(self):
        subject_id = request.args.get("subject_id", type=int)
        return controller.render_dashboard(None, subject_id)

    def _debug_current_leerling(self):
        try:
            lid = get_current_leerling_id(None)
        except Exception as e:
            return f"error: {e}", 500
        return f"current_leerling_id={lid}"
