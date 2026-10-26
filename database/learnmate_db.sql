CREATE DATABASE IF NOT EXISTS learnmate_db;
USE learnmate_db;


-- 1. AUTH USER
DROP TABLE IF EXISTS auth_user;

CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6),
    is_superuser TINYINT(1) DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    date_joined DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6)
);


-- 2. USER PROFILE
DROP TABLE IF EXISTS user_profile;

CREATE TABLE user_profile (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(20) DEFAULT 'student',
    phone VARCHAR(15),
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    user_id INT NOT NULL UNIQUE,

    FOREIGN KEY (user_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 3. SUBJECT
DROP TABLE IF EXISTS subject;

CREATE TABLE subject (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    description LONGTEXT NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    created_by_id INT NOT NULL,

    FOREIGN KEY (created_by_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 4. STUDY MATERIAL
DROP TABLE IF EXISTS study_material;

CREATE TABLE study_material (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    material_type VARCHAR(20) DEFAULT 'notes',
    file_path VARCHAR(255),
    drive_link VARCHAR(500),
    video_url VARCHAR(500),
    description LONGTEXT NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    created_by_id INT NOT NULL,
    subject_id INT NOT NULL,

    FOREIGN KEY (subject_id)
    REFERENCES subject(subject_id)
    ON DELETE CASCADE,

    FOREIGN KEY (created_by_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 5. FLASHCARD
DROP TABLE IF EXISTS flashcard;

CREATE TABLE flashcard (
    flashcard_id INT AUTO_INCREMENT PRIMARY KEY,
    question LONGTEXT NOT NULL,
    answer LONGTEXT NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    created_by_id INT NOT NULL,
    subject_id INT NOT NULL,

    FOREIGN KEY (subject_id)
    REFERENCES subject(subject_id)
    ON DELETE CASCADE,

    FOREIGN KEY (created_by_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 6. QUIZ
DROP TABLE IF EXISTS quiz;

CREATE TABLE quiz (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_title VARCHAR(150) NOT NULL,
    total_questions INT DEFAULT 5,
    passing_marks INT DEFAULT 3,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    created_by_id INT NOT NULL,
    subject_id INT NOT NULL,

    FOREIGN KEY (subject_id)
    REFERENCES subject(subject_id)
    ON DELETE CASCADE,

    FOREIGN KEY (created_by_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 7. QUIZ QUESTION
DROP TABLE IF EXISTS quiz_question;

CREATE TABLE quiz_question (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text LONGTEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer VARCHAR(1) NOT NULL,
    explanation LONGTEXT,
    quiz_id INT NOT NULL,

    FOREIGN KEY (quiz_id)
    REFERENCES quiz(quiz_id)
    ON DELETE CASCADE
);


-- 8. QUIZ ATTEMPT
DROP TABLE IF EXISTS quiz_attempt;

CREATE TABLE quiz_attempt (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    attempt_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    status VARCHAR(20) DEFAULT 'Completed',
    quiz_id INT NOT NULL,
    student_id INT NOT NULL,

    FOREIGN KEY (quiz_id)
    REFERENCES quiz(quiz_id)
    ON DELETE CASCADE,

    FOREIGN KEY (student_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 9. QUIZ ANSWER
DROP TABLE IF EXISTS quiz_answer;

CREATE TABLE quiz_answer (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    selected_answer VARCHAR(10) NOT NULL,
    is_correct TINYINT(1) DEFAULT 0,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,

    FOREIGN KEY (attempt_id)
    REFERENCES quiz_attempt(attempt_id)
    ON DELETE CASCADE,

    FOREIGN KEY (question_id)
    REFERENCES quiz_question(question_id)
    ON DELETE CASCADE
);


-- 10. QUIZ RESULT
DROP TABLE IF EXISTS quiz_result;

CREATE TABLE quiz_result (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    score INT NOT NULL,
    total_marks INT NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    result_status VARCHAR(20) DEFAULT 'Pass',
    result_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    attempt_id INT NOT NULL UNIQUE,
    quiz_id INT NOT NULL,
    student_id INT NOT NULL,

    FOREIGN KEY (attempt_id)
    REFERENCES quiz_attempt(attempt_id)
    ON DELETE CASCADE,

    FOREIGN KEY (quiz_id)
    REFERENCES quiz(quiz_id)
    ON DELETE CASCADE,

    FOREIGN KEY (student_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);


-- 11. CERTIFICATE
DROP TABLE IF EXISTS certificate;

CREATE TABLE certificate (
    certificate_id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_no VARCHAR(50) NOT NULL UNIQUE,
    issue_date DATE NOT NULL,
    certificate_path VARCHAR(255),
    result_id INT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,

    FOREIGN KEY (result_id)
    REFERENCES quiz_result(result_id)
    ON DELETE SET NULL,

    FOREIGN KEY (student_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE,

    FOREIGN KEY (subject_id)
    REFERENCES subject(subject_id)
    ON DELETE CASCADE
);


-- 12. BOOKMARK
DROP TABLE IF EXISTS bookmark;

CREATE TABLE bookmark (
    bookmark_id INT AUTO_INCREMENT PRIMARY KEY,
    bookmarked_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    status VARCHAR(20) DEFAULT 'Active',
    flashcard_id INT,
    material_id INT,
    question_id INT,
    student_id INT NOT NULL,
    subject_id INT,

    FOREIGN KEY (flashcard_id)
    REFERENCES flashcard(flashcard_id)
    ON DELETE CASCADE,

    FOREIGN KEY (material_id)
    REFERENCES study_material(material_id)
    ON DELETE CASCADE,

    FOREIGN KEY (question_id)
    REFERENCES quiz_question(question_id)
    ON DELETE CASCADE,

    FOREIGN KEY (student_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE,

    FOREIGN KEY (subject_id)
    REFERENCES subject(subject_id)
    ON DELETE CASCADE
);


-- 13. REVISION
DROP TABLE IF EXISTS revision;

CREATE TABLE revision (
    revision_id INT AUTO_INCREMENT PRIMARY KEY,
    revision_date DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    revision_status VARCHAR(20) DEFAULT 'Pending',
    notes LONGTEXT,
    question_id INT NOT NULL,
    student_id INT NOT NULL,

    FOREIGN KEY (question_id)
    REFERENCES quiz_question(question_id)
    ON DELETE CASCADE,

    FOREIGN KEY (student_id)
    REFERENCES auth_user(id)
    ON DELETE CASCADE
);