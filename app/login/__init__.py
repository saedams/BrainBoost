from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash

from app.db import execute_query

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
# REGISTRATIE ROUTE
# -------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        if not username or not email or not password or not password_confirm:
            flash("Vul alle velden in.", "error")
            return render_template("register.html")

        if password != password_confirm:
            flash("Wachtwoorden komen niet overeen.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Het wachtwoord moet minimaal 6 tekens bevatten.", "error")
            return render_template("register.html")

        existing = execute_query(
            "SELECT id FROM leerling WHERE email = ?",
            (email,)
        )
        if existing:
            flash("Er bestaat al een account met dit e-mailadres.", "error")
            return render_template("register.html")

        try:
            wachtwoord_hash = generate_password_hash(password)
            execute_query(
                "INSERT INTO leerling (naam, email, wachtwoord_hash) VALUES (?, ?, ?)",
                (username, email, wachtwoord_hash)
            )
            flash("Account is aangemaakt. Je kunt nu inloggen.", "success")
            return redirect(url_for("login.login"))
        except Exception as e:
            flash(f"Fout bij registreren: {e}", "error")
            return render_template("register.html")

    return render_template("register.html")


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

        from app import auth
        # Wachtwoord reset proberen via compatibele app.auth wrapper
        if auth.reset_password(email, code, new_password):
            return "Wachtwoord gewijzigd!"

        # Foutmelding bij mislukte reset
        return "Reset mislukt"

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