from app import create_app
from app.db import execute_query

app = create_app()
with app.app_context():
    leerlingen = execute_query("SELECT id, naam FROM leerling ORDER BY id")
    print('LEERLINGEN:')
    for l in leerlingen:
        print(f" - {l.get('id')} : {l.get('naam')}")

    print('\nVAKKEN PER LEERLING:')
    for l in leerlingen:
        sid = l.get('id')
        rows = execute_query(
            "SELECT DISTINCT s.id, s.name FROM subject s JOIN question q ON s.id=q.subject_id JOIN student_answer sa ON q.id=sa.question_id WHERE sa.student_id = ? ORDER BY s.name",
            (sid,)
        )
        names = [r.get('name') for r in rows]
        print(f" - {l.get('naam')} ({sid}): {names}")

    print('\nSTUDENT_ANSWERS COUNT:')
    counts = execute_query('SELECT student_id, COUNT(*) as cnt FROM student_answer GROUP BY student_id')
    for c in counts:
        print(f" - student {c.get('student_id')}: {c.get('cnt')}")
