import re

def calculate_ats_score(job_requirements, resume_description):
    job_keywords = set(re.findall(r'\b\w+\b', job_requirements.lower()))
    resume_keywords = set(re.findall(r'\b\w+\b', resume_description.lower()))

    if not job_keywords:
        return 0.0

    matched_keywords = job_keywords & resume_keywords
    score = (len(matched_keywords) / len(job_keywords)) * 100
    return round(score, 2)