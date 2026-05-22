from flask import render_template, session, redirect, url_for, request, flash, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import execute_query
import json
from app.main import bp
from app.services.fout_analyse_service import FoutAnalyseService, controller
from app.services.leerling_detail import LeerlingDetailController

@bp.route("/")
def index():
    """
    Homepage - Redirect naar dashboard.
    """
    return redirect(url_for('main.home'))


@bp.route("/over-mij")
def about_me():
    """
    About pagina.
    """
    return render_template("zelfportret.html")

@bp.route("/home")
def home():
    try:
        leerling_id = session.get("leerling_id", 1)

        #  Foutenanalyse ophalen via centrale service
        try:
            service = FoutAnalyseService()
            fa = service.get_fout_analyse_dashboard_data(leerling_id)
            fa_dict = fa.to_dict() if hasattr(fa, 'to_dict') else dict(fa)
            # Maak een eenvoudige lijst met categorie/percentage voor de home kaart
            fouten = []
            for subject, info in fa_dict.get('mistakes_by_subject', {}).items():
                fouten.append({
                    'categorie': subject,
                    'percentage': info.get('percentage', 0),
                    'details': info.get('mistakes', [])
                })
            aanbeveling = fa_dict.get('recommendation', 'Blijf oefenen!')
        except Exception as e:
            print(f"⚠️ Fout bij FoutAnalyseService: {e}")
            fouten = []
            aanbeveling = "Oefenen maakt perfect!"

        #  Skills (kan later uit database)
        skills = [
            {"name": "Tijdsbeheer", "score": 4, "trend": "up"},
            {"name": "Concentratie", "score": 3, "trend": "flat"},
            {"name": "Nauwkeurigheid", "score": 4, "trend": "up"},
            {"name": "Probleemoplossend", "score": 5, "trend": "up"},
        ]

        #  Gemiddelde score berekenen
        if fouten:
            gemiddelde_score = round(
                10 - (sum(f["percentage"] for f in fouten) / len(fouten)) / 10, 1
            )
        else:
            gemiddelde_score = 7.4

        # 📈 Dummy trend (later uit DB)
        trend_scores = [6, 6.5, 6.2, 7]

        user = {
            "name": session.get("user", "Jouw Naam"),
            "initials": "JN"
        }

        return render_template(
            "home.html",
            fouten=fouten[:3],
            aanbeveling=aanbeveling,
            skills=skills,
            gemiddelde_score=gemiddelde_score,
            trend_scores=trend_scores,
            user=user
        )
    except Exception as e:
        print(f"❌ Fout in home route: {e}")
        flash(f"Fout: {str(e)}", "error")
        return redirect(url_for('main.index'))


@bp.route("/leerlingen")
def leerlingen():
    """
    Overzicht van alle leerlingen.
    """
    leerlingen = execute_query("SELECT id, naam, klas FROM leerling")
    klassen = sorted({l.get("klas") for l in leerlingen if l.get("klas") is not None})
    
    return render_template(
        "leerlingen.html",
        leerlingen=leerlingen,
        klassen=klassen
    )


@bp.route("/leerling")
def leerling_redirect():
    """
    Redirect naar overzicht als geen ID is opgegeven.
    """
    return redirect(url_for('main.leerlingen'))


# Aanbevelingen pagina route

@bp.route("/aanbevelingen")
def aanbevelingen():
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
        "events/aanbevelingen.html",
        menu_items=menu_items,
        subtitle="Persoonlijke oefeningen en aanbevelingen om te verbeteren",
        user=user,
        cards=cards,
        completed=completed,
        upcoming=upcoming,
        cta_text="Start nu met oefenen"
    )


@bp.route("/leerling/<int:leerling_id>")
def leerling_detail(leerling_id):
    """
    Detailpagina van één leerling.

    Deze route gebruikt de controller en service in aparte bestanden.
    """
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


def ensure_oefenopgaven_table():
    """
    Maakt de tabel aan als deze nog niet bestaat.
    """
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


def save_oefenopgaven(score, total_answered, incorrect_answers):
    """
    Slaat de resultaten op in de database.
    """
    ensure_oefenopgaven_table()

    execute_query(
        """
        INSERT INTO oefenopgaven_result (score, total_answered, incorrect_answers)
        VALUES (?, ?, ?)
        """,
        (score, total_answered, json.dumps(incorrect_answers, ensure_ascii=False))
    )

@bp.route("/oefenen-opgaven")
def oefenen_opgaven():
    """
    Render de oefenopgaven-pagina.
    """
    return render_template("oefenen_opgaven.html")


@bp.route("/oefenen-opgaven/resultaat", methods=["POST"])
def oefenen_opgaven_resultaat():
    """
    Ontvangt resultaten en slaat deze op.
    """
    data = request.get_json() or {}

    score = int(data.get("score", 0))
    total_answered = int(data.get("total_answered", 0))
    incorrect_answers = data.get("incorrect_answers", [])

    save_oefenopgaven(score, total_answered, incorrect_answers)

    return jsonify({"ok": True})


@bp.route("/foutenanalyse")
@bp.route("/foutenanalyse/<int:leerling_id>")
def foutenanalyse(leerling_id=None):
    """
    Route voor foutenanalyse dashboard (backward compatible).

    Gebruikt dezelfde service als /fout-analyse voor compatibiliteit.
    """
    if leerling_id is None:
        leerling_id = request.args.get("leerling_id", type=int)
    if leerling_id is None:
        leerling_id = session.get("leerling_id", 1)

    
    analyzer = ErrorAnalyzer(leerling_id)
    analyzer.analyze()
    data = analyzer.get_data()
    

    subject_id = request.args.get("subject_id", type=int)

    from app.services.fout_analyse_service import controller
    return controller.render_dashboard(leerling_id, subject_id)


# DEFINITIE: FOUTENANALYSE ROUTE
# Deze route toont de foutenanalysepagina voor de leerling.
# De route verwerkt alleen de request-parameters, roept de serviceklasse aan
# en geeft de opgehaalde analysegegevens door aan de Jinja-template.
# Alle berekeningen en database-logica blijven binnen FoutAnalyseService.
@bp.route("/fout-analyse")
def fout_analyse():
    """
    Route voor foutenanalyse dashboard.
    """
    # De controller bepaalt de actieve leerling
    subject_id = request.args.get("subject_id", type=int)

    from app.services.fout_analyse_service import controller
    return controller.render_dashboard(None, subject_id)


@bp.route('/_debug_current_leerling')
def _debug_current_leerling():
    from app.utils.student_helper import get_current_leerling_id
    try:
        lid = get_current_leerling_id(None)
    except Exception as e:
        return f"error: {e}", 500
    return f"current_leerling_id={lid}"