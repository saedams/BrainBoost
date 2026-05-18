# Migration script voor nieuwe foutenanalyse tabellen

from app.db import execute_query

def migrate_foutenanalyse():
    """Voeg nieuwe tabellen toe voor foutenanalyse."""

    # Subject tabel
    subject_table = """
    CREATE TABLE IF NOT EXISTS `subject` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `name` VARCHAR(100) NOT NULL,
        PRIMARY KEY (`id`)
    );
    """

    # Question tabel
    question_table = """
    CREATE TABLE IF NOT EXISTS `question` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `subject_id` INT NOT NULL,
        `question_text` TEXT NOT NULL,
        `solution_text` TEXT,
        `difficulty` VARCHAR(50),
        `max_score` INT NOT NULL,
        PRIMARY KEY (`id`),
        FOREIGN KEY (`subject_id`) REFERENCES `subject`(`id`)
    );
    """

    # StudentAnswer tabel
    student_answer_table = """
    CREATE TABLE IF NOT EXISTS `student_answer` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `student_id` INT NOT NULL,
        `question_id` INT NOT NULL,
        `student_answer` TEXT,
        `score` INT NOT NULL,
        `max_score` INT NOT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        FOREIGN KEY (`student_id`) REFERENCES `leerling`(`id`),
        FOREIGN KEY (`question_id`) REFERENCES `question`(`id`)
    );
    """

    # MistakeAnalysis tabel
    mistake_analysis_table = """
    CREATE TABLE IF NOT EXISTS `mistake_analysis` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `student_answer_id` INT NOT NULL,
        `mistake_type` VARCHAR(100) NOT NULL,
        `feedback_text` TEXT,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        FOREIGN KEY (`student_answer_id`) REFERENCES `student_answer`(`id`)
    );
    """

    tables = [subject_table, question_table, student_answer_table, mistake_analysis_table]

    for table_sql in tables:
        print(f"Creating table...")
        result = execute_query(table_sql)
        print(f"Result: {result}")

def seed_demo_records():
    """
    Voeg demo data toe zodat elke leerling alleen zijn/haar vakken ziet.
    
    Structuur:
    - Leerling 1: Natuurkunde, Wiskunde A
    - Leerling 2: Natuurkunde, Wiskunde B
    - Leerling 3: Natuurkunde, Wiskunde C
    """

    def cleanup_table(table_name):
        try:
            execute_query(f"DELETE FROM {table_name};")
            execute_query(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
        except Exception:
            pass

    # STAP 0: Wis bestaande data (in omgekeerde volgorde van foreign keys)
    cleanup_table("mistake_analysis")
    cleanup_table("student_answer")
    cleanup_table("question")
    cleanup_table("subject")
    cleanup_table("leerling")

    # STAP 1: Voeg leerlingen toe en sla IDs op
    students = [
        {"name": "Anna", "email": "anna@example.com", "password": "pass"},
        {"name": "Bert", "email": "bert@example.com", "password": "pass"},
        {"name": "Carla", "email": "carla@example.com", "password": "pass"}
    ]
    student_ids = {}
    for student in students:
        execute_query(
            "INSERT INTO leerling (naam, email, wachtwoord_hash) VALUES (?, ?, ?);",
            (student["name"], student["email"], student["password"])
        )
        student_id = execute_query(
            "SELECT id FROM leerling WHERE naam = ? ORDER BY id DESC LIMIT 1;",
            (student["name"],)
        )[0]["id"]
        student_ids[student["name"]] = student_id

    # STAP 2: Voeg vakken toe en sla subject IDs op
    subjects = ["Natuurkunde", "Wiskunde A", "Wiskunde B", "Wiskunde C"]
    subject_ids = {}
    for name in subjects:
        execute_query("INSERT INTO subject (name) VALUES (?);", (name,))
        subject_id = execute_query(
            "SELECT id FROM subject WHERE name = ? ORDER BY id DESC LIMIT 1;",
            (name,)
        )[0]["id"]
        subject_ids[name] = subject_id

    # STAP 3: Voeg vragen toe en sla question IDs op
    questions = [
        {"subject": "Natuurkunde", "text": "Wat is de snelheid na 5 seconden?", "solution": "25 m/s", "difficulty": "gemiddeld"},
        {"subject": "Natuurkunde", "text": "Bereken de kracht F = m*a", "solution": "F = 100 N", "difficulty": "gemiddeld"},
        {"subject": "Natuurkunde", "text": "Bepaal de energie", "solution": "E = 500 J", "difficulty": "moeilijk"},
        {"subject": "Wiskunde A", "text": "Los op: 2x + 3 = 7", "solution": "x = 2", "difficulty": "makkelijk"},
        {"subject": "Wiskunde A", "text": "Bepaal de afgeleide van x²", "solution": "f'(x) = 2x", "difficulty": "gemiddeld"},
        {"subject": "Wiskunde A", "text": "Integraal van 3x²", "solution": "∫ = x³ + C", "difficulty": "moeilijk"},
        {"subject": "Wiskunde B", "text": "Goniometrie: sin(30°)", "solution": "0.5", "difficulty": "makkelijk"},
        {"subject": "Wiskunde B", "text": "Los op: cos(x) = 0.5", "solution": "x = 60°", "difficulty": "gemiddeld"},
        {"subject": "Wiskunde B", "text": "Bepaal tan(45°) + sin(45°)", "solution": "1 + √2/2", "difficulty": "moeilijk"},
        {"subject": "Wiskunde C", "text": "Statistiek: Bereken het gemiddelde", "solution": "5.5", "difficulty": "makkelijk"},
        {"subject": "Wiskunde C", "text": "Bepaal de standaarddeviatie", "solution": "2.1", "difficulty": "gemiddeld"},
        {"subject": "Wiskunde C", "text": "Kans: P(A en B)", "solution": "0.24", "difficulty": "moeilijk"}
    ]
    question_ids = {}
    for question in questions:
        execute_query(
            "INSERT INTO question (subject_id, question_text, solution_text, difficulty, max_score) VALUES (?, ?, ?, ?, 10);",
            (subject_ids[question["subject"]], question["text"], question["solution"], question["difficulty"])
        )
        question_id = execute_query(
            "SELECT id FROM question WHERE question_text = ? ORDER BY id DESC LIMIT 1;",
            (question["text"],)
        )[0]["id"]
        question_ids[question["text"]] = question_id

    # STAP 4: Voeg antwoorden toe per leerling
    answers = [
        # Leerling 1 Anna: Natuurkunde + Wiskunde A
        {"student": "Anna", "question": "Wat is de snelheid na 5 seconden?", "answer": "25", "score": 10},
        {"student": "Anna", "question": "Bereken de kracht F = m*a", "answer": "95", "score": 8},
        {"student": "Anna", "question": "Bepaal de energie", "answer": "480", "score": 7},
        {"student": "Anna", "question": "Los op: 2x + 3 = 7", "answer": "x = 2", "score": 10},
        {"student": "Anna", "question": "Bepaal de afgeleide van x²", "answer": "2x", "score": 9},
        {"student": "Anna", "question": "Integraal van 3x²", "answer": "x^3", "score": 7},
        # Leerling 2 Bert: Natuurkunde + Wiskunde B
        {"student": "Bert", "question": "Wat is de snelheid na 5 seconden?", "answer": "20", "score": 8},
        {"student": "Bert", "question": "Bereken de kracht F = m*a", "answer": "100", "score": 10},
        {"student": "Bert", "question": "Bepaal de energie", "answer": "500", "score": 9},
        {"student": "Bert", "question": "Goniometrie: sin(30°)", "answer": "0.5", "score": 10},
        {"student": "Bert", "question": "Los op: cos(x) = 0.5", "answer": "x = 60°", "score": 7},
        {"student": "Bert", "question": "Bepaal tan(45°) + sin(45°)", "answer": "1.7", "score": 8},
        # Leerling 3 Carla: Natuurkunde + Wiskunde C
        {"student": "Carla", "question": "Wat is de snelheid na 5 seconden?", "answer": "24", "score": 9},
        {"student": "Carla", "question": "Bereken de kracht F = m*a", "answer": "99", "score": 9},
        {"student": "Carla", "question": "Bepaal de energie", "answer": "510", "score": 10},
        {"student": "Carla", "question": "Statistiek: Bereken het gemiddelde", "answer": "5.4", "score": 9},
        {"student": "Carla", "question": "Bepaal de standaarddeviatie", "answer": "2.2", "score": 8},
        {"student": "Carla", "question": "Kans: P(A en B)", "answer": "0.25", "score": 10}
    ]

    answer_ids = {}
    for answer in answers:
        execute_query(
            "INSERT INTO student_answer (student_id, question_id, student_answer, score, max_score) VALUES (?, ?, ?, ?, 10);",
            (student_ids[answer["student"]], question_ids[answer["question"]], answer["answer"], answer["score"])
        )
        student_answer_id = execute_query(
            "SELECT id FROM student_answer WHERE student_id = ? AND question_id = ? ORDER BY id DESC LIMIT 1;",
            (student_ids[answer["student"]], question_ids[answer["question"]])
        )[0]["id"]
        answer_ids[(answer["student"], answer["question"])] = student_answer_id

    # STAP 5: Voeg foutanalyse data toe
    mistakes = [
        {"student": "Anna", "question": "Bepaal de energie", "type": "Berekeningsfout", "feedback": "Let op je berekening"},
        {"student": "Anna", "question": "Integraal van 3x²", "type": "Formulefout", "feedback": "Onjuiste integratieregel"},
        {"student": "Bert", "question": "Los op: cos(x) = 0.5", "type": "Afrondingsfout", "feedback": "Verkeerd afgerond"},
        {"student": "Bert", "question": "Bepaal tan(45°) + sin(45°)", "type": "Formulefout", "feedback": "Verkeerde formule gebruikt"},
        {"student": "Carla", "question": "Statistiek: Bereken het gemiddelde", "type": "Leesfout", "feedback": "Vraag niet goed gelezen"}
    ]

    for mistake in mistakes:
        execute_query(
            "INSERT INTO mistake_analysis (student_answer_id, mistake_type, feedback_text) VALUES (?, ?, ?);",
            (answer_ids[(mistake["student"], mistake["question"])], mistake["type"], mistake["feedback"])
        )

    print("Demo import completed!")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        migrate_foutenanalyse()
        seed_demo_records()
        print("Demo import completed!")