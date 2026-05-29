from flask import render_template, redirect, url_for, request, flash
from app.db import execute_query
from app.contact import bp

class FAQ:
    def __init__(self, id, question, answer):
        self.id = id
        self.question = question
        self.answer = answer


class ContactRoutes:
    """Object-georiënteerde router voor contactpagina's."""

    def __init__(self, blueprint):
        self.bp = blueprint
        self.register_routes()

    def register_routes(self):
        self.bp.add_url_rule('/contact', endpoint='contact', view_func=self.contact, methods=['GET', 'POST'])
        self.bp.add_url_rule('/support', endpoint='support', view_func=self.support)

    def contact(self):
        """Contact & Support pagina met veelgestelde vragen en hulp informatie."""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

            if not name or not email or not message:
                flash('Alle velden zijn verplicht.', 'danger')
                return redirect(url_for('contact.contact'))

            flash(f'Bedankt {name}! Je bericht is verzonden. We nemen zo snel mogelijk contact met je op.', 'success')
            return redirect(url_for('contact.contact'))

        try:
            faqs_raw = execute_query("SELECT id, question, answer FROM faq")
            faq_objects = [FAQ(f['id'], f['question'], f['answer']) for f in faqs_raw]
        except Exception as e:
            print(f"Database query failed: {e}")
            faq_objects = [
                FAQ(1, "Wat zijn de openingstijden?", "Wij zijn elke werkdag bereikbaar van 09:00 tot 17:00."),
                FAQ(2, "Hoe kan ik jullie bereiken?", "Je kunt ons mailen of het contactformulier hieronder invullen.")
            ]

        return render_template('contact/support/contact.html', faq_list=faq_objects)

    def support(self):
        """Support pagina - doorverwijzen naar contact pagina."""
        return redirect(url_for('contact.contact'))


ContactRoutes(bp)