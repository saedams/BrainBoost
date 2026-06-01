"""Entry point for Flask application"""

from flask import Flask, request, redirect, url_for, session

from app.events import bp as events_bp
from app.main import bp as main_bp
from app.contact import bp as contact_bp


def create_app():
    app = Flask(__name__)
    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
    app.config["SECRET_KEY"] = "DokkiePythoniAXRvULKWuFyfURRrG0YTOOTXswLJWpU"
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.config.from_pyfile("settings.py")

    from app.login import bp as login_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(contact_bp)

    @app.before_request
    def require_login():
        allowed_endpoints = {
            "login.login",
            "login.reset",
            "login.logout",
            "static",
        }

        docent_allowed_endpoints = allowed_endpoints.union({
            "main.leerlingen",
            "main.leerling_redirect",
            "main.leerling_detail",
            "contact.contact",
            "contact.support",
        })

        if request.endpoint in allowed_endpoints:
            return

        if session.get("user") is None:
            return redirect(url_for("login.login"))

        if session.get("role") == "docent" and request.endpoint not in docent_allowed_endpoints:
            return redirect(url_for("main.leerlingen"))

    # Maak `current_leerling_id` beschikbaar in alle templates
    from app.utils.student_helper import get_current_leerling_id

    @app.context_processor
    def inject_current_leerling():
        # context processor wordt in request context aangeroepen
        try:
            lid = get_current_leerling_id(None)
        except Exception:
            lid = 16
        return {"current_leerling_id": lid}

    return app
