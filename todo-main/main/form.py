from django import forms
from .models import Todo


# Create your form here
class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ('task', 'details', 'category', 'status')
        widgets = {
            'task': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task here', 'required': 'required'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter task details...', 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-control'}, choices={}),
            'status': forms.Select(attrs={'class': 'form-control'}, choices={})
        }
