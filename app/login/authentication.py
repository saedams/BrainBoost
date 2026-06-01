import random

class AuthSystem:
    def __init__(self):
        self.teachers = [
            {"email": "docent@test.nl", "password": "1234", "role": "docent"}
        ]
        self.reset_codes = {}
        self.verification_codes = {}

    def login_teacher(self, email, password):
        for teacher in self.teachers:
            if teacher["email"] == email and teacher["password"] == password:
                return teacher
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
