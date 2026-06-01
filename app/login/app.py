from flask import Flask, render_template, request, redirect, session
from authentication import AuthSystem

app = Flask(__name__)
app.secret_key = "secret"

auth = AuthSystem()


#LOGIN DOCENT
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        teacher = auth.login_teacher(email, password)

        if teacher:
            session["temp_user"] = teacher

            code = auth.generate_2fa(email)
            print("2FA CODE:", code)  # demo

            return redirect("/verify")

        return "Inloggen mislukt"

    return render_template("login.html")


#2FA
@app.route("/verify", methods=["GET", "POST"])
def verify():
    user = session.get("temp_user")

    if not user:
        return redirect("/")

    if request.method == "POST":
        code = request.form["code"]

        if auth.verify_2fa(user["email"], code):
            session["user"] = user
            session.pop("temp_user")
            return redirect("/dashboard")

        return "Foute code"

    return render_template("verify.html")


#DASHBOARD DOCENT
@app.route("/dashboard")
def dashboard():
    user = session.get("user")

    if not user:
        return redirect("/")

    return render_template("dashboard.html", user=user)


#WACHTWOORD RESET
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        email = request.form["email"]
        code = request.form["code"]
        new_password = request.form["new_password"]

        if auth.reset_password(email, code, new_password):
            return "Wachtwoord gewijzigd!"

        return "Reset mislukt"

    return render_template("reset.html")


if __name__ == "__main__":
    app.run(debug=True)