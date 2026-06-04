"""
Unit tests voor de leerlingroutes.

Deze tests gebruiken een tijdelijke Flask-app en patchen database- en
service-aanroepen zodat de pagina's zonder echte API-requests getest kunnen worden.
"""

import os
from pathlib import Path

import pytest
from flask import Flask


@pytest.fixture
def app():
    from app.main import bp as main_bp
    from app.contact import bp as contact_bp

    root = Path(__file__).resolve().parents[1]
    templates_path = root / 'app' / 'templates'

    app = Flask(__name__, template_folder=str(templates_path))
    app.config['TESTING'] = True
    app.secret_key = 'test-secret'
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    return app


def test_leerlingen_route_renders_student_list(monkeypatch, app):
    from app.main import leerling

    def fake_execute_query(query, values=None):
        return [
            {'id': 1, 'naam': 'Jan', 'klas': '6A'},
            {'id': 2, 'naam': 'Sara', 'klas': '5B'},
        ]

    monkeypatch.setattr(leerling, 'execute_query', fake_execute_query)

    with app.test_client() as client:
        response = client.get('/leerlingen')

    assert response.status_code == 200
    page_text = response.get_data(as_text=True)
    assert 'Jan' in page_text
    assert 'Sara' in page_text
    assert '/leerling/1' in page_text
    assert '/leerling/2' in page_text


def test_leerling_detail_route_shows_score_and_fouten(monkeypatch, app):
    from app.main import leerling

    class FakeLeerling:
        def __init__(self):
            self.id = 1
            self.naam = 'Jan'
            self.klas = '6A'
            self.email = 'jan@example.com'

        def get_resultaten(self):
            return [{'onderwerp': 'Rekenen', 'score': 62}]

        def get_fouten(self):
            return [{'categorie': 'Leesfout', 'subcategorie': 'begrip', 'aantal': 2}]

        def group_fouten_by_categorie(self, fouten):
            return {'Leesfout': fouten}

        def get_advies(self, resultaten):
            return ('Kijk beter naar tekstbegrip.', 'Oefen extra met vraagstukken.')

        def find_zwak_onderwerp(self, resultaten):
            return ('Rekenen', 62)

    class FakeFoutAnalyseService:
        def get_fout_analyse_dashboard_data(self, student_id):
            class DummyData:
                def to_dict(self):
                    return {
                        'mistakes_by_subject': {
                            'Rekenen': {
                                'percentage': 100,
                                'mistakes': [
                                    {'mistake_type': 'Leesfout', 'count': 2}
                                ]
                            }
                        },
                        'common_mistakes': [
                            {'mistake_type': 'Leesfout', 'count': 2}
                        ],
                        'recommendation': 'Lees de vraag zorgvuldig.',
                    }
            return DummyData()

    def fake_execute_query(query, values=None):
        if 'SUM(sa.score)' in query:
            return [{'total_score': 16, 'total_max': 20}]
        if 'SELECT score, max_score' in query:
            return [{'score': 8, 'max_score': 10}, {'score': 8, 'max_score': 10}]
        return []

    monkeypatch.setattr(leerling.Leerling, 'from_id', staticmethod(lambda x: FakeLeerling()))
    monkeypatch.setattr(leerling, 'FoutAnalyseService', lambda: FakeFoutAnalyseService())
    monkeypatch.setattr(leerling, 'execute_query', fake_execute_query)

    with app.test_client() as client:
        response = client.get('/leerling/1')

    assert response.status_code == 200
    page_text = response.get_data(as_text=True)
    assert 'Jan' in page_text
    assert 'Rekenen' in page_text
    assert 'Leesfout' in page_text
    assert 'Gemiddelde score' in page_text
