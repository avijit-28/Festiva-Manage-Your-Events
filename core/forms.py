from django import forms
from .models import Event
from django import forms
from django.core.validators import FileExtensionValidator

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'event_type', 
                 'location', 'start_date', 'end_date', 'capacity', 
                 'price', 'image']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class JobApplicationForm(forms.Form):
    position = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    resume = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    portfolio = forms.URLField(required=False)
    cover_letter = forms.CharField(widget=forms.Textarea)
    start_date = forms.DateField()
    employment_type = forms.ChoiceField(
        choices=[
            ('full_time', 'Full-time'),
            ('part_time', 'Part-time'),
            ('contract', 'Contract/Freelance'),
            ('internship', 'Internship')
        ]
    )