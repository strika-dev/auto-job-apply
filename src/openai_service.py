"""
OpenAI integration for customizing resumes and cover letters
"""

import json
from typing import Dict, Any


class OpenAIService:
    """Service for AI-powered document customization"""
    
    def __init__(self):
        self._client = None
    
    def _get_client(self):
        """Lazy load OpenAI client with current API key from settings"""
        from .settings import settings_manager
        
        settings = settings_manager.load()
        api_key = settings.openai_api_key
        
        if not api_key:
            raise ValueError("OpenAI API key not configured. Please add it in Settings.")
        
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    
    def customize_resume(
        self,
        base_resume: str,
        job_description: str,
        company: str,
        position: str
    ) -> Dict[str, Any]:
        """
        Customize resume based on job description
        """
        prompt = f"""You are an expert resume writer and career coach. 
Analyze the following job description and customize the resume to better match the position.

COMPANY: {company}
POSITION: {position}

JOB DESCRIPTION:
{job_description}

CURRENT RESUME:
{base_resume}

Please provide:
1. A customized version of the resume that:
   - Highlights relevant skills and experience
   - Uses keywords from the job description
   - Maintains truthfulness (don't add fake experience)
   - Optimizes for ATS (Applicant Tracking Systems)
   - Keeps the same structure but adjusts emphasis

2. A match score (0-100) based on how well the candidate fits

3. Key keywords from the job description that match the resume

4. Suggestions for improvement

Respond in JSON format:
{{
    "customized_resume": "...",
    "match_score": 85,
    "matched_keywords": ["Python", "API", "..."],
    "missing_keywords": ["Kubernetes", "..."],
    "suggestions": ["...", "..."]
}}"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer. Always respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            return {"success": True, "data": result}
            
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Failed to parse AI response: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_cover_letter(
        self,
        base_resume: str,
        job_description: str,
        company: str,
        position: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a customized cover letter
        """
        prompt = f"""You are an expert cover letter writer.
Create a compelling, personalized cover letter for the following position.

COMPANY: {company}
POSITION: {position}
TONE: {tone}

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{base_resume}

Requirements for the cover letter:
1. Be specific about why this company and role
2. Highlight 2-3 most relevant achievements from the resume
3. Show enthusiasm without being generic
4. Keep it concise (3-4 paragraphs)
5. Include a strong opening hook
6. End with a clear call to action
7. Don't repeat the resume - complement it

Respond in JSON format:
{{
    "cover_letter": "...",
    "key_points_highlighted": ["...", "..."],
    "personalization_elements": ["...", "..."]
}}"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer. Always respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            return {"success": True, "data": result}
            
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Failed to parse AI response: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_job_posting(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job posting to extract key information
        """
        prompt = f"""Analyze the following job posting and extract key information.

JOB POSTING:
{job_description}

Extract and return in JSON format:
{{
    "required_skills": ["...", "..."],
    "preferred_skills": ["...", "..."],
    "experience_years": "X-Y years",
    "education_requirements": "...",
    "key_responsibilities": ["...", "..."],
    "company_culture_hints": ["...", "..."],
    "red_flags": ["...", "..."],
    "application_tips": ["...", "..."]
}}"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a job market analyst. Always respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            return {"success": True, "data": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_interview_prep(
        self,
        job_description: str,
        company: str,
        position: str
    ) -> Dict[str, Any]:
        """
        Generate interview preparation materials
        """
        prompt = f"""Generate interview preparation materials for:

COMPANY: {company}
POSITION: {position}

JOB DESCRIPTION:
{job_description}

Provide in JSON format:
{{
    "likely_questions": [
        {{
            "question": "...",
            "type": "behavioral/technical/situational",
            "tips": "...",
            "sample_answer_structure": "..."
        }}
    ],
    "questions_to_ask": ["...", "..."],
    "company_research_points": ["...", "..."],
    "technical_topics_to_review": ["...", "..."]
}}"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interview coach. Always respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            return {"success": True, "data": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global service instance
ai_service = OpenAIService()
