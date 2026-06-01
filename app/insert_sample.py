#!/usr/bin/env python3
"""Insert sample data into the fout table."""

from app.db import execute_query

def insert_sample_data():
    """Insert some sample data."""
    inserts = [
        "INSERT INTO leerling (naam, email, wachtwoord_hash) VALUES ('Jan Jansen', 'jan.jansen@test.nl', '1234');",
        "INSERT INTO leerling (naam, email, wachtwoord_hash) VALUES ('Piet Peters', 'piet.peters@test.nl', '1234');",
        "INSERT INTO resultaat (leerling_id, onderwerp, score) VALUES (1, 'Rekenen', 75);",
        "INSERT INTO resultaat (leerling_id, onderwerp, score) VALUES (1, 'Taal', 82);",
        "INSERT INTO resultaat (leerling_id, onderwerp, score) VALUES (1, 'Biologie', 68);",
        "INSERT INTO fout (leerling_id, categorie, subcategorie, aantal) VALUES (1, 'Rekenen', 'Optellen', 5);",
        "INSERT INTO fout (leerling_id, categorie, subcategorie, aantal) VALUES (1, 'Rekenen', 'Aftrekken', 3);",
        "INSERT INTO fout (leerling_id, categorie, subcategorie, aantal) VALUES (1, 'Taal', 'Spelling', 7);",
        "INSERT INTO fout (leerling_id, categorie, subcategorie, aantal) VALUES (1, 'Taal', 'Woordenschat', 2);",
        "INSERT INTO fout (leerling_id, categorie, subcategorie, aantal) VALUES (1, 'Biologie', 'Cellen', 4);",
    ]

    for insert in inserts:
        print(f"Executing: {insert}")
        result = execute_query(insert)
        print(f"Result: {result}")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        insert_sample_data()