from flask import request
from app.main import bp
from app.controllers.widget_controller import controller


class WidgetRoutes:
    """
    Registreert alle routes die betrekking hebben op widgetvoorkeuren.

    Deze klasse koppelt URL-endpoints aan de juiste controller-methodes.
    """

    def __init__(self, blueprint):
        """
        Initialiseert de route-registratie.

        Args:
            blueprint: Flask Blueprint waarop de routes worden geregistreerd.
        """
        self.bp = blueprint
        self.register_routes()

    def register_routes(self):
        """
        Registreert de endpoint voor het beheren van widgetvoorkeuren.

        GET  -> Toont het voorkeurenscherm.
        POST -> Slaat gewijzigde voorkeuren op.
        """
        self.bp.add_url_rule(
            "/widget-preferences",
            endpoint="widget_preferences",
            view_func=self.widget_preferences,
            methods=["GET", "POST"],
        )
        self.bp.add_url_rule(
            "/dashboard-widgets",
            endpoint="dashboard_widgets",
            view_func=self.widget_preferences,
            methods=["GET", "POST"],
        )

    def widget_preferences(self):
        """
        Verwerkt verzoeken voor widgetvoorkeuren.

        Returns:
            Response:
                - POST: resultaat van het opslaan van voorkeuren.
                - GET: pagina met huidige widgetvoorkeuren.
        """
        # Verwerk het opslaan van voorkeuren
        if request.method == "POST":
            return controller.update_preferences()

        # Toon het voorkeurenscherm
        return controller.render_preferences()


# Registreer de widgetroutes op de applicatie-blueprint
WidgetRoutes(bp)