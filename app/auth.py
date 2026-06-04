"""Compatibele auth wrapper voor de Flask app.

Sommige tests importeren `app.auth`, dus deze module biedt dezelfde
API als de bestaande `AuthSystem`.
"""

from app.login.authentication import AuthSystem

_auth = AuthSystem()


def login_teacher(email, password):
    return _auth.login_teacher(email, password)


def login_student(email, password):
    return _auth.login_student(email, password)


def create_reset_code(email):
    return _auth.create_reset_code(email)


def reset_password(email, code, new_password):
    return _auth.reset_password(email, code, new_password)
