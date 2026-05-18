"""
Hulpmiddelen voor het bepalen van de huidige leerling (demo fallback).

Alle pagina's die leerlingdata tonen moeten deze helper gebruiken om
consistentie in fallback-logic te garanderen.

Regels:
- Als `url_leerling_id` is opgegeven, gebruik die.
- Anders: als query parameter `leerling_id` aanwezig is, gebruik die.
- Anders: als `session['leerling_id']` aanwezig is, gebruik die.
- Anders: gebruik demo fallback `DEMO_LEERLING_ID`.

NB: Functie gebruikt `flask.request` en `flask.session` en moet daarom
in een request context aangeroepen worden.
"""
from flask import request, session

DEMO_LEERLING_ID = 16


def get_current_leerling_id(url_leerling_id=None):
    """
    Bepaal de huidige leerling ID volgens de globale fallback regels.

    Args:
        url_leerling_id (int|None): optionele ID vanuit de route (pad-parameter)

    Returns:
        int: de gekozen leerling_id
    """
    # 1) Route/path parameter wint
    if url_leerling_id is not None:
        try:
            return int(url_leerling_id)
        except (TypeError, ValueError):
            pass

    # 2) Query parameter ?leerling_id=...
    q = request.args.get("leerling_id", type=int)
    if q is not None:
        return q

    # 3) Session waarde
    sess_val = session.get("leerling_id")
    if isinstance(sess_val, int):
        return sess_val

    # 4) Fallback demo leerling
    return DEMO_LEERLING_ID
