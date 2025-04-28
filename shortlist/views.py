from django.shortcuts import render
import os
import re
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .forms import ResumeShortlistForm
from .models import Resume_shortlist,ApplicationShortlist
from HR.models import Job
from docx import Document
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')


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

def extract_info_from_resume(text):
    
    name = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', text)
    
    return {
        'name': name.group(0) if name else "Unknown",
        'email': email.group(0) if email else "",
        'phone': phone.group(0) if phone else ""
    }

def preprocess_text(text):
    """Clean and normalize text for better matching"""
    import re
    
    text = text.lower()
    
    text = re.sub(r"[^a-zA-Z0-9'\s]", ' ', text)
   
    text = ' '.join(text.split())
    return text

def normalize_keyword_score(resume_text, keywords):
    """Calculate keyword match score normalized to 0-100 scale"""
    if not keywords.strip():
        return 0
    
    keywords_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
    resume_words = set(preprocess_text(resume_text).split())
    
    matched_keywords = [kw for kw in keywords_list if kw in resume_words]
    match_percentage = (len(matched_keywords) / len(keywords_list)) * 100 if keywords_list else 0
    return min(match_percentage * 1, 100)  
  
  
def calculate_similarity(resume_text, keywords):
    """Calculate semantic similarity score with boosting"""
    resume_text_clean = preprocess_text(resume_text)
    keywords_clean = ' '.join([k.strip() for k in keywords.split(',') if k.strip()])
    
    if not keywords_clean:
        return 0
    
    
    resume_embedding = model.encode([resume_text_clean])[0].reshape(1, -1)
    keywords_embedding = model.encode([keywords_clean])[0].reshape(1, -1)
    
    
    similarity = cosine_similarity(resume_embedding, keywords_embedding)[0][0]
    boosted_similarity = min(similarity * 1.3, 1.0)  
    return float(boosted_similarity * 100)  


def ats_score(resume_text, job_desc):
    """Calculate ATS score ensuring single float return value"""
    cosine = calculate_similarity(resume_text, job_desc)
    keyword = normalize_keyword_score(resume_text, job_desc)

    
    base_score = (cosine * 0.6) + (keyword * 0.4)

    
    if base_score > 10:
        base_score += 15
    if base_score > 30:
        base_score += 10
    if base_score > 50:
        base_score += 10
    if base_score > 70:
        base_score += 15

    
    final_score = float(min(base_score, 100))
    return round(final_score, 2)
  
  
def home(request):
    if request.method == 'POST':
        form = ResumeShortlistForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.cleaned_data['job']
            keywords = form.cleaned_data['keywords']
            resume_files = request.FILES.getlist('resumes')
            
            resumes_data = []
            for resume_file in resume_files:
                
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
                    continue
                
                
                info = extract_info_from_resume(text)
                score = ats_score(text, keywords)
                
                
                status = 'accepted' if score >= 70 else 'rejected'
                
               
                resume = Resume_shortlist(
                    job=job,
                    file=resume_file,
                    name=info['name'],
                    email=info['email'],
                    phone=info['phone'],
                    ats_score=float(score)
                )
                resume.save()
                
                
                application = ApplicationShortlist(
                    user=request.user,  
                    job=job,
                    job_role=job.job_title,  
                    description=f"Automated application with ATS score: {score}",
                    resume_file=resume_file,
                    overall_score=float(score),
                    status=status
                )
                application.save()
                
                resumes_data.append({
                    'name': info['name'],
                    'email': info['email'],
                    'score': float(score),
                    'file': resume.file.url,
                    'status': status
                })
                
                os.remove(file_path)
            
            sorted_resumes = sorted(resumes_data, key=lambda x: x['score'], reverse=True)
            request.session['resumes_data'] = sorted_resumes
            request.session['job_title'] = job.job_title
            request.session['keywords'] = keywords
            
            return redirect('results')
    else:
        form = ResumeShortlistForm()
    
    return render(request, 'shortlist/home.html', {'form': form})

def results(request):
    resumes_data = request.session.get('resumes_data', [])
    job_title = request.session.get('job_title', '')
    keywords = request.session.get('keywords', '')
    
    
    applications = ApplicationShortlist.objects.filter(job__job_title=job_title).order_by('-overall_score')
    
    context = {
        'resumes': resumes_data,  
        'applications': applications, 
        'job_title': job_title,
        'keywords': keywords
    }
    
    return render(request, 'shortlist/results.html', context)
def get_job_keywords(request):
    job_id = request.GET.get('job_id')
    try:
        job = Job.objects.get(pk=job_id)
        return JsonResponse({'keywords': str(job.keywords)})  
    except Job.DoesNotExist:
        return JsonResponse({'keywords': ''})