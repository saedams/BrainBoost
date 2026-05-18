"""Entry point for Flask application"""

from flask import Flask

from app.events import bp as events_bp
from app.main import bp as main_bp
from app.contact import bp as contact_bp


def create_app():
    app = Flask(__name__)
    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
    app.config["SECRET_KEY"] = "DokkiePythoniAXRvULKWuFyfURRrG0YTOOTXswLJWpU"
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.config.from_pyfile("settings.py")

    app.register_blueprint(main_bp)
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(contact_bp)

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
