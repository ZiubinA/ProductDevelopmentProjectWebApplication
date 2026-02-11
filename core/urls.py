from django.contrib import admin
from django.urls import path
from gameplay.views import dashboard  # Import your new view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),  # The empty '' means "Homepage"
]