from django.contrib import admin
from django.urls import path
from gameplay.views import dashboard, departments_page, ideas_page, vote_idea

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),                 # Homepage
    path('departments/', departments_page, name='departments_page'), # New Page
    path('ideas/', ideas_page, name='ideas_page'),         # New Page
    path('vote/<int:idea_id>/', vote_idea, name='vote_idea'),
]