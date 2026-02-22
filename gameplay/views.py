from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum
from .models import Department, Idea, Profile, Training, Question, QuizResult, Lesson
from .forms import IdeaForm, TrainingForm, QuestionForm, LessonForm         
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import re  

# 1. Home Page (Welcome)
def dashboard(request):
    return render(request, 'gameplay/dashboard.html')

# 2. Departments Page
def departments_page(request):
    all_departments = Department.objects.annotate(
        total_points=Sum('profile__total_score')
    ).order_by('-total_points')
    
    return render(request, 'gameplay/departments.html', {'departments': all_departments})

# 3. Ideas Page (Form + List)
def ideas_page(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            new_idea = form.save(commit=False)
            new_idea.submitted_by = request.user
            new_idea.save()
            return redirect('ideas_page') # Stay on this page
    else:
        form = IdeaForm()

    # Get ideas sorted by votes
    pending_ideas = Idea.objects.annotate(num_votes=Count('voters')).filter(is_approved=False).order_by('-num_votes')
    
    return render(request, 'gameplay/ideas.html', {'ideas': pending_ideas, 'form': form})

# 4. Voting Logic
def vote_idea(request, idea_id):
    idea = get_object_or_404(Idea, pk=idea_id)
    if request.user.is_authenticated:
        if request.user in idea.voters.all():
            idea.voters.remove(request.user)
        else:
            idea.voters.add(request.user)
    return redirect('ideas_page') # Go back to ideas page

@login_required
def profile_page(request):
    # This fetches the profile for the person who is logged in
    user_profile = get_object_or_404(Profile, user=request.user)
    # Fetch ideas submitted by this specific user
    my_ideas = Idea.objects.filter(submitted_by=request.user)
    
    return render(request, 'gameplay/profile.html', {
        'profile': user_profile,
        'my_ideas': my_ideas
    })

# 5. Training Page (List + Create)
def training_page(request):
    # Handle "Add Training" form
    if request.method == 'POST':
        form = TrainingForm(request.POST, request.FILES)
        if form.is_valid():
            new_training = form.save(commit=False)
            new_training.organizer = request.user
            new_training.save()
            return redirect('training_page')
    else:
        form = TrainingForm()

    # Get all trainings, sorted by newest first
    trainings = Training.objects.all().order_by('date_time')

    return render(request, 'gameplay/training.html', {
        'trainings': trainings, 
        'form': form
    })

# 6. Registration Logic (Like Voting)
def register_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)

    if request.user.is_authenticated:
        if request.user in training.attendees.all():
            training.attendees.remove(request.user) # Un-register
        else:
            training.attendees.add(request.user)    # Register

    return redirect('training_page')

# 7. Organizer adds a question
def add_question(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    
    # Security: Only the organizer can add questions
    if request.user != training.organizer:
        return redirect('training_page')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.training = training
            question.save()
            return redirect('add_question', training_id=training.id) # Reload to add another
    else:
        form = QuestionForm()

    # Show list of existing questions below the form
    existing_questions = training.questions.all()
    
    return render(request, 'gameplay/add_question.html', {
        'training': training, 
        'form': form, 
        'questions': existing_questions
    })

# 8. Attendees take the quiz
def take_quiz(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    questions = training.questions.all()

    if request.method == 'POST':
        score = 0
        for q in questions:
            selected_option = request.POST.get(f'question_{q.id}')
            if selected_option == q.correct_option:
                score += 1
        
        QuizResult.objects.create(training=training, user=request.user, score=score)
        
        request.user.profile.total_score += (score * 10)
        request.user.profile.save()

        return redirect('training_page')

    return render(request, 'gameplay/take_quiz.html', {'training': training, 'questions': questions})

# 9. Registration Page
def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after signing up
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'gameplay/register.html', {'form': form})

# 10. Organizer adds lessons to a training
def manage_lessons(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    
    # Security: Only the organizer can manage lessons
    if request.user != training.organizer:
        return redirect('training_page')

    if request.method == 'POST':
        # request.FILES is required for the attached slides/documents
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.training = training
            lesson.save()
            return redirect('manage_lessons', training_id=training.id)
    else:
        form = LessonForm(initial={'order': training.lessons.count() + 1})

    lessons = training.lessons.all()
    return render(request, 'gameplay/manage_lessons.html', {
        'training': training, 
        'form': form, 
        'lessons': lessons
    })

# 11. Attendees view the actual lesson
def view_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    training = lesson.training
    
    # Security: Must be registered to view
    if request.user not in training.attendees.all() and request.user != training.organizer:
        return redirect('training_page')
        
    return render(request, 'gameplay/view_lesson.html', {'lesson': lesson, 'training': training})

# 12. Department Profile Page
def department_detail(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    questions = department.questions.all()
    
    has_taken_quiz = QuizResult.objects.filter(user=request.user, department=department).exists()
    total_score = department.profile_set.aggregate(sum=Sum('total_score'))['sum'] or 0

    video_embed_url = None
    if department.video_url:
        regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(regex, department.video_url)
        
        if match:
            video_id = match.group(1)
            video_embed_url = f"https://www.youtube.com/embed/{video_id}"

    return render(request, 'gameplay/department_detail.html', {
        'department': department,
        'questions': questions,
        'has_taken_quiz': has_taken_quiz,
        'total_score': total_score,
        'video_embed_url': video_embed_url, 
    })

# 13. Add Questions to Department
def add_department_question(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    
    # Only superusers (Admins) should edit department quizzes
    if not request.user.is_superuser:
        return redirect('department_detail', department_id=department.id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.department = department 
            question.save()
            return redirect('add_department_question', department_id=department.id)
    else:
        form = QuestionForm()

    return render(request, 'gameplay/add_department_question.html', {
        'department': department, 
        'form': form,
        'questions': department.questions.all()
    })

# 14. Take Department Quiz
def take_department_quiz(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    questions = department.questions.all()

    # Prevent taking it twice
    if QuizResult.objects.filter(user=request.user, department=department).exists():
        return redirect('department_detail', department_id=department.id)

    if request.method == 'POST':
        score = 0
        for q in questions:
            selected = request.POST.get(f'question_{q.id}')
            if selected == q.correct_option:
                score += 1

        QuizResult.objects.create(department=department, user=request.user, score=score)
        
        # Give Points (e.g., 50 points for learning about a department!)
        points_earned = score * 10
        request.user.profile.total_score += points_earned
        request.user.profile.save()

        return redirect('department_detail', department_id=department.id)

    return render(request, 'gameplay/take_quiz.html', {
        'training': department,
        'questions': questions
    })