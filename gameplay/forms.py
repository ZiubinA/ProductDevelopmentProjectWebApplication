from django import forms
from .models import Idea

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Idea Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your idea...', 'rows': 3}),
        }