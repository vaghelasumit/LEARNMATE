from django.contrib import admin
from .models import (
    UserProfile, Subject, StudyMaterial, Flashcard,
    Quiz, QuizQuestion, QuizAttempt, QuizAnswer,
    QuizResult, Certificate, Bookmark, Revision
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id', 'subject_name', 'created_by', 'created_at')
    search_fields = ('subject_name',)

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'title', 'subject', 'material_type', 'created_at')
    list_filter = ('material_type', 'subject')
    search_fields = ('title', 'description')

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('flashcard_id', 'subject', 'question', 'created_at')
    list_filter = ('subject',)
    search_fields = ('question', 'answer')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('quiz_id', 'quiz_title', 'subject', 'total_questions', 'passing_marks', 'created_at')
    list_filter = ('subject',)
    search_fields = ('quiz_title',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'quiz', 'question_text', 'correct_answer')
    list_filter = ('quiz__subject', 'quiz')
    search_fields = ('question_text',)

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_id', 'student', 'quiz', 'attempt_date', 'status')
    list_filter = ('status', 'quiz')

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_id', 'attempt', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('result_id', 'student', 'quiz', 'score', 'total_marks', 'percentage', 'result_status', 'result_date')
    list_filter = ('result_status', 'quiz')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_no', 'student', 'subject', 'issue_date')
    search_fields = ('certificate_no', 'student__username')

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('bookmark_id', 'student', 'subject', 'material', 'flashcard', 'question', 'bookmarked_date', 'status')
    list_filter = ('status', 'subject')
    search_fields = ('student__username', 'subject__subject_name')

@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('revision_id', 'student', 'question', 'revision_status', 'revision_date')
    list_filter = ('revision_status',)
