from flask import redirect, render_template, request, url_for
from app.services.widget_service import WidgetService
from app.utils.student_helper import get_current_leerling_id


class WidgetController:
    """
    Controller voor het beheren van dashboardwidget-voorkeuren.

    Verantwoordelijk voor het ophalen, tonen en opslaan van de
    widgetselectie van een gebruiker.
    """

    def __init__(self):
        """
        Initialiseert de controller.

        De WidgetService wordt lazy-loaded via de service-property.
        """
        self._service = None

    @property
    def service(self):
        """
        Geeft een instantie van WidgetService terug.

        De service wordt pas aangemaakt wanneer deze voor het eerst
        nodig is.

        Returns:
            WidgetService: Service voor widget-gerelateerde logica.
        """
        if self._service is None:
            self._service = WidgetService()
        return self._service

    def render_preferences(self, user_id=None):
        """
        Toont de pagina met beschikbare widgetvoorkeuren.

        Args:
            user_id (int, optional): ID van de gebruiker. Indien niet
                opgegeven wordt de huidige leerling bepaald.

        Returns:
            Response: Gerenderde voorkeurenpagina.
        """
        user_id = get_current_leerling_id(user_id)

        # Haal alle beschikbare widgets voor de gebruiker op
        widgets = self.service.get_available_widgets(user_id)

        return render_template(
            "widget_preferences.html",
            widgets=[widget.to_dict() for widget in widgets],
        )

    def update_preferences(self, user_id=None):
        """
        Slaat de geselecteerde widgetvoorkeuren van de gebruiker op.

        Args:
            user_id (int, optional): ID van de gebruiker. Indien niet
                opgegeven wordt de huidige leerling bepaald.

        Returns:
            Response: Redirect naar de homepagina.
        """
        user_id = get_current_leerling_id(user_id)

        # Lees de geselecteerde widgets uit het formulier
        selected_slugs = request.form.getlist("widgets")

        # Sla de selectie op voor de gebruiker
        self.service.save_user_widget_selection(user_id, selected_slugs)

        return redirect(url_for("main.home"))


# Centrale controllerinstantie voor widgetvoorkeuren
controller = WidgetController()