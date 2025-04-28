from django import forms
from .models import Job
from shortlist.models import Resume_shortlist

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_title', 'company_name', 'location', 'job_type', 'job_description', 'keywords']
        widgets = {
            'job_description': forms.Textarea(attrs={'rows': 5}),
            'keywords': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, Software Engineer'}),
        }


# shortlist/forms.py

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume_shortlist
        fields = ['job', 'file', 'name', 'email', 'phone']  # Only fields that exist in the model
        widgets = {
            'job': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Applicant name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Applicant email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Applicant phone'}),
        }
        labels = {
            'file': 'Resume File',
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number'
        }
        help_texts = {
            'file': 'Upload resume file (PDF or DOCX)',
        }


