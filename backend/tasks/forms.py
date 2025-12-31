

#Form for creating a new task
from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'assignee': forms.IntegerField(widget=forms.Select(choices=[(user.id, user.username) for user in User.objects.all()], attrs={'class': 'form-control'})),
        }