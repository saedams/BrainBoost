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
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        auth_instance = get_auth()
        teacher = auth_instance.login_teacher(email, password)
        if teacher:
            session["user"] = teacher
            session["role"] = teacher.get("role", "docent")
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
