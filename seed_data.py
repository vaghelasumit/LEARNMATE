"""
LearnMate - Database Seeding Script
Populates sample courses, study materials, flashcards, quizzes, questions, and test users.
Run with: python seed_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmate_project.settings')
django.setup()

from django.contrib.auth.models import User
from main_app.models import (
    UserProfile, Subject, StudyMaterial, Flashcard,
    Quiz, QuizQuestion, QuizAttempt, QuizAnswer,
    QuizResult, Certificate, Bookmark, Revision
)

def seed_database():
    print("--- Starting LearnMate Database Seeding ---")

    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@learnmate.ac.in', 'first_name': 'Faculty Admin', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        UserProfile.objects.create(user=admin_user, role='admin')
        print("[OK] Created Admin User: admin / admin123")
    else:
        print("[OK] Admin User already exists.")

    # 2. Create Student User
    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={'email': 'student@learnmate.ac.in', 'first_name': 'Sumitkumar Vaghela'}
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        UserProfile.objects.create(user=student_user, role='student')
        print("[OK] Created Student User: student / student123")
    else:
        print("[OK] Student User already exists.")

    # 3. Create Subject 1: Python Programming
    sub_python, _ = Subject.objects.get_or_create(
        subject_name="Python Programming Basics",
        defaults={
            'description': "Comprehensive guide to core Python concepts including variables, data types, control flow, functions, and object-oriented programming.",
            'created_by': admin_user
        }
    )

    # Subject 1 Study Materials
    StudyMaterial.objects.get_or_create(
        subject=sub_python,
        title="Chapter 1: Python Introduction & Variables",
        defaults={
            'material_type': 'notes',
            'drive_link': 'https://drive.google.com/drive/folders/1PythonBasicsCourseNotes_MCA',
            'video_url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',
            'description': """Welcome to Python Basics!
Python is a high-level, interpreted programming language known for its clear syntax and readability.

Key Topics:
1. Variable Declaration:
   In Python, variables are dynamically typed. You do not need to declare types explicitly.
   Example:
   x = 10
   name = 'LearnMate'
   price = 99.50

2. Python Identifiers:
   - Must begin with a letter (a-z, A-Z) or underscore (_).
   - Cannot start with a digit.
   - Case-sensitive: 'var' and 'Var' are different.

3. Comments:
   Use # for single-line comments and triple quotes for multi-line comments.""",
            'created_by': admin_user
        }
    )

    StudyMaterial.objects.get_or_create(
        subject=sub_python,
        title="Chapter 2: Data Types and Collections (List, Tuple, Dict)",
        defaults={
            'material_type': 'pdf',
            'drive_link': 'https://drive.google.com/file/d/1PythonCollectionsGuide_MCA/view',
            'video_url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8',
            'description': """Python Collections Overview:

1. Lists:
   - Ordered, mutable, allows duplicate members.
   - Syntax: my_list = [1, 2, 'three', 4.0]
   - Methods: append(), extend(), pop(), remove()

2. Tuples:
   - Ordered, immutable, allows duplicate members.
   - Syntax: my_tuple = (10, 20, 30)

3. Dictionaries:
   - Key-Value pairs, unordered (Python 3.7+ insertion ordered), mutable.
   - Syntax: student = {'name': 'Sumit', 'course': 'MCA', 'sem': 2}

4. Sets:
   - Unordered, unindexed, no duplicate elements.
   - Syntax: unique_numbers = {1, 2, 3, 3} -> {1, 2, 3}""",
            'created_by': admin_user
        }
    )

    # Subject 1 Flashcards (Matching Sketch 4)
    flashcards_python = [
        ("How do you declare a variable in Python?", "You simply assign a value to a variable name without any type keyword:\nname = 'LearnMate'\nage = 25"),
        ("What is the difference between a List and a Tuple in Python?", "Lists are mutable (can be changed using append/pop) using square brackets [].\nTuples are immutable (cannot be changed after creation) using parentheses ()."),
        ("What is a Python Dictionary?", "A Dictionary is an unordered collection of key:value pairs enclosed in curly braces {}.\nExample: info = {'name': 'John', 'age': 21}"),
        ("What does the 'len()' function do in Python?", "len() returns the number of items in an object like strings, lists, tuples, or dictionaries."),
        ("What is a Lambda function in Python?", "A lambda function is a small anonymous function defined using the 'lambda' keyword.\nSyntax: lambda arguments: expression"),
    ]

    for q, a in flashcards_python:
        Flashcard.objects.get_or_create(
            subject=sub_python,
            question=q,
            defaults={'answer': a, 'created_by': admin_user}
        )

    # Subject 1 Quiz & Questions
    quiz_python, _ = Quiz.objects.get_or_create(
        subject=sub_python,
        quiz_title="Python Fundamentals Assessment",
        defaults={'total_questions': 5, 'passing_marks': 3, 'created_by': admin_user}
    )

    quiz_questions_python = [
        {
            'text': "Which keyword is used to define a function in Python?",
            'a': "func", 'b': "def", 'c': "function", 'd': "define",
            'correct': "B", 'exp': "In Python, the 'def' keyword is used to declare and define a user function."
        },
        {
            'text': "Which of the following data types in Python is immutable?",
            'a': "List", 'b': "Dictionary", 'c': "Tuple", 'd': "Set",
            'correct': "C", 'exp': "Tuples cannot be altered once created, making them immutable."
        },
        {
            'text': "What is the output of print(2 ** 3) in Python?",
            'a': "6", 'b': "8", 'c': "9", 'd': "5",
            'correct': "B", 'exp': "The ** operator computes exponentiation (2^3 = 8)."
        },
        {
            'text': "Which built-in method adds an element to the end of a list?",
            'a': "add()", 'b': "push()", 'c': "append()", 'd': "insert_end()",
            'correct': "C", 'exp': "list.append(x) adds item x to the end of the existing list."
        },
        {
            'text': "How do you start a single-line comment in Python?",
            'a': "// comment", 'b': "/* comment */", 'c': "# comment", 'd': "-- comment",
            'correct': "C", 'exp': "Python uses the hash symbol (#) for single-line comments."
        },
    ]

    for q_data in quiz_questions_python:
        QuizQuestion.objects.get_or_create(
            quiz=quiz_python,
            question_text=q_data['text'],
            defaults={
                'option_a': q_data['a'],
                'option_b': q_data['b'],
                'option_c': q_data['c'],
                'option_d': q_data['d'],
                'correct_answer': q_data['correct'],
                'explanation': q_data['exp'],
            }
        )
    quiz_python.total_questions = quiz_python.questions.count()
    quiz_python.save()

    # 4. Create Subject 2: PHP & Web Development
    sub_php, _ = Subject.objects.get_or_create(
        subject_name="PHP & Web Development",
        defaults={
            'description': "Learn server-side web scripting with PHP, form processing, session management, and MySQL database integration.",
            'created_by': admin_user
        }
    )

    StudyMaterial.objects.get_or_create(
        subject=sub_php,
        title="Chapter 1: PHP Basics & Syntax",
        defaults={
            'material_type': 'notes',
            'drive_link': 'https://drive.google.com/drive/folders/1PHPLectureNotes_MCA',
            'video_url': 'https://www.youtube.com/watch?v=2eebptXfEvw',
            'description': """PHP (Hypertext Preprocessor) is an open source server-side scripting language widely used for web development.

1. PHP Tags:
   PHP code is enclosed within <?php and ?>.

2. Variables:
   Variables start with the $ sign.
   Example: $txt = "Hello World!"; $x = 5;

3. Output:
   echo and print statements are used to output data to the screen.""",
            'created_by': admin_user
        }
    )

    flashcards_php = [
        ("What does PHP stand for?", "PHP originally stood for Personal Home Page, but now stands for Hypertext Preprocessor."),
        ("How are variables declared in PHP?", "All variables in PHP start with a dollar sign ($), for example: $student_name = 'Sumit';"),
        ("What is the difference between $_GET and $_POST?", "$_GET sends data visible in the URL query string (limit on size).\n$_POST sends data invisibly in the HTTP request body (secure for passwords and large data)."),
    ]

    for q, a in flashcards_php:
        Flashcard.objects.get_or_create(
            subject=sub_php,
            question=q,
            defaults={'answer': a, 'created_by': admin_user}
        )

    quiz_php, _ = Quiz.objects.get_or_create(
        subject=sub_php,
        quiz_title="PHP Fundamentals Quiz",
        defaults={'total_questions': 3, 'passing_marks': 2, 'created_by': admin_user}
    )

    quiz_questions_php = [
        {
            'text': "Which superglobal variable is used to collect data sent via HTTP POST method?",
            'a': "$_GET", 'b': "$_POST", 'c': "$_REQUEST_POST", 'd': "$_DATA",
            'correct': "B", 'exp': "$_POST is an associative array containing form variables submitted with method='post'."
        },
        {
            'text': "Which function is used to start a new or resume an existing session in PHP?",
            'a': "session_begin()", 'b': "session_start()", 'c': "start_session()", 'd': "init_session()",
            'correct': "B", 'exp': "session_start() creates a session or resumes the current one based on a session identifier."
        },
        {
            'text': "Which symbol is used to concatenate strings in PHP?",
            'a': "+", 'b': "&", 'c': ".", 'd': "*",
            'correct': "C", 'exp': "The dot (.) operator is used for string concatenation in PHP."
        },
    ]

    for q_data in quiz_questions_php:
        QuizQuestion.objects.get_or_create(
            quiz=quiz_php,
            question_text=q_data['text'],
            defaults={
                'option_a': q_data['a'],
                'option_b': q_data['b'],
                'option_c': q_data['c'],
                'option_d': q_data['d'],
                'correct_answer': q_data['correct'],
                'explanation': q_data['exp'],
            }
        )
    quiz_php.total_questions = quiz_php.questions.count()
    quiz_php.save()

    # 5. Create Subject 3: Database Management Systems
    sub_dbms, _ = Subject.objects.get_or_create(
        subject_name="Database Management Systems (DBMS)",
        defaults={
            'description': "Concepts of relational database modeling, normalization (1NF, 2NF, 3NF), SQL querying, and transaction management.",
            'created_by': admin_user
        }
    )

    StudyMaterial.objects.get_or_create(
        subject=sub_dbms,
        title="Chapter 1: Relational Database Model & SQL",
        defaults={
            'material_type': 'notes',
            'description': """A Database Management System (DBMS) is software designed to store, retrieve, define, and manage data in a database.

1. Primary Key:
   A minimal set of attributes that uniquely identifies each tuple in a relation. Cannot be NULL.

2. Foreign Key:
   A field in one table that uniquely identifies a row in another table, enforcing referential integrity.

3. ACID Properties:
   - Atomicity (All or nothing)
   - Consistency (Valid database state)
   - Isolation (Concurrent transactions do not affect each other)
   - Durability (Committed changes survive system crashes)""",
            'created_by': admin_user
        }
    )

    # 6. Simulate a sample test attempt for 'student' so that Revision & Certificate are populated
    attempt, created_attempt = QuizAttempt.objects.get_or_create(
        student=student_user,
        quiz=quiz_python,
        defaults={'status': 'Completed'}
    )

    if created_attempt:
        questions = quiz_python.questions.all()
        # Answer Q1, Q2, Q3, Q4 correctly, and Q5 incorrectly to demo Mistake Revision Hub!
        score = 0
        for i, q in enumerate(questions):
            if i == 4:
                # Wrong answer
                ans = QuizAnswer.objects.create(attempt=attempt, question=q, selected_answer='A', is_correct=False)
                Revision.objects.create(student=student_user, question=q, revision_status='Pending', notes='Need to remember Python uses # for comments')
            else:
                ans = QuizAnswer.objects.create(attempt=attempt, question=q, selected_answer=q.correct_answer, is_correct=True)
                score += 1

        result = QuizResult.objects.create(
            attempt=attempt,
            student=student_user,
            quiz=quiz_python,
            score=score,
            total_marks=len(questions),
            percentage=round((score / len(questions)) * 100, 2),
            result_status='Pass'
        )

        cert_no = Certificate.generate_certificate_number()
        Certificate.objects.create(
            student=student_user,
            subject=sub_python,
            result=result,
            certificate_no=cert_no
        )
        print("[OK] Sample student quiz attempt, certificate, and revision items populated.")

    # 14. Create Sample Bookmarks for Demo Student (Across all content types)
    # Subject Bookmark
    Bookmark.objects.get_or_create(
        student=student_user,
        subject=sub_python,
        material=None,
        flashcard=None,
        question=None
    )
    # Material Bookmark
    first_mat = StudyMaterial.objects.filter(subject=sub_python).first()
    if first_mat:
        Bookmark.objects.get_or_create(
            student=student_user,
            material=first_mat,
            defaults={'subject': first_mat.subject}
        )
    # Flashcard Bookmark
    first_card = Flashcard.objects.filter(subject=sub_python).first()
    if first_card:
        Bookmark.objects.get_or_create(
            student=student_user,
            flashcard=first_card,
            defaults={'subject': first_card.subject}
        )
    # Question Bookmark
    first_q = QuizQuestion.objects.filter(quiz=quiz_python).first()
    if first_q:
        Bookmark.objects.get_or_create(
            student=student_user,
            question=first_q,
            defaults={'subject': sub_python}
        )
    print("[OK] Sample student bookmarks created across all content types.")

    print("--- LearnMate Database Seeding Completed Successfully! ---")

if __name__ == '__main__':
    seed_database()
