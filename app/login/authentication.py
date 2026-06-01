import random
from app.db import execute_query
from werkzeug.security import check_password_hash

class AuthSystem:
    def __init__(self):
        self.teachers = [
            {"email": "docent@test.nl", "password": "1234", "role": "docent", "name": "Docent Demo"}
        ]
        self.reset_codes = {}
        self.verification_codes = {}

    def login_teacher(self, email, password):
        for teacher in self.teachers:
            if teacher["email"] == email and teacher["password"] == password:
                return teacher
        return None

    def login_student(self, email, password):
        if not email or not password:
            return None

        rows = execute_query(
            "SELECT id, naam, email, wachtwoord_hash FROM leerling WHERE email = ?",
            (email,)
        )

        if not rows:
            # Fallback demo leerling account for sample testing
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

        if wachtwoord_hash is None:
            # Sample dataset uses empty wachtwoord_hash for default demo passwords.
            if password == "1234":
                return {
                    "id": student.get("id"),
                    "name": student.get("naam"),
                    "email": student.get("email"),
                    "role": "leerling",
                }
            return None

        if wachtwoord_hash == password:
            return {
                "id": student.get("id"),
                "name": student.get("naam"),
                "email": student.get("email"),
                "role": "leerling",
            }

        try:
            if check_password_hash(wachtwoord_hash, password):
                return {
                    "id": student.get("id"),
                    "name": student.get("naam"),
                    "email": student.get("email"),
                    "role": "leerling",
                }
        except ValueError:
            pass

        return None

    def generate_2fa(self, email):
        code = str(random.randint(100000, 999999))
        self.verification_codes[email] = code
        return code

    def verify_2fa(self, email, code):
        return self.verification_codes.get(email) == code

    def create_reset_code(self, email):
        code = str(random.randint(1000, 9999))
        self.reset_codes[email] = code
        return code

    def reset_password(self, email, code, new_password):
        if self.reset_codes.get(email) == code:
            for teacher in self.teachers:
                if teacher["email"] == email:
                    teacher["password"] = new_password
                    return True
        return False
