# Import van de Flask app die we gaan testen
from app import app

# Mock gebruiken om externe afhankelijkheden (AuthSystem) te simuleren
from unittest.mock import patch

import pytest


# -------------------------
# TEST FIXTURE
# -------------------------
@pytest.fixture
def client():
    """
    Maakt een test client aan voor de Flask applicatie.

    Hiermee kunnen we HTTP requests simuleren zonder een echte server te starten.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# -------------------------
# LOGIN TESTS
# -------------------------
def test_login_success(client):
    """
    Test of login succesvol verloopt wanneer correcte gegevens worden ingevoerd.
    """

    # Mock de login_teacher functie zodat we geen echte database gebruiken
    with patch("app.auth.login_teacher") as mock_login:
        mock_login.return_value = {
            "name": "Docent",
            "email": "docent@test.nl"
        }

        # Simuleer POST request naar login endpoint
        response = client.post(
            "/",
            data={
                "email": "docent@test.nl",
                "password": "1234"
            },
            follow_redirects=True  # volg redirect naar dashboard
        )

        # Controleer of request succesvol is verwerkt
        assert response.status_code == 200


def test_login_failed(client):
    """
    Test of login mislukt wanneer verkeerde gegevens worden ingevoerd.
    """

    # Mock login zodat het systeem "None" teruggeeft (geen gebruiker gevonden)
    with patch("app.auth.login_teacher") as mock_login:
        mock_login.return_value = None

        # Simuleer foutieve login
        response = client.post(
            "/",
            data={
                "email": "fout@test.nl",
                "password": "verkeerd"
            }
        )

        # Controleer of foutmelding zichtbaar is in response
        assert b"Inloggen mislukt" in response.data


# -------------------------
# DASHBOARD TEST
# -------------------------
def test_dashboard_without_login(client):
    """
    Test of gebruiker wordt doorgestuurd als hij niet ingelogd is.
    """

    response = client.get("/dashboard")

    # 302 = redirect (naar login pagina)
    assert response.status_code == 302


# -------------------------
# RESET WACHTWOORD TESTS
# -------------------------
def test_reset_success(client):
    """
    Test of wachtwoord reset succesvol werkt.
    """

    # Mock reset functie als succesvol
    with patch("app.auth.reset_password") as mock_reset:
        mock_reset.return_value = True

        response = client.post(
            "/reset",
            data={
                "email": "test@test.nl",
                "code": "123456",
                "new_password": "nieuw123"
            }
        )

        # Controleer succesmelding
        assert b"Wachtwoord gewijzigd!" in response.data


def test_reset_failed(client):
    """
    Test of foutmelding verschijnt bij mislukte reset.
    """

    # Mock reset functie als mislukt
    with patch("app.auth.reset_password") as mock_reset:
        mock_reset.return_value = False

        response = client.post(
            "/reset",
            data={
                "email": "test@test.nl",
                "code": "fout",
                "new_password": "nieuw123"
            }
        )

        # Controleer foutmelding
        assert b"Reset mislukt" in response.data