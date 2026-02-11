from django.shortcuts import render
from .models import Department, Idea

def dashboard(request):
    # Fetch data from the database
    all_departments = Department.objects.all()
    top_ideas = Idea.objects.filter(is_approved=False).order_by('-votes')[:5]
    
    # Prepare the data to send to the HTML
    context = {
        'departments': all_departments,
        'ideas': top_ideas
    }
    
    return render(request, 'gameplay/dashboard.html', context)