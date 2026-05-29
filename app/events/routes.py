from dateutil.parser import isoparse

from flask import abort, redirect, render_template, request, url_for

from app.events import bp, create_event, get_event, get_events, update_event


class EventRoutes:
    """Object-georiënteerde router voor events."""

    def __init__(self, blueprint):
        self.bp = blueprint
        self.register_routes()

    def register_routes(self):
        self.bp.add_url_rule("/", endpoint="index", view_func=self.index)
        self.bp.add_url_rule("/view/<int:event_id>", endpoint="view", view_func=self.view)
        self.bp.add_url_rule("/create", endpoint="create", view_func=self.create, methods=["GET", "POST"])
        self.bp.add_url_rule("/edit/<int:event_id>", endpoint="edit", view_func=self.edit, methods=["GET", "POST"])

    def index(self):
        """Returns the events index page."""
        events = get_events()
        return render_template("events/index.html", events=events)

    def view(self, event_id):
        event = get_event(event_id) or abort(404)
        event["eventDate"] = isoparse(event["eventDate"])
        return render_template("events/view.html", event=event)

    def create(self):
        if request.method == "POST":
            description = request.form["description"]
            date = request.form["date"]
            event_id = create_event(description, date)

            if not event_id:
                return render_template(
                    "events/create.html",
                    error="Event kon niet worden aangemaakt, zorg dat de datum in de toekomst ligt."
                )
            return redirect(url_for("events.view", event_id=event_id))

        return render_template("events/create.html")

    def edit(self, event_id):
        if request.method == "POST":
            description = request.form["description"]
            date = request.form["date"]
            update_event(event_id, description, date)
            return redirect(url_for("events.view", event_id=event_id))

        event = get_event(event_id) or abort(404)
        event["eventDate"] = isoparse(event["eventDate"])
        return render_template("events/edit.html", event=event)


EventRoutes(bp)
