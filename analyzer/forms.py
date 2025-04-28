from django import forms

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        label='Select a resume',
        help_text='PDF or DOCX files only',
        widget=forms.FileInput(attrs={'accept': '.pdf,.docx'})
    )