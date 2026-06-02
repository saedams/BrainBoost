import random
from app.db import execute_query
from werkzeug.security import check_password_hash


class AuthSystem:
    def __init__(self):
        # Hardcoded docent accounts (demo/test data)
        self.teachers = [
            {
                "email": "docent@test.nl",
                "password": "1234",
                "role": "docent",
                "name": "Docent Demo"
            }
        ]

        # Opslag voor reset codes per email
        self.reset_codes = {}


    def login_teacher(self, email, password):
        # Controleer login voor docenten via harde lijst
        for teacher in self.teachers:
            if teacher["email"] == email and teacher["password"] == password:
                return teacher
        return None

    def login_student(self, email, password):
        # Basis validatie: lege input weigeren
        if not email or not password:
            return None

        # Haal leerling op uit database
        rows = execute_query(
            "SELECT id, naam, email, wachtwoord_hash FROM leerling WHERE email = ?",
            (email,)
        )

        # Geen leerling gevonden in database
        if not rows:
            # Fallback demo account voor testen
            if email == "leerling@test.nl" and password == "1234":
                return {
                    "id": None,
                    "name": "Leerling Demo",
                    "email": email,
                    "role": "leerling",
                }
            return None

        student = rows[0]
        wachtwoord_hash = student.get("wachtwoord_hash")

        # Case 1: geen wachtwoord hash aanwezig (demo dataset)
        if wachtwoord_hash is None:
            if password == "1234":
                return {
                    "id": student.get("id"),
                    "name": student.get("naam"),
                    "email": student.get("email"),
                    "role": "leerling",
                }
            return None

        # Case 2: onveilige plain-text vergelijking (legacy/demo)
        if wachtwoord_hash == password:
            return {
                "id": student.get("id"),
                "name": student.get("naam"),
                "email": student.get("email"),
                "role": "leerling",
            }

        # Case 3: veilige wachtwoord hash controle (werkzeug)
        try:
            if check_password_hash(wachtwoord_hash, password):
                return {
                    "id": student.get("id"),
                    "name": student.get("naam"),
                    "email": student.get("email"),
                    "role": "leerling",
                }
        except ValueError:
            # Foutieve hash wordt genegeerd
            pass

        # Login mislukt
        return None

    def create_reset_code(self, email):
        # Genereer 4-cijferige reset code
        code = str(random.randint(1000, 9999))

        # Sla reset code op per email
        self.reset_codes[email] = code

        return code

    def reset_password(self, email, code, new_password):
        # Controleer of reset code klopt
        if self.reset_codes.get(email) == code:

            # Zoek docent en wijzig wachtwoord
            for teacher in self.teachers:
                if teacher["email"] == email:
                    teacher["password"] = new_password
                    return True

        # Reset mislukt (code of email klopt niet)
        return False