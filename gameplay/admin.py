from django.contrib import admin
from .models import Department, Profile, ActionLog, Idea

admin.site.register(Department)
admin.site.register(Profile)
admin.site.register(ActionLog)
admin.site.register(Idea)