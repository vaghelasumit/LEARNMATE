from django.urls import path
from . import views

urlpatterns = [
    # Public & Auth URLs
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),

    # Student URLs
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('courses/', views.course_list, name='courses'),
    path('courses/<int:subject_id>/', views.course_detail, name='course_detail'),
    path('material/<int:material_id>/', views.study_material_view, name='study_material_view'),
    path('courses/<int:subject_id>/flashcards/', views.flashcards_deck, name='flashcards_deck'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/result/<int:result_id>/', views.quiz_result_view, name='quiz_result'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    
    # Mistake Revision Hub
    path('revision/', views.revision_hub, name='revision_hub'),
    path('revision/<int:revision_id>/master/', views.mark_mastered, name='mark_mastered'),
    path('revision/<int:subject_id>/quiz/', views.take_revision_quiz, name='take_revision_quiz'),
    path('revision/<int:subject_id>/submit/', views.submit_revision_quiz, name='submit_revision_quiz'),

    # Bookmarks
    path('bookmark/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.bookmarks_list, name='bookmarks_list'),

    # Certificates & Profile
    path('certificates/', views.certificates_list, name='certificates_list'),
    path('certificate/<str:cert_no>/', views.view_certificate, name='view_certificate'),
    path('profile/', views.student_profile, name='student_profile'),

    # Admin Panel URLs
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/courses/', views.admin_manage_courses, name='admin_manage_courses'),
    path('admin-panel/courses/edit/<int:subject_id>/', views.admin_edit_course, name='admin_edit_course'),
    path('admin-panel/courses/delete/<int:subject_id>/', views.admin_delete_course, name='admin_delete_course'),
    
    path('admin-panel/materials/', views.admin_manage_materials, name='admin_manage_materials'),
    path('admin-panel/materials/edit/<int:material_id>/', views.admin_edit_material, name='admin_edit_material'),
    path('admin-panel/materials/delete/<int:material_id>/', views.admin_delete_material, name='admin_delete_material'),

    path('admin-panel/flashcards/', views.admin_manage_flashcards, name='admin_manage_flashcards'),
    path('admin-panel/flashcards/subject/<int:subject_id>/', views.admin_subject_flashcards, name='admin_subject_flashcards'),
    path('admin-panel/flashcards/edit/<int:flashcard_id>/', views.admin_edit_flashcard, name='admin_edit_flashcard'),
    path('admin-panel/flashcards/delete/<int:flashcard_id>/', views.admin_delete_flashcard, name='admin_delete_flashcard'),

    path('admin-panel/quizzes/', views.admin_manage_quizzes, name='admin_manage_quizzes'),
    path('admin-panel/quizzes/<int:quiz_id>/questions/', views.admin_manage_questions, name='admin_manage_questions'),
    path('admin-panel/quizzes/questions/delete/<int:question_id>/', views.admin_delete_question, name='admin_delete_question'),
    path('admin-panel/quizzes/delete/<int:quiz_id>/', views.admin_delete_quiz, name='admin_delete_quiz'),

    path('admin-panel/results/', views.admin_student_results, name='admin_student_results'),
    path('admin-panel/certificates/', views.admin_certificates, name='admin_certificates'),
    path('admin-panel/certificates/generate/<int:result_id>/', views.admin_generate_certificate, name='admin_generate_certificate'),
    path('admin-panel/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin-panel/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('ppt/', views.presentation_view, name='presentation'),
]
