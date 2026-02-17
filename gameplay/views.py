from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Department, Idea, Profile, Training 
from .forms import IdeaForm, TrainingForm              
from django.contrib.auth.decorators import login_required

# 1. Home Page (Welcome)
def dashboard(request):
    return render(request, 'gameplay/dashboard.html')

# 2. Departments Page
def departments_page(request):
    all_departments = Department.objects.all()
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
        form = TrainingForm(request.POST)
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