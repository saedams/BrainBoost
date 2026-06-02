from app.db import execute_query
from app.models.widget import Widget


class WidgetService:
    """
    Service voor het beheren van dashboardwidgets en gebruikersvoorkeuren.

    Verantwoordelijk voor:
    - Het aanmaken van de benodigde database-tabellen.
    - Het initialiseren van standaardwidgets.
    - Het ophalen van beschikbare widgets voor een gebruiker.
    - Het opslaan van widgetvoorkeuren.
    """

    DEFAULT_WIDGETS = [
        {
            "slug": "vaardigheden",
            "name": "Vaardigheden",
            "description": "Toon of verberg je vaardighedenkaart op het dashboard.",
        },
        {
            "slug": "beheersingsniveau",
            "name": "Beheersingsniveau",
            "description": "Toon of verberg de beheersingsniveau widget.",
        },
        {
            "slug": "aanbevelingen",
            "name": "Aanbevelingen",
            "description": "Toon of verberg persoonlijke aanbevelingen.",
        },
        {
            "slug": "scores",
            "name": "Scores",
            "description": "Toon of verberg het score overzicht op het dashboard.",
        },
    ]

    # Ondersteuning voor oudere widget-slugs zodat bestaande data
    # automatisch kan worden gemigreerd.
    LEGACY_SLUGS = {
        "skills": "vaardigheden",
        "mistakes": "beheersingsniveau",
        "recommendation": "aanbevelingen",
    }

    def __init__(self):
        """
        Initialiseert de service en zorgt ervoor dat de benodigde
        database-structuur beschikbaar is.
        """
        self.ensure_widget_tables()

    def ensure_widget_tables(self):
        """
        Maakt de widgettabellen aan indien deze nog niet bestaan.

        Na het aanmaken worden de standaardwidgets gecontroleerd en
        indien nodig toegevoegd of bijgewerkt.
        """
        execute_query(
            """
            CREATE TABLE IF NOT EXISTS dashboard_widget (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            )
            """
        )

        execute_query(
            """
            CREATE TABLE IF NOT EXISTS student_widget (
                student_id INT NOT NULL,
                widget_id INT NOT NULL,
                PRIMARY KEY (student_id, widget_id),
                FOREIGN KEY (widget_id) REFERENCES dashboard_widget(id)
            )
            """
        )

        self.seed_default_widgets()

    def seed_default_widgets(self):
        """
        Synchroniseert de standaardwidgets met de database.

        - Voegt ontbrekende widgets toe.
        - Werkt naam en beschrijving bij wanneer deze gewijzigd zijn.
        - Migreert oudere slugs naar de huidige naamgeving.
        """
        for widget in self.DEFAULT_WIDGETS:
            existing = execute_query(
                "SELECT id, name, description FROM dashboard_widget WHERE slug = ?",
                (widget["slug"],),
            )

            if existing:
                current = existing[0] if isinstance(existing, list) and existing else None

                # Werk metadata bij wanneer de configuratie is gewijzigd.
                if current and (
                    current.get("name") != widget["name"]
                    or current.get("description") != widget["description"]
                ):
                    execute_query(
                        "UPDATE dashboard_widget SET name = ?, description = ? WHERE slug = ?",
                        (widget["name"], widget["description"], widget["slug"]),
                    )
                continue

            # Controleer of deze widget eerder een andere slug gebruikte.
            legacy_slug = next(
                (
                    old_slug
                    for old_slug, new_slug in self.LEGACY_SLUGS.items()
                    if new_slug == widget["slug"]
                ),
                None,
            )

            if legacy_slug:
                legacy_row = execute_query(
                    "SELECT id FROM dashboard_widget WHERE slug = ?",
                    (legacy_slug,),
                )

                # Migreer bestaande widget naar de nieuwe slug.
                if legacy_row:
                    execute_query(
                        "UPDATE dashboard_widget SET slug = ?, name = ?, description = ? WHERE slug = ?",
                        (
                            widget["slug"],
                            widget["name"],
                            widget["description"],
                            legacy_slug,
                        ),
                    )
                    continue

            execute_query(
                "INSERT INTO dashboard_widget (name, slug, description) VALUES (?, ?, ?)",
                (widget["name"], widget["slug"], widget["description"]),
            )

    def get_available_widgets(self, user_id):
        """
        Haalt alle beschikbare widgets op voor een gebruiker.

        Geeft per widget aan of deze momenteel geselecteerd is.

        Args:
            user_id (int): ID van de gebruiker.

        Returns:
            list[Widget]: Lijst met beschikbare widgets.
        """
        query = """
        SELECT w.id,
               w.name,
               w.slug,
               w.description,
               CASE WHEN sw.student_id IS NOT NULL THEN 1 ELSE 0 END AS selected
        FROM dashboard_widget w
        LEFT JOIN student_widget sw 
            ON w.id = sw.widget_id
           AND sw.student_id = ?
        ORDER BY w.id
        """
        # LEFT JOIN: Geef ALLE widgets terug, en voeg data toe als die bestaat in student_widget

        rows = execute_query(query, (user_id,))

        if not isinstance(rows, list):
            rows = []

        widgets = []
        has_selection = any(
            isinstance(row, dict) and (row.get("selected") == 1 or row.get("selected") == "1")
            for row in rows
        )

        for row in rows:
            if not isinstance(row, dict):
                continue

            selected = (row.get("selected") == 1 or row.get("selected") == "1")
            if not has_selection:
                selected = True

            widgets.append(
                Widget(
                    widget_id=row.get("id"),
                    name=row.get("name"),
                    slug=row.get("slug"),
                    description=row.get("description"),
                    selected=selected,
                    metadata={
                        "source": "widget_service",
                        "type": "dashboard",
                    },
                    tags=["dashboard", "preference"],
                )
            )

        return widgets

    def save_user_widget_selection(self, user_id, selected_slugs):
        """
        Slaat de widgetselectie van een gebruiker op.

        Bestaande voorkeuren worden eerst verwijderd waarna de nieuwe
        selectie wordt opgeslagen.

        Args:
            user_id (int): ID van de gebruiker.
            selected_slugs (list[str]): Geselecteerde widget-slugs.
        """
        # Verwijder bestaande voorkeuren.
        execute_query(
            "DELETE FROM student_widget WHERE student_id = ?",
            (user_id,),
        )

        if not selected_slugs:
            return

        placeholders = ",".join(["?"] * len(selected_slugs))

        query = f"""
            SELECT id
            FROM dashboard_widget
            WHERE slug IN ({placeholders})
        """

        rows = execute_query(query, tuple(selected_slugs))

        widget_ids = [
            row.get("id")
            for row in (rows or [])
            if row.get("id") is not None
        ]

        # Koppel de geselecteerde widgets aan de gebruiker.
        for widget_id in widget_ids:
            execute_query(
                """
                INSERT INTO student_widget (student_id, widget_id)
                VALUES (?, ?)
                """,
                (user_id, widget_id),
            )