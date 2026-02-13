from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Department, Idea
from .forms import IdeaForm

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