import os
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from docx import Document
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .forms import ResumeUploadForm
from HR.models import Job,Application
from shortlist.models import Resume_shortlist

model = SentenceTransformer('all-MiniLM-L6-v2')

class IndexView(LoginRequiredMixin, View):
    template_name = 'analyzer/index.html'
    login_url = reverse_lazy('login')

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def calculate_ats_score(resume_text, job_description=None):
    word_count = len(resume_text.split())
    length_score = min(word_count / 500 * 100, 100)
    
    sections = ['experience', 'education', 'skills', 'projects']
    section_score = 0
    for section in sections:
        if section in resume_text.lower():
            section_score += 25
    
    embedding = model.encode([resume_text])[0].reshape(1, -1)
    quality_score = cosine_similarity(embedding, embedding)[0][0] * 100
    
    base_score = (length_score * 0.3) + (section_score * 0.4) + (quality_score * 0.3)
    
    if word_count > 300:
        base_score += 10
    if 'education' in resume_text.lower() and 'experience' in resume_text.lower():
        base_score += 15
    
    base_score = min(base_score, 100)
    
    if job_description:
        job_embedding = model.encode([job_description])[0].reshape(1, -1)
        job_similarity = cosine_similarity(embedding, job_embedding)[0][0] * 100
        job_score = (base_score * 0.5) + (job_similarity * 0.5)
        return min(job_score, 100), base_score
    
    return base_score, None
@login_required
@login_required
def analyze_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    
    if Application.objects.filter(user=request.user, job=job).exists():
        return render(request, 'analyzer/upload.html', {
            'form': ResumeUploadForm(),
            'job': job,
            'error': 'You have already applied for this job. You can only apply once.'
        })

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            file_path = os.path.join(settings.MEDIA_ROOT, 'temp', resume_file.name)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)
            
            if resume_file.name.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif resume_file.name.lower().endswith('.docx'):
                text = extract_text_from_docx(file_path)
            else:
                os.remove(file_path)
                return render(request, 'analyzer/upload.html', {
                    'form': form,
                    'job': job,
                    'error': 'Unsupported file format. Please upload PDF or DOCX.'
                })
            
            job_description = f"{job.job_title} {job.job_description} {job.keywords}"
            job_score, general_score = calculate_ats_score(text, job_description)
            
            
            info = extract_info_from_resume(text)
           
            
            resume_shortlist = Resume_shortlist(
                job=job,
                file=resume_file,
                name=info['name'],
                email=info['email'],
                phone=info['phone'],
                ats_score=job_score,
                upload_date=timezone.now()
            )
            resume_shortlist.save()
            
            
            application = Application(
                user=request.user,
                job=job,
                job_role=job.job_title,
                description=f"ATS Score: {job_score}",
                resume_file=resume_file,
                overall_score=job_score,
                status='rejected' if job_score < 70 else 'accepted'
            )
            application.save()
            
            os.remove(file_path)
            return render(request, 'analyzer/results.html', {
                'score': round(job_score, 2),
                'general_score': round(general_score, 2) if general_score else None,
                'resume': resume_shortlist,
                'application': application,
                'job': job
            })
    else:
        form = ResumeUploadForm()

    return render(request, 'analyzer/upload.html', {
        'form': form,
        'job': job
    })


from django.utils import timezone

@login_required
def home(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            file_path = os.path.join(settings.MEDIA_ROOT, 'temp', resume_file.name)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)
            
            if resume_file.name.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif resume_file.name.lower().endswith('.docx'):
                text = extract_text_from_docx(file_path)
            else:
                os.remove(file_path)
                return render(request, 'analyzer/home.html', {
                    'form': form,
                    'error': 'Unsupported file format. Please upload PDF or DOCX.'
                })
            
            general_score, _ = calculate_ats_score(text)
            
            
            info = extract_info_from_resume(text)
            status = 'accepted' if general_score >= 70 else 'rejected'
            
            generic_job, created = Job.objects.get_or_create(
                job_title="Generic Analysis Job",
                defaults={
                    'user': request.user,
                    'company_name': "Generic Company",
                    'location': "Not specified",
                    'job_type': "full_time",
                    'job_description': "Generic job for resume analysis",
                    'keywords': "analysis,generic,resume"
                }
            )
            
            
            resume_shortlist = Resume_shortlist(
                job=generic_job,
                file=resume_file,
                name=info['name'],
                email=info['email'],
                phone=info['phone'],
                ats_score=general_score,
                upload_date=timezone.now()
            )
            resume_shortlist.save()
            
            
            application = Application(
                user=request.user,
                job=generic_job,
                job_role="Generic Analysis",
                description=f"Generic resume analysis. ATS Score: {general_score}",
                resume_file=resume_file,
                overall_score=general_score,
                status='pending' if general_score < 70 else 'accepted'
            )
            application.save()
            
            os.remove(file_path)
            return render(request, 'analyzer/results.html', {
                'score': round(general_score, 2),
                'resume': resume_shortlist,
                'application': application
            })
    else:
        form = ResumeUploadForm()
    
    return render(request, 'analyzer/home.html', {'form': form})

import re

def extract_info_from_resume(text):
    
    name = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', text)
    
    return {
        'name': name.group(0) if name else "Unknown",
        'email': email.group(0) if email else "",
        'phone': phone.group(0) if phone else ""
    }