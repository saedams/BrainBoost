"""
Unit Tests – Foutenanalyse

Pytest unit tests voor de FoutAnalyseService module.

Deze tests controleren:
- calculate_percentages() berekeningen
- FoutAnalyseData.to_dict() conversie naar template data
- Lege data situaties (edge cases)

Test aanpak:
- Mockdata gebruikt (geen echte database calls)
- Test classes alleen voor overzichtelijke code organisatie
"""

import pytest
from app.services.fout_analyse_service import FoutAnalyseData, FoutAnalyseService


class TestFoutAnalyseData:
    """
    Unit tests voor FoutAnalyseData.to_dict() conversie.
    """

    def test_fout_analyse_data_to_dict(self):
        """
        Controleert of to_dict() correct werkt.
        """

        data = FoutAnalyseData(
            mistakes_by_subject={'Natuurkunde': []},
            common_mistakes=[{'mistake_type': 'Leesfout', 'count': 2}],
            recommendation="Lees instructies zorgvuldig",
            subjects=[{'id': 2, 'name': 'Natuurkunde'}],
            selected_subject_id=2,
            current_student_id=17
        )

        result_dict = data.to_dict()

        assert isinstance(result_dict, dict)
        assert 'mistakes_by_subject' in result_dict
        assert 'common_mistakes' in result_dict
        assert 'recommendation' in result_dict
        assert 'subjects' in result_dict
        assert 'selected_subject_id' in result_dict
        assert 'current_student_id' in result_dict

        assert result_dict['current_student_id'] == 17
        assert result_dict['selected_subject_id'] == 2


class TestFoutAnalyseServiceCalculations:
    """
    Unit tests voor calculate_percentages() berekeningen.
    """

    @staticmethod
    def create_test_service():
        """
        Maak een FoutAnalyseService instance voor testing.
        """
        return FoutAnalyseService()

    def test_calculate_percentages_basic(self):
        """
        Controleert percentage berekeningen.
        """

        service = self.create_test_service()

        # Mockdata: 2 vakken met verschillende fouten
        test_data = {
            'Wiskunde': [
                {'mistake_type': 'Berekeningsfout', 'count': 60},
                {'mistake_type': 'Formulefout', 'count': 40}
            ],
            'Natuurkunde': [
                {'mistake_type': 'Eenhedenfout', 'count': 100}
            ]
        }

        result = service.calculate_percentages(test_data)

        # Totaal = 200 fouten
        assert result['Wiskunde']['percentage'] == 50.0
        assert result['Wiskunde']['total'] == 100
        assert result['Natuurkunde']['percentage'] == 50.0
        assert result['Natuurkunde']['total'] == 100

    def test_calculate_percentages_empty_data(self):
        """
        Controleert lege data situaties.
        """

        service = self.create_test_service()

        result = service.calculate_percentages({})

        assert result == {}
        assert isinstance(result, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])