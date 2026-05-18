CREATE TABLE Event (
    eventId INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    eventDate DATETIME,
    creationDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


/** Exercise table to store exercise details such as title, description, duration, question count, color code, and status.
 * The status field can be used to indicate whether an exercise is recommended or not.
 */

CREATE TABLE exercises (
    -- Unique ID number for each exercise, counts up automatically: 1,2,3 etc.
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- The name of the exercise.
    title TEXT NOT NULL,
    -- A short explanation of what the exercise is about.
    description TEXT,
    -- How long the exercise takes.
    duration INTEGER,
    -- How many questions the exercise has.
    question_count INTEGER,
    -- A color to visually represent the exercise.
    color_code TEXT,
    -- Whether the exercise is recommended or not, default is 'recommended'.
    status TEXT DEFAULT 'recommended'
);

/** Result table to store the results of exercises, including the score and completion time.
 * It has a foreign key relationship with the exercises table to link each result to a specific exercise.
 */

CREATE TABLE `leerling`(
    `id` INT NOT NULL AUTO_INCREMENT,
    `naam` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `wachtwoord_hash` VARCHAR(255) NOT NULL,
    PRIMARY KEY(`id`)
);


CREATE TABLE `resultaat`(
    `id` INT NOT NULL AUTO_INCREMENT,
    `leerling_id` INT NOT NULL,
    `onderwerp` VARCHAR(100) NOT NULL,
    `score` INT NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY (`leerling_id`) REFERENCES `leerling`(`id`)
);

CREATE TABLE `vak`(
    `id` INT NOT NULL AUTO_INCREMENT,
    `naam` VARCHAR(100) NOT NULL,
    PRIMARY KEY(`id`)
);



--  VAARDIGHEID
CREATE TABLE `vaardigheid` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `leerling_id` INT NOT NULL,
    `naam` VARCHAR(100),
    `sterren` INT,
    `trend` VARCHAR(50),
    `bijgewerkt_op` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`leerling_id`) REFERENCES `leerling`(`id`)
) ENGINE=InnoDB;

-- FOUT
CREATE TABLE `fout` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `leerling_id` INT NOT NULL,
    `categorie` VARCHAR(100) NOT NULL,
    `subcategorie` VARCHAR(100) NOT NULL,
    `aantal` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`leerling_id`) REFERENCES `leerling`(`id`)
);

-- Nieuwe tabellen voor Foutenanalyse volgens OOP

-- Subject tabel voor vakken
CREATE TABLE `subject` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`id`)
);

-- Question tabel voor vragen
CREATE TABLE `question` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `subject_id` INT NOT NULL,
    `question_text` TEXT NOT NULL,
    `solution_text` TEXT,
    `difficulty` VARCHAR(50),
    `max_score` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`subject_id`) REFERENCES `subject`(`id`)
);

-- StudentAnswer tabel voor antwoorden van leerlingen
CREATE TABLE `student_answer` (
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

-- MistakeAnalysis tabel voor foutanalyse
CREATE TABLE `mistake_analysis` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `student_answer_id` INT NOT NULL,
    `mistake_type` VARCHAR(100) NOT NULL,
    `feedback_text` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`student_answer_id`) REFERENCES `student_answer`(`id`)
);



