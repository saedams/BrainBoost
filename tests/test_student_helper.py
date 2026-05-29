"""
Unit tests voor de leerling helper.

Deze tests controleren de fallback-logica voor het bepalen van de
huidige leerling-ID.
"""

from flask import Flask

from app.utils.student_helper import DEMO_LEERLING_ID, get_current_leerling_id


def test_get_current_leerling_id_uses_route_parameter():
    app = Flask(__name__)

    with app.test_request_context('/?leerling_id=5'):
        assert get_current_leerling_id(12) == 12


def test_get_current_leerling_id_uses_query_parameter():
    app = Flask(__name__)

    with app.test_request_context('/?leerling_id=5'):
        assert get_current_leerling_id(None) == 5


def test_get_current_leerling_id_uses_session_value():
    app = Flask(__name__)
    app.secret_key = 'test'

    with app.test_request_context('/') as ctx:
        ctx.session['leerling_id'] = 7
        assert get_current_leerling_id(None) == 7


def test_get_current_leerling_id_uses_demo_fallback_when_no_id():
    app = Flask(__name__)

    with app.test_request_context('/'):
        assert get_current_leerling_id(None) == DEMO_LEERLING_ID
