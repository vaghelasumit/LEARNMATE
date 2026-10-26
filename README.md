<<<<<<< HEAD
# LearnMate - Centralized Learning & Revision Platform

**An MCA Academic Project Submitted to Ganpat University (A M Patel Institute of Computer Studies)**

---

## 📌 Project Overview
**LearnMate** is a web-based educational platform developed to provide organized, course-wise study materials, interactive digital flashcards, practice quizzes with real-time scoring, an automated **Mistake-Based Revision Hub**, and verifiable course completion certificates.

### 👥 Project Developers:
- **Vaghela Sumitkumar hirabhai** (Enrollment No: `25034211082`)
- **Bahelim Uzer** (Enrollment No: `25034211005`)
- **Department**: Master of Computer Applications (MCA)
- **Institution**: A M Patel Institute of Computer Studies (AMPICS), Ganpat University

---

## 🛠️ Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python (Django Framework - MVT Architecture)
- **Database**: MySQL / SQLite (configured with dual support)
- **Tools / IDE**: Visual Studio Code, Git, phpMyAdmin / MySQL Workbench

---

## 🚀 How to Run the Project Locally

### Step 1: Open Terminal / Command Prompt
Navigate to the project folder:
```bash
cd d:\LEARNMATE_MCA
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Populate Sample Seed Data
To populate sample courses (Python, PHP, DBMS), flashcards, quizzes, MCQs, and demo student/admin accounts with 1 command:
```bash
python seed_data.py
```

### Step 5: Start the Development Server
```bash
python manage.py runserver
```
Open your browser and visit: **`http://127.0.0.1:8000/`**

---

## 🔑 Default Login Credentials

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Admin / Teacher** | `admin` | `admin123` | Full access to manage courses, upload materials, create flashcards, build quizzes/MCQs, view student results & issue certificates. |
| **Student** | `student` | `student123` | Access study materials, flip flashcards, attempt timed quizzes, revise mistakes in Revision Hub, bookmark notes, and view certificates. |

*(You can also register a new student account using the Sign Up page)*

---

## 🗄️ Database Setup (MySQL Configuration)
By default, the project runs seamlessly using SQLite. If you want to connect to MySQL (e.g. via XAMPP / phpMyAdmin for college viva):
1. Start MySQL in XAMPP or MySQL Server.
2. Create a database named `learnmate_db`:
   ```sql
   CREATE DATABASE learnmate_db;
   ```
3. Open `learnmate_project/settings.py` and set:
   ```python
   USE_MYSQL = True
   ```
4. Run migrations: `python manage.py migrate` and seed data: `python seed_data.py`.
*(A raw SQL export is also available in `database/learnmate_db.sql` for direct import).*

---

## 📂 Project Directory Structure
```
LEARNMATE_MCA/
│
├── manage.py                  # Django CLI management script
├── requirements.txt           # Project dependencies
├── seed_data.py               # Auto-seed script for demo presentation
├── README.md                  # Project documentation & guide
│
├── learnmate_project/         # Project settings and core routing
│   ├── settings.py           # Database & app settings
│   ├── urls.py               # Root URL config
│   ├── wsgi.py
│   └── asgi.py
│
├── main_app/                  # Application logic
│   ├── models.py             # 13 Models corresponding to Data Dictionary
│   ├── views.py              # Controller views with student-friendly comments
│   ├── forms.py              # Forms for authentication & CRUD
│   ├── urls.py               # Application routes
│   └── admin.py              # Django Admin registrations
│
├── templates/                 # HTML Templates
│   ├── base.html             # Common layout, navbar, footer
│   ├── index.html            # Landing / Home page
│   ├── about.html            # Project profile & Ganpat University info
│   ├── auth/                 # Login & Signup templates
│   ├── student/              # Dashboard, Courses, Flashcards, Quiz, Revision Hub, Certificates
│   └── admin_panel/          # Admin stats dashboard, Course/Material/Quiz managers
│
├── static/                    # CSS, JavaScript, and asset files
│   ├── css/style.css         # Clean custom styling & 3D flashcard flip
│   └── js/main.js            # Timer, flip player, AJAX bookmarks & revision master
│
├── media/                     # Uploaded files & generated media
└── database/
    └── learnmate_db.sql      # Raw MySQL dump for submission
```

---

## 🎓 Key Features Implemented
1. **Course-wise Learning**: Access categorized notes, PDFs, presentations, and lecture resources.
2. **Interactive 3D Flashcards**: Flip digital cards (Question on front, Answer on back) with smooth Previous/Next navigation.
3. **Timed Quizzes & Instant Scoring**: Multiple-choice assessments with automatic score calculation and percentage badges.
4. **Mistake-Based Revision Hub**: Incorrectly answered quiz questions are auto-logged to a dedicated revision queue where students practice them and mark them as *Mastered*.
5. **Smart Bookmarks**: Save materials and flashcards for quick revision before exams.
6. **Official Certificate of Completion**: Printable & verifiable certificate of completion branded for Ganpat University (AMPICS).
7. **Admin / Teacher Dashboard**: Comprehensive management of courses, study notes, flashcards, MCQs, and student performance oversight.
=======
# LEARNMATE
>>>>>>> cfc439e990163d04054ba835081ae90fa7ed74f3
