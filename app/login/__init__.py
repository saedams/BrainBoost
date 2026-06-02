from flask import Blueprint, render_template, request, redirect, session, url_for

# Blueprint: maakt dit onderdeel van de app modulair (login-functionaliteit apart)
bp = Blueprint("login", __name__, template_folder=".")

# Variabele voor AuthSystem (wordt later pas aangemaakt)
auth = None


# Functie om AuthSystem maar 1 keer aan te maken (lazy loading)
def get_auth():
    global auth
    if auth is None:
        # import hier voorkomt circular import problemen
        from .authentication import AuthSystem
        auth = AuthSystem()
    return auth


# -------------------------
# LOGIN ROUTE
# -------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():

    # Als gebruiker al ingelogd is, direct doorsturen
    if session.get("user"):
        if session.get("role") == "docent":
            return redirect(url_for("main.leerlingen"))
        return redirect(url_for("main.home"))

    # Alleen uitvoeren bij formulier-submit
    if request.method == "POST":

        # Gegevens uit login-formulier ophalen
        email = request.form.get("email")
        password = request.form.get("password")
        roles = request.form.getlist("role")

        # Check of rol gekozen is
        if not roles:
            return render_template("login.html", error="Selecteer Docent of Leerling.")

        auth_instance = get_auth()

        user = None
        role = roles[0]

        # Login afhankelijk van rol
        if role == "docent":
            user = auth_instance.login_teacher(email, password)
        elif role == "leerling":
            user = auth_instance.login_student(email, password)

        # Als login succesvol is
        if user:
            session["user"] = user
            session["role"] = user.get("role", role)

            # Extra data opslaan voor leerlingen
            if session["role"] == "leerling":
                session["leerling_id"] = user.get("id")
            else:
                session.pop("leerling_id", None)

            # Doorsturen naar juiste pagina
            if session["role"] == "docent":
                return redirect(url_for("main.leerlingen"))
            return redirect(url_for("main.home"))

        # Foutmelding bij verkeerde login
        return render_template("login.html", error="Inloggen mislukt. Controleer je gegevens.")

    # GET request → toon loginpagina
    return render_template("login.html")


# -------------------------
# RESET WACHTWOORD ROUTE
# -------------------------
@bp.route("/reset", methods=["GET", "POST"])
def reset():

    if request.method == "POST":

        # Formuliergegevens ophalen
        email = request.form.get("email")
        code = request.form.get("code")
        new_password = request.form.get("new_password")

        auth_instance = get_auth()

        # Wachtwoord reset proberen
        if auth_instance.reset_password(email, code, new_password):
            return render_template(
                "reset.html",
                message="Wachtwoord gewijzigd. Je kunt nu opnieuw inloggen."
            )

        # Foutmelding bij mislukte reset
        return render_template(
            "reset.html",
            error="Reset mislukt. Controleer je gegevens."
        )

    # GET request → toon resetpagina
    return render_template("reset.html")


# -------------------------
# LOGOUT ROUTE
# -------------------------
@bp.route("/logout")
def logout():

    # Sessie leegmaken (gebruiker uitloggen)
    session.pop("user", None)
    session.pop("role", None)

    # Terug naar loginpagina
    return redirect(url_for("login.login"))