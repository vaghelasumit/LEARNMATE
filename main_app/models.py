from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin / Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='subjects/', null=True, blank=True, help_text="Upload subject cover image")
    image_url = models.URLField(max_length=500, null=True, blank=True, help_text="Or paste direct web image URL")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_url:
            return self.image_url
        name_lower = self.subject_name.lower()
        if 'python' in name_lower:
            return 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&auto=format&fit=crop&q=80'
        elif 'php' in name_lower or 'web' in name_lower:
            return 'https://images.unsplash.com/photo-1599507593499-a3f7f7d97f66?w=600&auto=format&fit=crop&q=80'
        elif 'dbms' in name_lower or 'data' in name_lower or 'sql' in name_lower:
            return 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=600&auto=format&fit=crop&q=80'
        elif 'java' in name_lower:
            return 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&auto=format&fit=crop&q=80'
        return 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&auto=format&fit=crop&q=80'

    def __str__(self):
        return self.subject_name

    class Meta:
        db_table = 'subject'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'


class StudyMaterial(models.Model):
    MATERIAL_TYPES = (
        ('notes', 'Study Notes / Text'),
        ('pdf', 'PDF Document'),
        ('ppt', 'Presentation (PPT)'),
        ('video', 'Video Lecture / Link'),
    )
    material_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=150)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='notes')
    file_path = models.FileField(upload_to='materials/', null=True, blank=True)
    drive_link = models.URLField(max_length=500, null=True, blank=True, help_text="Google Drive link for notes/PDFs")
    video_url = models.URLField(max_length=500, null=True, blank=True, help_text="YouTube or Video Lecture URL")
    description = models.TextField(help_text="Detailed notes or description of the material")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.subject_name}"

    class Meta:
        db_table = 'study_material'
        verbose_name = 'Study Material'
        verbose_name_plural = 'Study Materials'


class Flashcard(models.Model):
    flashcard_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='flashcards')
    question = models.TextField(help_text="Front of flashcard: Question or Concept")
    answer = models.TextField(help_text="Back of flashcard: Explanation or Answer")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Flashcard #{self.flashcard_id}: {self.question[:40]}..."

    class Meta:
        db_table = 'flashcard'
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'

class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    quiz_title = models.CharField(max_length=150)
    total_questions = models.IntegerField(default=5)
    passing_marks = models.IntegerField(default=3)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_title} ({self.subject.subject_name})"

    class Meta:
        db_table = 'quiz'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

class QuizQuestion(models.Model):
    ANSWER_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )
    question_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, help_text="Select correct option (A/B/C/D)")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for student revision")

    def __str__(self):
        return f"Q{self.question_id}: {self.question_text[:50]}"

    class Meta:
        db_table = 'quiz_question'
        verbose_name = 'Quiz Question'
        verbose_name_plural = 'Quiz Questions'

class QuizAttempt(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    attempt_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Completed')

    def __str__(self):
        return f"Attempt #{self.attempt_id} by {self.student.username} on {self.quiz.quiz_title}"

    class Meta:
        db_table = 'quiz_attempt'
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'

class QuizAnswer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=10) # 'A', 'B', 'C', or 'D'
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Ans #{self.answer_id} (Attempt #{self.attempt.attempt_id}) - Correct: {self.is_correct}"

    class Meta:
        db_table = 'quiz_answer'
        verbose_name = 'Quiz Answer'
        verbose_name_plural = 'Quiz Answers'

class QuizResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='result')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_marks = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    result_status = models.CharField(max_length=20, default='Pass') 
    result_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result #{self.result_id}: {self.student.username} - {self.score}/{self.total_marks} ({self.result_status})"

    class Meta:
        db_table = 'quiz_result'
        verbose_name = 'Quiz Result'
        verbose_name_plural = 'Quiz Results'

class Certificate(models.Model):
    certificate_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='issued_certificates')
    result = models.ForeignKey(QuizResult, on_delete=models.CASCADE, null=True, blank=True)
    certificate_no = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    certificate_path = models.CharField(max_length=255, blank=True, null=True)

    @staticmethod
    def generate_certificate_number():
        """Helper to generate sequential simple certificate numbers: 1, 2, 3, 4, ..."""
        max_num = 0
        for cert in Certificate.objects.all():
            try:
                num = int(str(cert.certificate_no).strip())
                if num > max_num:
                    max_num = num
            except (ValueError, TypeError):
                pass
        next_num = max_num + 1 if max_num > 0 else (Certificate.objects.count() + 1 if Certificate.objects.exists() else 1)
        while Certificate.objects.filter(certificate_no=str(next_num)).exists():
            next_num += 1
        return str(next_num)

    def __str__(self):
        return f"Certificate {self.certificate_no} for {self.student.username}"

    class Meta:
        db_table = 'certificate'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'

class Bookmark(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, null=True, blank=True)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, null=True, blank=True)
    bookmarked_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return f"Bookmark #{self.bookmark_id} by {self.student.username}"

    class Meta:
        db_table = 'bookmark'
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'

class Revision(models.Model):
    REVISION_STATUS = (
        ('Pending', 'Needs Practice'),
        ('Mastered', 'Mastered / Corrected'),
    )
    revision_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revision_items')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='revisions')
    revision_date = models.DateTimeField(auto_now_add=True)
    revision_status = models.CharField(max_length=20, choices=REVISION_STATUS, default='Pending')
    notes = models.TextField(blank=True, null=True, help_text="Personal notes for this mistake")

    def __str__(self):
        return f"Revision #{self.revision_id} for {self.student.username} - {self.revision_status}"

    class Meta:
        db_table = 'revision'
        verbose_name = 'Revision'
        verbose_name_plural = 'Revisions'
