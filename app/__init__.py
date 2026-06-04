"""Entry point for Flask application"""

from flask import Flask, request, redirect, url_for, session

from app.main import bp as main_bp
from app.contact import bp as contact_bp


def create_app():
    # Flask applicatie initialiseren
    app = Flask(__name__)

    # Configuratie-instellingen
    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True

    # Belangrijk: secret key voor sessions (moet normaal uit env komen)
    app.config["SECRET_KEY"] = "DokkiePythoniAXRvULKWuFyfURRrG0YTOOTXswLJWpU"

    # Templates automatisch herladen bij wijzigingen (dev mode)
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Extra configuratie uit settings.py laden
    app.config.from_pyfile("settings.py")

    # Blueprints importeren (modulaire routes)
    from app.login import bp as login_bp

    # Blueprints registreren
    app.register_blueprint(login_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)

    # Compatibiliteitsroutes voor oude test- en gebruikersflow
    import app.auth as auth_wrapper

    @app.route("/", methods=["GET", "POST"])
    def root_login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            teacher = auth_wrapper.login_teacher(email, password)
            if teacher:
                session["user"] = teacher
                session["role"] = teacher.get("role", "docent")
                return redirect(url_for("login.login"))
            return "Inloggen mislukt"
        return redirect(url_for("login.login"))

    @app.route("/reset", methods=["GET", "POST"])
    def root_reset():
        if request.method == "POST":
            email = request.form.get("email")
            code = request.form.get("code")
            new_password = request.form.get("new_password")
            if auth_wrapper.reset_password(email, code, new_password):
                return "Wachtwoord gewijzigd!"
            return "Reset mislukt"
        return redirect(url_for("login.reset"))

    @app.before_request
    def require_login():
        """
        Globale middleware die elke request controleert:
        - Is gebruiker ingelogd?
        - Heeft gebruiker (docent/leerling) toegang tot endpoint?
        """

        # Routes die altijd toegankelijk zijn zonder login
        allowed_endpoints = {
            "login.login",
            "login.register",
            "login.reset",
            "login.logout",
            "root_login",
            "root_reset",
            "static",
        }

        # Extra toegestane routes voor docenten
        docent_allowed_endpoints = allowed_endpoints.union({
            "main.leerlingen",
            "main.leerling_redirect",
            "main.leerling_detail",
            "main.widget_preferences",
            "contact.contact",
            "contact.support",
        })

        # Extra toegestane routes voor leerlingen
        leerling_allowed_endpoints = allowed_endpoints.union({
            "main.index",
            "main.home",
            "main.score",
            "main.score_with_id",
            "main.beheersingsniveau",
            "main.beheersingsniveau_with_id",
            "main.aanbevelingen",
            "main.widget_preferences",
            "main.dashboard_widgets",
            "main.oefenen_opgaven",
            "main.oefenen_opgaven_resultaat",
            "contact.contact",
            "contact.support",
        })

        # Laat publieke endpoints direct door
        if request.endpoint in allowed_endpoints:
            return

        # Geen ingelogde gebruiker → redirect naar login
        if session.get("user") is None:
            return redirect(url_for("login.login"))

        # Docent mag alleen docent-routes
        if session.get("role") == "docent" and request.endpoint not in docent_allowed_endpoints:
            return redirect(url_for("main.leerlingen"))

        # Leerling mag alleen leerling-routes
        if session.get("role") == "leerling" and request.endpoint not in leerling_allowed_endpoints:
            return redirect(url_for("main.home"))

    # Context processor: maakt data beschikbaar in ALLE templates
    from app.utils.student_helper import get_current_leerling_id

    @app.context_processor
    def inject_current_leerling():
        """
        Zorgt dat `current_leerling_id` beschikbaar is in Jinja templates
        zonder het steeds expliciet mee te geven.
        """

        try:
            lid = get_current_leerling_id(None)
        except Exception:
            # fallback ID als helper faalt
            lid = 16

        return {"current_leerling_id": lid}

    return app


# Maak een module-brede Flask-app beschikbaar voor eenvoudige import.
app = create_app()
