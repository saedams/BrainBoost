class Widget:
    """
    Model dat een dashboardwidget representeert inclusief selectie-status.

    Deze klasse wordt gebruikt om widgetdata vanuit de database
    te structureren en te manipuleren binnen de applicatie.
    """

    def __init__(self, widget_id, name, slug, description, selected=False, metadata=None, tags=None):
        """
        Initialiseert een Widget-instantie.

        Args:
            widget_id (int): Unieke ID van de widget.
            name (str): Weergavenaam van de widget.
            slug (str): Unieke identifier (bijv. 'vaardigheden').
            description (str): Omschrijving van de widget.
            selected (bool, optional): Of de widget actief is voor de gebruiker.
            metadata (dict, optional): Extra configuratie- en contextinformatie.
            tags (list, optional): Labels voor categorisering.
        """
        self.id = widget_id
        self.name = name
        self.slug = slug
        self.description = description

        # Zorg ervoor dat selected altijd een boolean is
        self.selected = bool(selected)

        # Default metadata als er niets wordt meegegeven
        self.metadata = metadata or {
            "category": "dashboard_widget",
            "version": 1,
            "settings": {}
        }

        # Default tags voor filtering en grouping
        self.tags = tags or ["dashboard", "insight"]

    def to_dict(self):
        """
        Converteert het Widget-object naar een dictionary.

        Handig voor JSON-responses en template rendering.

        Returns:
            dict: Representatie van de widget.
        """
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "selected": self.selected,
            "metadata": self.metadata,
            "tags": self.tags,
        }

    def toggle(self):
        """
        Wisselt de geselecteerde status van de widget om.

        True → False of False → True
        """
        self.selected = not self.selected