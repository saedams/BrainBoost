/* * Seed Data for Brain Boost
 * Purpose: Fills the 'exercises' and 'result' tables with initial data from the wireframe.
 */

-- Insert exercises for the "Recommended" section
INSERT INTO exercises (title, description, duration, question_count, color_code, status)
VALUES 
('Vermijd Haastige Conclusies', 'Leer alle antwoordopties grondig te lezen voordat je kiest.', 15, 12, '#D38D8D', 'recommended'),
('Sleutelwoorden Herkennen', 'Oefen met het markeren van belangrijke woorden zoals "NIET" en "ALLEEN".', 10, 8, '#8D8DB7', 'recommended'),
('Tijdsplanning Verbeteren', 'Oefen met tijdsbeheer tijdens toetsen en lastige vragen.', 20, 15, '#74A9CF', 'recommended');

-- Insert exercises for the "Soon" (Binnenkort) section
INSERT INTO exercises (title, description, status)
VALUES 
('Nauwkeurigheid Training', 'Coming soon: Focus op details.', 'upcoming'),
('Spelling & Grammatica', 'Coming soon: Verbeter je taalvaardigheid.', 'upcoming');

-- Insert some initial results for the sidebar
-- Note: exercise_id 1 refers to 'Vermijd Haastige Conclusies'
INSERT INTO result (exercise_id, score, completion_time)
VALUES 
(1, 8.5, '2026-03-28 14:30:00'),
(2, 7.2, '2026-03-29 09:15:00');

-- Seed data voor nieuwe tabellen voor Beheersingsniveau

-- Insert a sample student
INSERT INTO leerling (naam, email, wachtwoord_hash) VALUES 
('Elena de Vries', 'elena.devries@example.com', 'hashedpassword');

-- Insert subjects (vakken)
INSERT INTO subject (name) VALUES 
('Wiskunde A'),
('Wiskunde B'),
('Wiskunde C'),
('Natuurkunde');

-- Insert sample questions
INSERT INTO question (subject_id, question_text, solution_text, difficulty, max_score) VALUES 
(1, 'Bereken 2 + 2', 'Het antwoord is 4', 'makkelijk', 10),
(1, 'Bereken de afgeleide van x^2', 'De afgeleide is 2x', 'gemiddeld', 15),
(2, 'Los de vergelijking x + 3 = 7 op', 'x = 4', 'makkelijk', 10),
(3, 'Bereken de integraal van 2x dx', 'Het antwoord is x^2 + C', 'moeilijk', 20),
(4, 'Wat is de snelheid van licht?', '299792458 m/s', 'gemiddeld', 10),
(4, 'Wat zegt de helling van deze grafiek over snelheid?', 'Een stijgende helling betekent een toenemende snelheid', 'gemiddeld', 10),
(2, 'Hoeveel is 20% van 50?', '10', 'makkelijk', 10),
(1, 'Rond 3.14159 af op twee decimalen.', '3.14', 'makkelijk', 10),
(1, 'Bereken 12 / 4', '3', 'makkelijk', 10);

-- Insert sample student answers
INSERT INTO student_answer (student_id, question_id, student_answer, score, max_score) VALUES 
(1, 1, '4', 10, 10),
(1, 2, 'x', 5, 15),          -- Formulefout
(1, 3, '4', 10, 10),
(1, 4, 'x^2', 10, 20),       -- Stappen ontbreken
(1, 5, '300000000', 8, 10),  -- Eenhedenfout
(1, 6, 'De helling is constant', 6, 10), -- Grafiekfout
(1, 7, '15', 7, 10),         -- Leesfout
(1, 8, '3.1', 7, 10),        -- Afrondingsfout
(1, 9, '2.5', 6, 10);        -- Berekeningsfout

-- Insert mistake analyses
INSERT INTO mistake_analysis (student_answer_id, mistake_type, feedback_text) VALUES 
(2, 'Formulefout', 'Je hebt de verkeerde formule gebruikt voor de afgeleide.'),
(4, 'Stappen ontbreken', 'Je hebt de tussenstap met de integratieconstante overgeslagen.'),
(5, 'Eenhedenfout', 'De snelheid van licht moet in m/s staan en niet worden afgerond.'),
(6, 'Grafiekfout', 'Je hebt de schaal en de helling van de grafiek niet goed geïnterpreteerd.'),
(7, 'Leesfout', 'Je hebt de vraag niet goed gelezen; let op wat er precies wordt gevraagd.'),
(8, 'Afrondingsfout', 'Je hebt niet correct afgerond op twee decimalen.'),
(9, 'Berekeningsfout', 'Je berekening van de deling is niet correct.');

