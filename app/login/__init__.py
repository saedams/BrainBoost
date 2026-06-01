from flask import Blueprint, render_template, request, redirect, session, url_for

bp = Blueprint("login", __name__, template_folder=".")

auth = None


def get_auth():
    global auth
    if auth is None:
        from .authentication import AuthSystem
        auth = AuthSystem()
    return auth


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        if session.get("role") == "docent":
            return redirect(url_for("main.leerlingen"))
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        roles = request.form.getlist("role")

        if not roles:
            return render_template("login.html", error="Selecteer Docent of Leerling.")

        auth_instance = get_auth()
        
        user = None
        role = roles[0]
        
        if role == "docent":
            user = auth_instance.login_teacher(email, password)
        elif role == "leerling":
            user = auth_instance.login_student(email, password)
        
        if user:
            session["user"] = user
            session["role"] = user.get("role", role)
            if session["role"] == "leerling":
                session["leerling_id"] = user.get("id")
            else:
                session.pop("leerling_id", None)

            if session["role"] == "docent":
                return redirect(url_for("main.leerlingen"))
            return redirect(url_for("main.home"))

        return render_template("login.html", error="Inloggen mislukt. Controleer je gegevens.")

    return render_template("login.html")


@bp.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        email = request.form.get("email")
        code = request.form.get("code")
        new_password = request.form.get("new_password")

        auth_instance = get_auth()
        if auth_instance.reset_password(email, code, new_password):
            return render_template("reset.html", message="Wachtwoord gewijzigd. Je kunt nu opnieuw inloggen.")

        return render_template("reset.html", error="Reset mislukt. Controleer je gegevens.")

    return render_template("reset.html")


@bp.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("login.login"))
