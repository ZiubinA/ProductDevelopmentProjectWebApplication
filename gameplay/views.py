from django.shortcuts import render, redirect
from .models import Department, Idea
from .forms import IdeaForm

def dashboard(request):
    # 1. Handle the Form Submission (POST request)
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            new_idea = form.save(commit=False)
            new_idea.submitted_by = None  # Explicitly set to None for anonymity
            new_idea.save()
            return redirect('dashboard')  # Refresh the page to show the new idea
    else:
        form = IdeaForm()

    # 2. Fetch data for the page
    all_departments = Department.objects.all()
    # Show pending ideas (waiting for approval)
    pending_ideas = Idea.objects.filter(is_approved=False).order_by('-votes')

    context = {
        'departments': all_departments,
        'ideas': pending_ideas,
        'form': form,  # Send the form to the HTML
    }
    
    return render(request, 'gameplay/dashboard.html', context)