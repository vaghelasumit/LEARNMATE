from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
import json

from .models import (
    UserProfile, Subject, StudyMaterial, Flashcard,
    Quiz, QuizQuestion, QuizAttempt, QuizAnswer,
    QuizResult, Certificate, Bookmark, Revision
)
from .forms import (
    StudentRegisterForm, LoginForm, SubjectForm,
    StudyMaterialForm, FlashcardForm, QuizForm, QuizQuestionForm
)

# Helper function to check if user is Admin / Teacher
def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    try:
        return user.profile.role == 'admin'
    except Exception:
        return False


# ==============================================================================
# 1. PUBLIC & AUTHENTICATION VIEWS
# ==============================================================================

def home(request):
    """
    Landing / Home Page View (Matches Sketch 1)
    """
    subjects = Subject.objects.all().order_by('-created_at')[:6]
    total_subjects = Subject.objects.count()
    total_materials = StudyMaterial.objects.count()
    total_quizzes = Quiz.objects.count()
    total_flashcards = Flashcard.objects.count()
    
    context = {
        'subjects': subjects,
        'total_subjects': total_subjects,
        'total_materials': total_materials,
        'total_quizzes': total_quizzes,
        'total_flashcards': total_flashcards,
    }
    return render(request, 'index.html', context)


def user_signup(request):
    """
    Student Registration View (Matches Sketch 2)
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['full_name']
            user.save()
            
            # Create student user profile
            UserProfile.objects.create(user=user, role='student')
            
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegisterForm()

    return render(request, 'auth/signup.html', {'form': form})


def user_login(request):
    """
    User Login View for both Students and Admins (Matches Sketch 2)
    """
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if user entered email or username
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.filter(email__iexact=username_or_email).first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                    else:
                        user = None
                except Exception:
                    user = None
            else:
                user = authenticate(request, username=username_or_email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                if is_admin(user):
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def user_logout(request):
    """
    User Logout View
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
@login_required
def student_dashboard(request):
    """
    Student Main Dashboard (Matches Sketch 4)
    """
    if is_admin(request.user):
        return redirect('admin_dashboard')

    subjects = Subject.objects.all().order_by('-created_at')
    recent_attempts = QuizResult.objects.filter(student=request.user).order_by('-result_date')[:5]
    pending_revisions = Revision.objects.filter(student=request.user, revision_status='Pending').count()
    earned_certificates = Certificate.objects.filter(student=request.user).count()
    bookmarks_count = Bookmark.objects.filter(student=request.user).count()
    bookmarked_subject_ids = list(Bookmark.objects.filter(
        student=request.user, subject__isnull=False, material__isnull=True, flashcard__isnull=True, question__isnull=True
    ).values_list('subject_id', flat=True))

    context = {
        'subjects': subjects,
        'recent_attempts': recent_attempts,
        'pending_revisions': pending_revisions,
        'earned_certificates': earned_certificates,
        'bookmarks_count': bookmarks_count,
        'bookmarked_subject_ids': bookmarked_subject_ids,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def course_list(request):
    """
    Explore Courses / Subjects Page
    """
    query = request.GET.get('q', '')
    if query:
        subjects = Subject.objects.filter(
            Q(subject_name__icontains=query) | Q(description__icontains=query)
        )
    else:
        subjects = Subject.objects.all()

    bookmarked_subject_ids = list(Bookmark.objects.filter(
        student=request.user, subject__isnull=False, material__isnull=True, flashcard__isnull=True, question__isnull=True
    ).values_list('subject_id', flat=True))

    context = {
        'subjects': subjects,
        'query': query,
        'bookmarked_subject_ids': bookmarked_subject_ids,
    }
    return render(request, 'student/courses.html', context)


@login_required
def course_detail(request, subject_id):
    """
    Subject Detail Page with 4 Tabs: Study Material, Flashcards, Quiz, Revision
    """
    subject = get_object_or_404(Subject, subject_id=subject_id)
    materials = StudyMaterial.objects.filter(subject=subject).order_by('created_at')
    flashcards = Flashcard.objects.filter(subject=subject).order_by('created_at')
    quizzes = Quiz.objects.filter(subject=subject).order_by('created_at')
    
    revisions = Revision.objects.filter(
        student=request.user,
        question__quiz__subject=subject
    ).select_related('question')

    bookmarked_material_ids = Bookmark.objects.filter(
        student=request.user, material__isnull=False
    ).values_list('material_id', flat=True)
    
    bookmarked_flashcard_ids = set(Bookmark.objects.filter(
        student=request.user, flashcard__isnull=False
    ).values_list('flashcard_id', flat=True))

    is_subject_bookmarked = Bookmark.objects.filter(
        student=request.user, subject=subject, material__isnull=True, flashcard__isnull=True, question__isnull=True
    ).exists()

    certificate = Certificate.objects.filter(student=request.user, subject=subject).first()
    has_passed_quiz = QuizResult.objects.filter(student=request.user, quiz__subject=subject, result_status='Pass').exists()

    cards_data = []
    for card in flashcards:
        cards_data.append({
            'id': card.flashcard_id,
            'question': card.question,
            'answer': card.answer,
            'is_bookmarked': card.flashcard_id in bookmarked_flashcard_ids,
        })

    context = {
        'subject': subject,
        'materials': materials,
        'flashcards': flashcards,
        'cards_json': json.dumps(cards_data),
        'total_cards': len(cards_data),
        'quizzes': quizzes,
        'revisions': revisions,
        'bookmarked_material_ids': list(bookmarked_material_ids),
        'bookmarked_flashcard_ids': list(bookmarked_flashcard_ids),
        'is_subject_bookmarked': is_subject_bookmarked,
        'certificate': certificate,
        'has_passed_quiz': has_passed_quiz,
    }
    return render(request, 'student/course_detail.html', context)


@login_required
def study_material_view(request, material_id):
    """
    View Study Material (Notes, PPT, PDF, Video)
    """
    material = get_object_or_404(StudyMaterial, material_id=material_id)
    is_bookmarked = Bookmark.objects.filter(student=request.user, material=material).exists()

    context = {
        'material': material,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'student/study_material.html', context)


@login_required
def flashcards_deck(request, subject_id):
    """
    Interactive Flashcards Player (Flip Card with Prev/Next buttons)
    """
    subject = get_object_or_404(Subject, subject_id=subject_id)
    flashcards = Flashcard.objects.filter(subject=subject).order_by('flashcard_id')
    bookmarked_flashcard_ids = set(Bookmark.objects.filter(
        student=request.user, flashcard__isnull=False
    ).values_list('flashcard_id', flat=True))

    cards_data = []
    for card in flashcards:
        cards_data.append({
            'id': card.flashcard_id,
            'question': card.question,
            'answer': card.answer,
            'is_bookmarked': card.flashcard_id in bookmarked_flashcard_ids,
        })

    context = {
        'subject': subject,
        'flashcards': flashcards,
        'cards_json': json.dumps(cards_data),
        'total_cards': len(cards_data),
        'bookmarked_flashcard_ids': list(bookmarked_flashcard_ids),
    }
    return render(request, 'student/flashcards.html', context)


@login_required
def take_quiz(request, quiz_id):
    """
    Quiz Screen: displays MCQ questions with timer and options
    """
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    questions = quiz.questions.all().order_by('question_id')

    if not questions.exists():
        messages.warning(request, "This quiz currently does not have any questions.")
        return redirect('course_detail', subject_id=quiz.subject.subject_id)

    context = {
        'quiz': quiz,
        'questions': questions,
        'total_questions': questions.count(),
    }
    return render(request, 'student/take_quiz.html', context)


@login_required
def submit_quiz(request, quiz_id):
    """
    Evaluates quiz submission:
    - Calculates score & percentage
    - Records Attempt, Answers, and Result
    - Automatically adds wrong answers to Revision table
    - Auto-generates certificate if student passes
    """
    if request.method != 'POST':
        return redirect('dashboard')

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    questions = quiz.questions.all()
    total_marks = questions.count()
    score = 0

    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        status='Completed'
    )
    for question in questions:
        field_name = f"question_{question.question_id}"
        selected_answer = request.POST.get(field_name, '')

        is_correct = (selected_answer == question.correct_answer)
        if is_correct:
            score += 1

        QuizAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct
        )

        if not is_correct:
            revision_item, created = Revision.objects.get_or_create(
                student=request.user,
                question=question,
                defaults={'revision_status': 'Pending', 'notes': 'Auto-saved from quiz mistake.'}
            )
            if not created and revision_item.revision_status == 'Mastered':
                revision_item.revision_status = 'Pending'
                revision_item.save()

    percentage = (score / total_marks * 100) if total_marks > 0 else 0
    passed = score >= quiz.passing_marks
    result_status = 'Pass' if passed else 'Fail'

    result = QuizResult.objects.create(
        attempt=attempt,
        student=request.user,
        quiz=quiz,
        score=score,
        total_marks=total_marks,
        percentage=round(percentage, 2),
        result_status=result_status
    )

    return redirect('quiz_result', result_id=result.result_id)


@login_required
def quiz_result_view(request, result_id):
    """
    Detailed Result View showing score, pass/fail, and review of answers
    """
    result = get_object_or_404(QuizResult, result_id=result_id, student=request.user)
    answers = QuizAnswer.objects.filter(attempt=result.attempt).select_related('question')
    certificate = Certificate.objects.filter(student=request.user, subject=result.quiz.subject).first()
    bookmarked_question_ids = list(Bookmark.objects.filter(
        student=request.user, question__isnull=False
    ).values_list('question_id', flat=True))

    context = {
        'result': result,
        'answers': answers,
        'certificate': certificate,
        'bookmarked_question_ids': bookmarked_question_ids,
    }
    return render(request, 'student/quiz_result.html', context)


@login_required
def quiz_history(request):
    """
    View all quiz attempts and results for the current student
    """
    results = QuizResult.objects.filter(student=request.user).order_by('-result_date')
    return render(request, 'student/quiz_history.html', {'results': results})


@login_required
def revision_hub(request):
    """
    Mistake-Based Revision Hub:
    Organized by course/subject. Only questions for the selected course are displayed.
    If questions exist for a course (e.g. Database), only that course is shown.
    Accessing a different subject shows only that subject from the beginning.
    """
    all_student_revisions = Revision.objects.filter(student=request.user).select_related(
        'question', 'question__quiz', 'question__quiz__subject'
    ).order_by('revision_status', '-revision_date')

    subject_ids_with_revisions = list(
        all_student_revisions.values_list('question__quiz__subject_id', flat=True).distinct()
    )
    subjects_with_revisions = Subject.objects.filter(subject_id__in=subject_ids_with_revisions).order_by('subject_name')

    subject_tabs = []
    for subj in subjects_with_revisions:
        subj_revs = all_student_revisions.filter(question__quiz__subject=subj)
        pending = subj_revs.filter(revision_status='Pending').count()
        mastered = subj_revs.filter(revision_status='Mastered').count()
        subject_tabs.append({
            'subject': subj,
            'total_count': subj_revs.count(),
            'pending_count': pending,
            'mastered_count': mastered,
        })

    selected_subject_id = request.GET.get('subject_id')
    selected_subject = None

    if selected_subject_id:
        try:
            subj_id_int = int(selected_subject_id)
            selected_subject = Subject.objects.filter(subject_id=subj_id_int).first()
        except (ValueError, TypeError):
            selected_subject = None

    if not selected_subject and subject_tabs:
        pending_tab = next((tab for tab in subject_tabs if tab['pending_count'] > 0), subject_tabs[0])
        selected_subject = pending_tab['subject']

    if selected_subject:
        active_revisions = all_student_revisions.filter(question__quiz__subject=selected_subject)
        for rev in active_revisions:
            latest_ans = QuizAnswer.objects.filter(
                attempt__student=request.user,
                question=rev.question
            ).order_by('-answer_id').first()
            rev.last_selected_answer = latest_ans.selected_answer if latest_ans else None
    else:
        active_revisions = Revision.objects.none()

    pending_count = active_revisions.filter(revision_status='Pending').count()
    mastered_count = active_revisions.filter(revision_status='Mastered').count()
    bookmarked_question_ids = list(Bookmark.objects.filter(
        student=request.user, question__isnull=False
    ).values_list('question_id', flat=True))

    context = {
        'subject_tabs': subject_tabs,
        'selected_subject': selected_subject,
        'revisions': active_revisions,
        'pending_count': pending_count,
        'mastered_count': mastered_count,
        'total_all_pending': all_student_revisions.filter(revision_status='Pending').count(),
        'bookmarked_question_ids': bookmarked_question_ids,
    }
    return render(request, 'student/revision.html', context)


@login_required
def mark_mastered(request, revision_id):
    """
    AJAX / POST toggle for marking a mistake question as Mastered / Pending
    """
    revision = get_object_or_404(Revision, revision_id=revision_id, student=request.user)
    if revision.revision_status == 'Pending':
        revision.revision_status = 'Mastered'
    else:
        revision.revision_status = 'Pending'
    revision.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'new_status': revision.revision_status})
    messages.success(request, f"Question marked as {revision.revision_status}.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    subject_id = revision.question.quiz.subject.subject_id
    return redirect(f"{reverse('revision_hub')}?subject_id={subject_id}")


@login_required
def take_revision_quiz(request, subject_id):
    """
    Retake Revision Quiz:
    Displays an interactive quiz containing only the mistake questions for the specific course.
    """
    subject = get_object_or_404(Subject, subject_id=subject_id)
    revisions = Revision.objects.filter(
        student=request.user,
        question__quiz__subject=subject
    ).select_related('question')

    if not revisions.exists():
        messages.info(request, f"No revision questions found for {subject.subject_name}.")
        return redirect(f"{reverse('revision_hub')}?subject_id={subject.subject_id}")

    questions = [rev.question for rev in revisions]

    context = {
        'subject': subject,
        'questions': questions,
        'total_questions': len(questions),
        'revisions_count': revisions.count(),
    }
    return render(request, 'student/take_revision_quiz.html', context)


@login_required
def submit_revision_quiz(request, subject_id):
    """
    Evaluates submitted revision quiz answers:
    - If student gets question right, it is marked as 'Mastered'.
    - If wrong, it remains 'Pending'.
    - Renders detailed results and review.
    """
    if request.method != 'POST':
        return redirect('revision_hub')

    subject = get_object_or_404(Subject, subject_id=subject_id)
    revisions = Revision.objects.filter(
        student=request.user,
        question__quiz__subject=subject
    ).select_related('question')

    if not revisions.exists():
        messages.warning(request, f"No revision questions found for {subject.subject_name}.")
        return redirect('revision_hub')

    results = []
    score = 0
    total = revisions.count()

    for rev in revisions:
        q = rev.question
        field_name = f"question_{q.question_id}"
        selected_answer = request.POST.get(field_name, '')

        is_correct = (selected_answer.upper() == q.correct_answer.upper())
        if is_correct:
            score += 1
            rev.revision_status = 'Mastered'
        else:
            rev.revision_status = 'Pending'
        rev.save()

        results.append({
            'question': q,
            'selected_answer': selected_answer,
            'is_correct': is_correct,
            'new_status': rev.revision_status,
        })

    percentage = round((score / total * 100), 2) if total > 0 else 0
    all_mastered = (score == total)

    context = {
        'subject': subject,
        'results': results,
        'score': score,
        'total': total,
        'percentage': percentage,
        'all_mastered': all_mastered,
    }
    return render(request, 'student/revision_quiz_result.html', context)


@login_required
def toggle_bookmark(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')

        if not item_type or not item_id:
            return JsonResponse({'status': 'error', 'message': 'Missing item_type or item_id'}, status=400)

        if item_type == 'material':
            material = get_object_or_404(StudyMaterial, material_id=item_id)
            existing = Bookmark.objects.filter(student=request.user, material=material).first()
            if existing:
                existing.delete()
                return JsonResponse({'status': 'removed', 'item_type': item_type, 'item_id': item_id, 'message': 'Material bookmark removed'})
            else:
                Bookmark.objects.create(student=request.user, material=material, subject=material.subject)
                return JsonResponse({'status': 'added', 'item_type': item_type, 'item_id': item_id, 'message': 'Material bookmarked'})

        elif item_type == 'flashcard':
            flashcard = get_object_or_404(Flashcard, flashcard_id=item_id)
            existing = Bookmark.objects.filter(student=request.user, flashcard=flashcard).first()
            if existing:
                existing.delete()
                return JsonResponse({'status': 'removed', 'item_type': item_type, 'item_id': item_id, 'message': 'Flashcard bookmark removed'})
            else:
                Bookmark.objects.create(student=request.user, flashcard=flashcard, subject=flashcard.subject)
                return JsonResponse({'status': 'added', 'item_type': item_type, 'item_id': item_id, 'message': 'Flashcard bookmarked'})

        elif item_type == 'question':
            question = get_object_or_404(QuizQuestion, question_id=item_id)
            existing = Bookmark.objects.filter(student=request.user, question=question).first()
            if existing:
                existing.delete()
                return JsonResponse({'status': 'removed', 'item_type': item_type, 'item_id': item_id, 'message': 'Question bookmark removed'})
            else:
                Bookmark.objects.create(student=request.user, question=question, subject=question.quiz.subject)
                return JsonResponse({'status': 'added', 'item_type': item_type, 'item_id': item_id, 'message': 'Question bookmarked'})

        elif item_type == 'subject':
            subject = get_object_or_404(Subject, subject_id=item_id)
            existing = Bookmark.objects.filter(
                student=request.user,
                subject=subject,
                material__isnull=True,
                flashcard__isnull=True,
                question__isnull=True
            ).first()
            if existing:
                existing.delete()
                return JsonResponse({'status': 'removed', 'item_type': item_type, 'item_id': item_id, 'message': 'Subject bookmark removed'})
            else:
                Bookmark.objects.create(student=request.user, subject=subject)
                return JsonResponse({'status': 'added', 'item_type': item_type, 'item_id': item_id, 'message': 'Subject bookmarked'})

        return JsonResponse({'status': 'error', 'message': f'Invalid item type: {item_type}'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def bookmarks_list(request):
    """
    Student Bookmarks Page: view all saved subjects, materials, flashcards, and questions
    """
    bookmarks = Bookmark.objects.filter(student=request.user).select_related(
        'subject', 'material', 'flashcard', 'question', 'question__quiz', 'question__quiz__subject'
    ).order_by('-bookmarked_date')

    total_count = bookmarks.count()
    subject_count = bookmarks.filter(subject__isnull=False, material__isnull=True, flashcard__isnull=True, question__isnull=True).count()
    material_count = bookmarks.filter(material__isnull=False).count()
    flashcard_count = bookmarks.filter(flashcard__isnull=False).count()
    question_count = bookmarks.filter(question__isnull=False).count()

    context = {
        'bookmarks': bookmarks,
        'total_count': total_count,
        'subject_count': subject_count,
        'material_count': material_count,
        'flashcard_count': flashcard_count,
        'question_count': question_count,
    }
    return render(request, 'student/bookmarks.html', context)


@login_required
def certificates_list(request):
    """
    List all earned certificates & pending approval requests for student
    """
    certificates = Certificate.objects.filter(student=request.user).select_related('subject', 'result').order_by('-issue_date')
    issued_subject_ids = certificates.values_list('subject_id', flat=True)

    passed_results = QuizResult.objects.filter(
        student=request.user,
        result_status='Pass'
    ).exclude(
        quiz__subject_id__in=issued_subject_ids
    ).select_related('quiz', 'quiz__subject').order_by('-result_date')

    pending_subjects = []
    seen = set()
    for res in passed_results:
        if res.quiz.subject_id not in seen:
            seen.add(res.quiz.subject_id)
            pending_subjects.append(res)

    context = {
        'certificates': certificates,
        'pending_subjects': pending_subjects,
    }
    return render(request, 'student/certificates.html', context)


@login_required
def view_certificate(request, cert_no):
    """
    Printable & downloadable Certificate Page
    """
    certificate = get_object_or_404(Certificate, certificate_no=cert_no)
    
    if not is_admin(request.user) and certificate.student != request.user:
        messages.error(request, "You do not have permission to view this certificate.")
        return redirect('dashboard')

    context = {
        'certificate': certificate,
        'student': certificate.student,
        'subject': certificate.subject,
        'result': certificate.result,
        'issue_date': certificate.issue_date,
    }
    return render(request, 'student/certificate_view.html', context)


@login_required
def student_profile(request):
    """
    Student Profile view with total statistics
    """
    attempts_count = QuizAttempt.objects.filter(student=request.user).count()
    passed_count = QuizResult.objects.filter(student=request.user, result_status='Pass').count()
    certificates_count = Certificate.objects.filter(student=request.user).count()
    bookmarks_count = Bookmark.objects.filter(student=request.user).count()

    context = {
        'attempts_count': attempts_count,
        'passed_count': passed_count,
        'certificates_count': certificates_count,
        'bookmarks_count': bookmarks_count,
    }
    return render(request, 'student/profile.html', context)



@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Admin Dashboard (Matches Sketch 3 stats and management tables)
    """
    total_students = UserProfile.objects.filter(role='student').count()
    total_courses = Subject.objects.count()
    total_materials = StudyMaterial.objects.count()
    total_quizzes = Quiz.objects.count()
    total_flashcards = Flashcard.objects.count()
    total_certificates = Certificate.objects.count()

    issued_pairs = set(Certificate.objects.values_list('student_id', 'subject_id'))
    passed_results = QuizResult.objects.filter(result_status='Pass').values_list('student_id', 'quiz__subject_id').distinct()
    pending_certificates_count = sum(1 for p in passed_results if p not in issued_pairs)

    user_query = request.GET.get('user_search', '')
    course_query = request.GET.get('course_search', '')

    if user_query:
        students = User.objects.filter(
            Q(profile__role='student') & 
            (Q(username__icontains=user_query) | Q(email__icontains=user_query) | Q(first_name__icontains=user_query))
        ).distinct()
    else:
        students = User.objects.filter(profile__role='student').order_by('-date_joined')[:10]

    if course_query:
        courses = Subject.objects.filter(subject_name__icontains=course_query)
    else:
        courses = Subject.objects.all().order_by('-created_at')[:10]

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_materials': total_materials,
        'total_quizzes': total_quizzes,
        'total_flashcards': total_flashcards,
        'total_certificates': total_certificates,
        'pending_certificates_count': pending_certificates_count,
        'students': students,
        'courses': courses,
        'user_query': user_query,
        'course_query': course_query,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_manage_courses(request):
    """
    List & Add Courses
    """
    courses = Subject.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.created_by = request.user
            subject.save()
            messages.success(request, f"Subject '{subject.subject_name}' created successfully!")
            return redirect('admin_manage_courses')
        else:
            messages.error(request, "Failed to create subject. Please check the form errors below.")
    else:
        form = SubjectForm()

    return render(request, 'admin_panel/manage_courses.html', {'courses': courses, 'form': form})


@login_required
@user_passes_test(is_admin)
def admin_edit_course(request, subject_id):
    """
    Edit Course
    """
    course = get_object_or_404(Subject, subject_id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Subject '{course.subject_name}' updated successfully!")
            return redirect('admin_manage_courses')
        else:
            messages.error(request, "Failed to update subject. Please check the form errors below.")
    else:
        form = SubjectForm(instance=course)

    return render(request, 'admin_panel/edit_course.html', {'form': form, 'course': course})


@login_required
@user_passes_test(is_admin)
def admin_delete_course(request, subject_id):
    """
    Delete Course
    """
    course = get_object_or_404(Subject, subject_id=subject_id)
    course_name = course.subject_name
    course.delete()
    messages.success(request, f"Subject '{course_name}' has been deleted.")
    return redirect('admin_manage_courses')


@login_required
@user_passes_test(is_admin)
def admin_manage_materials(request):
    """
    List & Upload Study Materials
    """
    materials = StudyMaterial.objects.all().select_related('subject', 'created_by').order_by('-created_at')
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user
            material.save()
            messages.success(request, f"Study Material '{material.title}' uploaded successfully!")
            return redirect('admin_manage_materials')
        else:
            messages.error(request, "Failed to upload study material. Please check the form errors below.")
    else:
        form = StudyMaterialForm()

    return render(request, 'admin_panel/manage_materials.html', {'materials': materials, 'form': form})


@login_required
@user_passes_test(is_admin)
def admin_edit_material(request, material_id):
    """
    Edit Study Material
    """
    material = get_object_or_404(StudyMaterial, material_id=material_id)
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, f"Study Material '{material.title}' updated successfully!")
            return redirect('admin_manage_materials')
        else:
            messages.error(request, "Failed to update study material. Please check the form errors below.")
    else:
        form = StudyMaterialForm(instance=material)

    return render(request, 'admin_panel/edit_material.html', {'form': form, 'material': material})


@login_required
@user_passes_test(is_admin)
def admin_delete_material(request, material_id):
    """
    Delete Study Material
    """
    material = get_object_or_404(StudyMaterial, material_id=material_id)
    material.delete()
    messages.success(request, "Study material deleted successfully.")
    return redirect('admin_manage_materials')


@login_required
@user_passes_test(is_admin)
def admin_manage_flashcards(request):
    """
    Step 1: View all subjects first, then click on subject to manage its flashcards
    """
    subject_id = request.GET.get('subject_id')
    if subject_id:
        return redirect('admin_subject_flashcards', subject_id=subject_id)

    subjects = Subject.objects.all().annotate(card_count=Count('flashcards')).order_by('subject_name')
    total_flashcards = Flashcard.objects.count()

    return render(request, 'admin_panel/manage_flashcards.html', {
        'subjects': subjects,
        'total_flashcards': total_flashcards
    })


@login_required
@user_passes_test(is_admin)
def admin_subject_flashcards(request, subject_id):
    """
    Step 2: Manage Flashcards Subject-Wise (Add, Edit, Delete for this subject)
    """
    subject = get_object_or_404(Subject, subject_id=subject_id)
    flashcards = Flashcard.objects.filter(subject=subject).order_by('-created_at')

    if request.method == 'POST':
        form = FlashcardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.subject = subject
            card.created_by = request.user
            card.save()
            messages.success(request, f"Flashcard added to '{subject.subject_name}' successfully!")
            return redirect('admin_subject_flashcards', subject_id=subject.subject_id)
        else:
            messages.error(request, "Failed to add flashcard. Please check the form errors below.")
    else:
        form = FlashcardForm(initial={'subject': subject})

    return render(request, 'admin_panel/manage_subject_flashcards.html', {
        'subject': subject,
        'flashcards': flashcards,
        'form': form,
    })


@login_required
@user_passes_test(is_admin)
def admin_edit_flashcard(request, flashcard_id):
    """
    Edit Flashcard (Subject-wise)
    """
    card = get_object_or_404(Flashcard, flashcard_id=flashcard_id)
    subject_id = card.subject.subject_id
    if request.method == 'POST':
        form = FlashcardForm(request.POST, instance=card)
        if form.is_valid():
            updated_card = form.save()
            messages.success(request, "Flashcard updated successfully!")
            return redirect('admin_subject_flashcards', subject_id=updated_card.subject.subject_id)
        else:
            messages.error(request, "Failed to update flashcard. Please check the form errors below.")
    else:
        form = FlashcardForm(instance=card)

    return render(request, 'admin_panel/edit_flashcard.html', {
        'form': form,
        'card': card,
        'subject': card.subject
    })


@login_required
@user_passes_test(is_admin)
def admin_delete_flashcard(request, flashcard_id):
    """
    Delete Flashcard (Subject-wise)
    """
    card = get_object_or_404(Flashcard, flashcard_id=flashcard_id)
    subject_id = card.subject.subject_id
    card.delete()
    messages.success(request, "Flashcard deleted successfully.")
    return redirect('admin_subject_flashcards', subject_id=subject_id)

@login_required
@user_passes_test(is_admin)
def admin_manage_quizzes(request):
    """
    List & Create Quizzes
    """
    quizzes = Quiz.objects.all().select_related('subject').annotate(num_questions=Count('questions')).order_by('-created_at')
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, f"Quiz '{quiz.quiz_title}' created successfully!")
            return redirect('admin_manage_quizzes')
        else:
            messages.error(request, "Failed to create quiz. Please check the form errors below.")
    else:
        form = QuizForm()

    return render(request, 'admin_panel/manage_quizzes.html', {'quizzes': quizzes, 'form': form})


@login_required
@user_passes_test(is_admin)
def admin_manage_questions(request, quiz_id):
    """
    Manage MCQ Questions for a specific quiz
    """
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    questions = quiz.questions.all().order_by('question_id')

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
    
            quiz.total_questions = quiz.questions.count()
            quiz.save()
            messages.success(request, "Question added successfully!")
            return redirect('admin_manage_questions', quiz_id=quiz.quiz_id)
        else:
            messages.error(request, "Failed to add question. Please check the form errors below.")
    else:
        form = QuizQuestionForm()

    return render(request, 'admin_panel/manage_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'form': form
    })


@login_required
@user_passes_test(is_admin)
def admin_delete_question(request, question_id):
    """
    Delete Question
    """
    question = get_object_or_404(QuizQuestion, question_id=question_id)
    quiz_id = question.quiz.quiz_id
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect('admin_manage_questions', quiz_id=quiz_id)


@login_required
@user_passes_test(is_admin)
def admin_delete_quiz(request, quiz_id):
    """
    Delete Quiz
    """
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    quiz.delete()
    messages.success(request, "Quiz deleted successfully.")
    return redirect('admin_manage_quizzes')

@login_required
@user_passes_test(is_admin)
def admin_student_results(request):
    """
    View Student Quiz Results & Performance with Certificate Generation Actions
    """
    results = QuizResult.objects.all().select_related('student', 'quiz', 'quiz__subject').order_by('-result_date')
    certs = Certificate.objects.all().select_related('student', 'subject')
    cert_map = {(c.student_id, c.subject_id): c for c in certs}
    for r in results:
        r.cert = cert_map.get((r.student_id, r.quiz.subject_id))

    return render(request, 'admin_panel/student_results.html', {'results': results})


@login_required
@user_passes_test(is_admin)
def admin_certificates(request):
    """
    List all awarded certificates and pending certificate requests awaiting generation
    """
    certificates = Certificate.objects.all().select_related('student', 'subject', 'result').order_by('-issue_date')

    issued_pairs = set(Certificate.objects.values_list('student_id', 'subject_id'))
    passed_results = QuizResult.objects.filter(result_status='Pass').select_related(
        'student', 'quiz', 'quiz__subject'
    ).order_by('-result_date')

    pending_requests = []
    seen = set()
    for res in passed_results:
        pair = (res.student_id, res.quiz.subject_id)
        if pair not in issued_pairs and pair not in seen:
            seen.add(pair)
            pending_requests.append(res)

    context = {
        'certificates': certificates,
        'pending_requests': pending_requests,
    }
    return render(request, 'admin_panel/certificates.html', context)


@login_required
@user_passes_test(is_admin)
def admin_generate_certificate(request, result_id):
    """
    Admin generates/issues an official certificate for a student who passed a quiz.
    """
    result = get_object_or_404(QuizResult, result_id=result_id)
    if result.result_status != 'Pass':
        messages.error(request, "Cannot generate certificate for a quiz attempt that did not meet passing score.")
        return redirect('admin_certificates')

    existing_cert = Certificate.objects.filter(student=result.student, subject=result.quiz.subject).first()
    if existing_cert:
        messages.info(request, f"Certificate already exists for {result.student.username} ({existing_cert.certificate_no}).")
    else:
        cert_no = Certificate.generate_certificate_number()
        Certificate.objects.create(
            student=result.student,
            subject=result.quiz.subject,
            result=result,
            certificate_no=cert_no
        )
        messages.success(request, f"Certificate {cert_no} successfully generated for {result.student.first_name or result.student.username} ({result.quiz.subject.subject_name})!")

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('admin_certificates')


@login_required
@user_passes_test(is_admin)
def admin_manage_users(request):
    """
    Manage Registered Users & Students (Matches Sketch 3)
    """
    students = User.objects.filter(profile__role='student').order_by('-date_joined')
    return render(request, 'admin_panel/manage_users.html', {'students': students})


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    """
    Delete User
    """
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete superuser.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('admin_manage_users')


def presentation_view(request):
    """
    Renders the MCA Project Presentation Slides (ppt.html)
    """
    return render(request, 'ppt.html')
