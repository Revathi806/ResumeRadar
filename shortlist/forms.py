from django import forms
from HR.models import Job

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ResumeShortlistForm(forms.Form):
    resumes = MultipleFileField(
        label='Upload Resumes',
        help_text='Upload multiple resumes (PDF or DOCX)'
    )
    
    job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        label='Select Job',
        empty_label="Select a job"
    )
    
    keywords = forms.CharField(
        label='Keywords',
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Keywords for matching (auto-filled based on job)'
    )