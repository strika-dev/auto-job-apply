"""
REST API for job application tracking
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from pathlib import Path

from .database import db
from .openai_service import ai_service
from .job_scraper import job_scraper
from .email_notifier import email_notifier
from .settings import settings_manager
from .config import get_config

config = get_config()

# Create Blueprint
api = Blueprint("api", __name__, url_prefix="/api")


# ============== Application Endpoints ==============

@api.route("/applications", methods=["GET"])
def get_applications():
    """Get all applications with optional filters"""
    status = request.args.get("status")
    company = request.args.get("company")
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    applications = db.get_all_applications(
        status=status, company=company, limit=limit, offset=offset
    )
    
    return jsonify({
        "success": True,
        "count": len(applications),
        "data": [app.to_dict() for app in applications]
    })


@api.route("/applications/<int:app_id>", methods=["GET"])
def get_application(app_id: int):
    """Get a single application by ID"""
    application = db.get_application(app_id)
    
    if not application:
        return jsonify({"success": False, "error": "Application not found"}), 404
    
    return jsonify({"success": True, "data": application.to_dict()})


@api.route("/applications", methods=["POST"])
def create_application():
    """Create a new application"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    for field in ["company", "position"]:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing: {field}"}), 400
    
    data.setdefault("status", "pending")
    application = db.create_application(data)
    
    # Send notification
    email_notifier.notify_application_created(
        company=data["company"],
        position=data["position"],
        job_url=data.get("job_url")
    )
    
    return jsonify({
        "success": True,
        "message": "Application created",
        "data": application.to_dict()
    }), 201


@api.route("/applications/<int:app_id>", methods=["PUT"])
def update_application(app_id: int):
    """Update an application"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    current_app = db.get_application(app_id)
    if not current_app:
        return jsonify({"success": False, "error": "Application not found"}), 404
    
    old_status = current_app.status
    
    # Handle status changes
    if "status" in data and data["status"] != old_status:
        if data["status"] not in config.STATUS_OPTIONS:
            return jsonify({"success": False, "error": f"Invalid status"}), 400
        
        if data["status"] == "applied" and not current_app.applied_date:
            data["applied_date"] = datetime.utcnow()
        
        if data["status"] in ["interview_scheduled", "offer_received", "rejected"]:
            data["response_date"] = datetime.utcnow()
    
    application = db.update_application(app_id, data)
    
    # Notify on status change
    if "status" in data and data["status"] != old_status:
        email_notifier.notify_status_change(
            company=application.company,
            position=application.position,
            old_status=old_status,
            new_status=data["status"]
        )
    
    return jsonify({
        "success": True,
        "message": "Application updated",
        "data": application.to_dict()
    })


@api.route("/applications/<int:app_id>", methods=["DELETE"])
def delete_application(app_id: int):
    """Delete an application"""
    success = db.delete_application(app_id)
    
    if not success:
        return jsonify({"success": False, "error": "Application not found"}), 404
    
    return jsonify({"success": True, "message": "Application deleted"})


@api.route("/applications/search", methods=["GET"])
def search_applications():
    """Search applications"""
    query = request.args.get("q", "")
    
    if not query:
        return jsonify({"success": False, "error": "Search query required"}), 400
    
    applications = db.search_applications(query)
    
    return jsonify({
        "success": True,
        "count": len(applications),
        "data": [app.to_dict() for app in applications]
    })


# ============== Statistics ==============

@api.route("/stats", methods=["GET"])
def get_statistics():
    """Get application statistics"""
    stats = db.get_statistics()
    return jsonify({"success": True, "data": stats})


# ============== AI Customization ==============

@api.route("/customize", methods=["POST"])
def customize_documents():
    """Generate customized resume and cover letter"""
    data = request.get_json()
    
    for field in ["job_description", "company", "position"]:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing: {field}"}), 400
    
    # Get resume from settings
    settings = settings_manager.load()
    base_resume = settings.base_resume
    
    if not base_resume:
        return jsonify({
            "success": False,
            "error": "No resume configured. Please add your resume in Settings."
        }), 400
    
    # Check OpenAI key
    if not settings.openai_api_key:
        return jsonify({
            "success": False,
            "error": "OpenAI API key not configured. Please add it in Settings."
        }), 400
    
    resume_result = ai_service.customize_resume(
        base_resume=base_resume,
        job_description=data["job_description"],
        company=data["company"],
        position=data["position"]
    )
    
    cover_letter_result = ai_service.generate_cover_letter(
        base_resume=base_resume,
        job_description=data["job_description"],
        company=data["company"],
        position=data["position"],
        tone=data.get("tone", "professional")
    )
    
    return jsonify({
        "success": True,
        "data": {
            "resume": resume_result,
            "cover_letter": cover_letter_result
        }
    })


@api.route("/analyze-job", methods=["POST"])
def analyze_job():
    """Analyze a job posting"""
    data = request.get_json()
    
    if "job_description" not in data:
        return jsonify({"success": False, "error": "job_description required"}), 400
    
    result = ai_service.analyze_job_posting(data["job_description"])
    return jsonify(result)


@api.route("/interview-prep", methods=["POST"])
def interview_prep():
    """Generate interview preparation materials"""
    data = request.get_json()
    
    for field in ["job_description", "company", "position"]:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing: {field}"}), 400
    
    result = ai_service.generate_interview_prep(
        job_description=data["job_description"],
        company=data["company"],
        position=data["position"]
    )
    
    return jsonify(result)


# ============== Job Scraping ==============

@api.route("/scrape", methods=["POST"])
def scrape_jobs():
    """Scrape jobs from platforms"""
    data = request.get_json()
    
    if "query" not in data:
        return jsonify({"success": False, "error": "query required"}), 400
    
    results = job_scraper.search_all(
        query=data["query"],
        location=data.get("location", ""),
        platforms=data.get("platforms"),
        num_jobs_per_platform=data.get("num_jobs", 25)
    )
    
    formatted_results = {}
    total_jobs = 0
    
    for platform, jobs in results.items():
        formatted_results[platform] = [
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "platform": job.platform
            }
            for job in jobs
        ]
        total_jobs += len(jobs)
    
    return jsonify({
        "success": True,
        "total_jobs": total_jobs,
        "data": formatted_results
    })


@api.route("/job-details", methods=["POST"])
def get_job_details():
    """Get full details of a job posting"""
    data = request.get_json()
    
    if "url" not in data:
        return jsonify({"success": False, "error": "url required"}), 400
    
    details = job_scraper.get_job_details(data["url"])
    
    if not details:
        return jsonify({"success": False, "error": "Failed to fetch details"}), 400
    
    return jsonify({"success": True, "data": details})


# ============== Settings Endpoints ==============

@api.route("/settings", methods=["GET"])
def get_settings():
    """Get user settings (sensitive data masked)"""
    settings = settings_manager.load()
    return jsonify({
        "success": True,
        "data": settings.to_dict(include_sensitive=False)
    })


@api.route("/settings", methods=["PUT"])
def update_settings():
    """Update user settings"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    settings = settings_manager.update(data)
    
    return jsonify({
        "success": True,
        "message": "Settings updated",
        "data": settings.to_dict(include_sensitive=False)
    })


@api.route("/settings/resume", methods=["GET"])
def get_resume():
    """Get the base resume text"""
    resume = settings_manager.get_resume()
    return jsonify({"success": True, "data": {"resume": resume}})


@api.route("/settings/resume", methods=["PUT"])
def update_resume():
    """Update the base resume"""
    data = request.get_json()
    
    if "resume" not in data:
        return jsonify({"success": False, "error": "resume required"}), 400
    
    settings_manager.update({"base_resume": data["resume"]})
    
    return jsonify({"success": True, "message": "Resume updated"})


@api.route("/settings/test-email", methods=["POST"])
def test_email():
    """Test email SMTP connection"""
    result = settings_manager.test_email()
    return jsonify(result)


@api.route("/settings/test-openai", methods=["POST"])
def test_openai():
    """Test OpenAI API connection"""
    result = settings_manager.test_openai()
    return jsonify(result)


# ============== Health Check ==============

@api.route("/health", methods=["GET"])
def health_check():
    """API health check"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })
