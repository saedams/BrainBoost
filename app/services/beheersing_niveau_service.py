"""
Beheersingsniveau module voor Brain Boost

Dit bestand bevat alle logica voor het beheersingsniveau dashboard.
De service haalt data op uit de database en berekent beheersingsniveaustatistieken.
"""

from app.db import execute_query
from app.utils.student_helper import get_current_leerling_id
from flask import render_template


# DEFINITIE: BEHEERSINGSNIVEAU DATA KLASSE
# Deze klasse bevat alle data die voor het beheersingsniveau dashboard nodig is.
# Dit zorgt voor een schone weergave en makkelijke passing naar templates.
class BeheersingNiveauData:
    """
    Container voor alle beheersingsniveau data.
    """

    def __init__(self, mistakes_by_subject=None, common_mistakes=None,
                 recommendation="", subjects=None, selected_subject_id=None,
                 current_student_id=None):
        self.mistakes_by_subject = mistakes_by_subject or {}
        self.common_mistakes = common_mistakes or []
        self.recommendation = recommendation
        self.subjects = subjects or []
        self.selected_subject_id = selected_subject_id
        self.current_student_id = current_student_id

    def to_dict(self):
        """
        Zet alle data om naar een dictionary voor template passing.
        """
        return {
            'mistakes_by_subject': self.mistakes_by_subject,
            'common_mistakes': self.common_mistakes,
            'recommendation': self.recommendation,
            'subjects': self.subjects,
            'selected_subject_id': self.selected_subject_id,
            'current_student_id': self.current_student_id
        }


# DEFINITIE: BEHEERSINGSNIVEAU SERVICE KLASSE
# Deze service bevat alle logica voor het ophalen en berekenen van beheersingsniveaudata.
# De klasse communiceert met de database en bereikt alle berekeningen.
class BeheersingNiveauService:
    """
    Service voor het analyseren van beheersingsniveaus van leerlingen.
    Bevat methodes voor het ophalen, groeperen en analyseren van beheersingsniveaudata.
    """

    def __init__(self):
        self.mistake_types = [
            'Berekeningsfout',
            'Formulefout',
            'Afrondingsfout',
            'Stappen ontbreken',
            'Leesfout',
            'Eenhedenfout'
        ]

    # DEFINITIE: BEHEERSINGSNIVEAUS PER VAK OPHALEN
    # Deze methode haalt de beheersingsniveaus van een leerling op uit de database
    # en groepeert deze per vak. De uitkomst wordt gebruikt voor de grafiek
    # op de Beheersingsniveau-pagina.
    def get_mistakes_by_subject(self, student_id):
        """
        Haalt alle beheersingsniveaus van een leerling op en groepeert ze per vak.

        Args:
            student_id (int): ID van de leerling

        Returns:
            dict: Dictionary met vakken als keys en lijsten van beheersingsniveaus als values
        """
        query = """
        SELECT s.name as subject_name, ma.mistake_type, COUNT(*) as count
        FROM mistake_analysis ma
        JOIN student_answer sa ON ma.student_answer_id = sa.id
        JOIN question q ON sa.question_id = q.id
        JOIN subject s ON q.subject_id = s.id
        WHERE sa.student_id = ?
        GROUP BY s.name, ma.mistake_type
        ORDER BY s.name, count DESC
        """
        results = execute_query(query, (student_id,))

        mistakes_by_subject = {}
        for row in results:
            subject = row['subject_name']
            if subject not in mistakes_by_subject:
                mistakes_by_subject[subject] = []
            mistakes_by_subject[subject].append({
                'mistake_type': row['mistake_type'],
                'count': row['count']
            })

        return mistakes_by_subject

    # DEFINITIE: MEEST VOORKOMENDE BEHEERSINGSNIVEAUS
    # Deze methode haalt de top beheersingsniveaus op en sorteert ze op frequentie.
    # Dit wordt weergegeven in de "Top Beheersingsniveaus Overzicht" kaart.
    def get_common_mistake_types(self, student_id):
        """
        Haalt de meest voorkomende beheersingsniveaus van een leerling op.

        Args:
            student_id (int): ID van de leerling

        Returns:
            list: Gesorteerde lijst van beheersingsniveaus met aantallen
        """
        query = """
        SELECT ma.mistake_type, COUNT(*) as count
        FROM mistake_analysis ma
        JOIN student_answer sa ON ma.student_answer_id = sa.id
        WHERE sa.student_id = ?
        GROUP BY ma.mistake_type
        ORDER BY count DESC
        """
        results = execute_query(query, (student_id,))

        return [{'mistake_type': row['mistake_type'], 'count': row['count']} for row in results]

    # DEFINITIE: LEERLING VAKKEN OPHALEN
    # Haalt alleen unieke vakken op die bij deze leerling horen.
    def get_student_subjects(self, student_id):
        """
        Haalt unieke vakken op voor een specifieke leerling.

        Args:
            student_id (int): ID van de leerling

        Returns:
            list: Lijst van vakken met id en naam
        """
        query = """
        SELECT DISTINCT s.id, s.name
        FROM student_answer sa
        JOIN question q ON sa.question_id = q.id
        JOIN subject s ON q.subject_id = s.id
        WHERE sa.student_id = ?
        ORDER BY s.name
        """
        return execute_query(query, (student_id,))

    # DEFINITIE: BEHEERSINGSNIVEAUPERCENTAGES BEREKENEN
    # Deze methode berekent welk percentage van de beheersingsniveaus bij elk vak hoort.
    # Dit wordt gebruikt voor de beheersingsniveaudistributie grafiek.
    def calculate_percentages(self, data):
        """
        Berekent percentages voor beheersingsniveaus per vak.

        Args:
            data (dict): Data met beheersingsniveaus per vak

        Returns:
            dict: Data met toegevoegde percentages
        """
        total_mistakes = sum(sum(mistake['count'] for mistake in mistakes) for mistakes in data.values())

        if total_mistakes == 0:
            return data

        result = {}
        for subject, mistakes in data.items():
            subject_total = sum(m['count'] for m in mistakes)
            percentage = round((subject_total / total_mistakes) * 100, 1)
            result[subject] = {
                'mistakes': mistakes,
                'total': subject_total,
                'percentage': percentage
            }

        return result

    # DEFINITIE: FILTEREN OP VAK
    # Deze methode filtert de beheersingsniveaus op één specifiek vak.
    # Dit wordt gebruikt wanneer de leerling een vak selecteert in de dropdown.
    def filter_by_subject(self, student_id, subject_id):
        """
        Haalt beheersingsniveaus op voor een specifiek vak.

        Args:
            student_id (int): ID van de leerling
            subject_id (int): ID van het vak

        Returns:
            dict: Beheersingsniveaus voor het specifieke vak
        """
        query = """
        SELECT ma.mistake_type, COUNT(*) as count
        FROM mistake_analysis ma
        JOIN student_answer sa ON ma.student_answer_id = sa.id
        JOIN question q ON sa.question_id = q.id
        WHERE sa.student_id = ? AND q.subject_id = ?
        GROUP BY ma.mistake_type
        ORDER BY count DESC
        """
        results = execute_query(query, (student_id, subject_id))

        return [{'mistake_type': row['mistake_type'], 'count': row['count']} for row in results]

    # DEFINITIE: AANBEVELING GENEREREN
    # Deze methode genereert een persoonlijke aanbeveling op basis van
    # het vak en beheersingsniveau waar de leerling de meeste problemen mee heeft.
    def generate_recommendation(self, student_id):
        """
        Genereert een aanbeveling gebaseerd op de meest voorkomende beheersingsniveaus.

        Args:
            student_id (int): ID van de leerling

        Returns:
            str: Aanbevelingstekst
        """
        common_mistakes = self.get_common_mistake_types(student_id)
        mistakes_by_subject = self.get_mistakes_by_subject(student_id)

        if not common_mistakes:
            return "Geweldig! Geen beheersingsniveaus gevonden om te analyseren."

        # Vind het meest voorkomende beheersingsniveau
        top_mistake = common_mistakes[0]['mistake_type']

        # Vind het vak met de meeste beheersingsniveaus
        subject_totals = {}
        for subject, mistakes in mistakes_by_subject.items():
            subject_totals[subject] = sum(m['count'] for m in mistakes)

        if subject_totals:
            worst_subject = max(subject_totals, key=subject_totals.get)
            # Vind het meest voorkomende beheersingsniveau in dat vak
            subject_mistakes = mistakes_by_subject[worst_subject]
            if subject_mistakes:
                top_mistake_in_subject = max(subject_mistakes, key=lambda x: x['count'])['mistake_type']
                return f"Focus op {worst_subject} waar je vooral {top_mistake_in_subject.lower()}en maakt. Oefen meer op dit gebied!"
            else:
                return f"Focus op {worst_subject}. Oefen meer op dit vak!"
        else:
            return f"Je maakt vooral {top_mistake.lower()}en. Let hier extra op tijdens het maken van opdrachten!"

    # DEFINITIE: COMPLETE DASHBOARD DATA OPHALEN
    # Deze methode haalt alle data op die de template nodig heeft.
    # Dit is de hoofdmethode die door de controller wordt aangeroepen.
    def get_beheersing_niveau_dashboard_data(self, student_id, subject_id=None):
        """
        Haalt alle benodigde data op voor het beheersingsniveau dashboard.

        Args:
            student_id (int): ID van de leerling
            subject_id (int, optional): ID van specifiek vak om te filteren

        Returns:
            dict: Complete dashboard data
        """
        if subject_id:
            mistakes_data = self.filter_by_subject(student_id, subject_id)
            # Voor gefilterde data, maak een dict met één vak
            subject_name_query = "SELECT name FROM subject WHERE id = ?"
            subject_name = execute_query(subject_name_query, (subject_id,))[0]['name']
            mistakes_by_subject = {subject_name: mistakes_data}
        else:
            mistakes_by_subject = self.get_mistakes_by_subject(student_id)

        percentages_data = self.calculate_percentages(mistakes_by_subject)
        recommendation = self.generate_recommendation(student_id)
        common_mistakes = self.get_common_mistake_types(student_id)

        # Haal alleen unieke vakken op die bij deze leerling horen
        subjects = self.get_student_subjects(student_id)

        return BeheersingNiveauData(
            mistakes_by_subject=percentages_data,
            common_mistakes=common_mistakes,
            recommendation=recommendation,
            subjects=subjects,
            selected_subject_id=subject_id,
            current_student_id=student_id
        )


# DEFINITIE: BEHEERSINGSNIVEAU CONTROLLER KLASSE
# Deze controller zorgt voor de renderlogica en het aanroepen van de service.
# De controller geeft alleen data door aan de template en houdt routing logica van de service af.
class BeheersingNiveauController:
    """
    Controller voor beheersingsniveau dashboard.
    """

    def __init__(self):
        self.service = BeheersingNiveauService()

    # DEFINITIE: DASHBOARD PAGINA RENDEREN
    # Deze methode bereidt alle data voor en geeft het door aan de template.
    def render_dashboard(self, student_id=None, subject_id=None):
        """
        Rendert de beheersingsniveau dashboard pagina.
        """
        student_id = get_current_leerling_id(student_id)
        data = self.service.get_beheersing_niveau_dashboard_data(student_id, subject_id)
        return render_template("beheersingsniveau.html", **data.to_dict())


# Maak een controller aan
controller = BeheersingNiveauController()
