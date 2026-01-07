"""
Email notification service for application updates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .config import get_config

config = get_config()


class EmailNotifier:
    """Email notification service"""
    
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.email_address = config.EMAIL_ADDRESS
        self.email_password = config.EMAIL_PASSWORD
        self.notification_email = config.NOTIFICATION_EMAIL or config.EMAIL_ADDRESS
        
        # Load email template
        self.template_path = Path(__file__).parent.parent / "templates" / "email_template.html"
    
    def _get_template(self) -> str:
        """Load email template"""
        if self.template_path.exists():
            return self.template_path.read_text()
        return self._default_template()
    
    def _default_template(self) -> str:
        """Default email template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0; }
        .footer { background: #1e293b; color: #94a3b8; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }
        .status { display: inline-block; padding: 5px 12px; border-radius: 20px; font-weight: bold; }
        .status-applied { background: #dbeafe; color: #1d4ed8; }
        .status-interview { background: #dcfce7; color: #15803d; }
        .status-rejected { background: #fee2e2; color: #dc2626; }
        .status-offer { background: #fef3c7; color: #d97706; }
        .details { background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .details-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
        .details-row:last-child { border-bottom: none; }
        .btn { display: inline-block; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Auto Job Apply</h1>
            <p>Application Update</p>
        </div>
        <div class="content">
            <h2>{{title}}</h2>
            <p>{{message}}</p>
            
            <div class="details">
                {{details}}
            </div>
            
            {{action_button}}
        </div>
        <div class="footer">
            <p>Auto Job Apply - Your Automated Job Search Assistant</p>
            <p>{{timestamp}}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _render_template(self, data: Dict[str, Any]) -> str:
        """Render email template with data"""
        template = self._get_template()
        
        for key, value in data.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        
        return template
    
    def send_email(
        self,
        subject: str,
        html_content: str,
        to_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            subject: Email subject
            html_content: HTML content of the email
            to_email: Recipient email (defaults to notification_email)
        
        Returns:
            Dict with success status and message
        """
        to_email = to_email or self.notification_email
        
        if not all([self.email_address, self.email_password, to_email]):
            return {
                "success": False,
                "error": "Email configuration incomplete"
            }
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_address
            msg["To"] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, to_email, msg.as_string())
            
            return {
                "success": True,
                "message": f"Email sent to {to_email}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def notify_application_created(
        self,
        company: str,
        position: str,
        job_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification for new application"""
        details = f"""
        <div class="details-row">
            <span><strong>Company:</strong></span>
            <span>{company}</span>
        </div>
        <div class="details-row">
            <span><strong>Position:</strong></span>
            <span>{position}</span>
        </div>
        """
        
        action_button = ""
        if job_url:
            action_button = f'<a href="{job_url}" class="btn">View Job Posting</a>'
        
        html_content = self._render_template({
            "title": "New Application Created! 📝",
            "message": f"A new job application has been added to your tracker.",
            "details": details,
            "action_button": action_button,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return self.send_email(
            subject=f"🆕 New Application: {position} at {company}",
            html_content=html_content
        )
    
    def notify_status_change(
        self,
        company: str,
        position: str,
        old_status: str,
        new_status: str
    ) -> Dict[str, Any]:
        """Send notification for status change"""
        status_class = {
            "applied": "status-applied",
            "interview_scheduled": "status-interview",
            "interviewed": "status-interview",
            "offer_received": "status-offer",
            "rejected": "status-rejected"
        }.get(new_status, "status-applied")
        
        status_emoji = {
            "applied": "✅",
            "interview_scheduled": "📅",
            "interviewed": "🎯",
            "offer_received": "🎉",
            "rejected": "❌",
            "withdrawn": "🔙"
        }.get(new_status, "📋")
        
        details = f"""
        <div class="details-row">
            <span><strong>Company:</strong></span>
            <span>{company}</span>
        </div>
        <div class="details-row">
            <span><strong>Position:</strong></span>
            <span>{position}</span>
        </div>
        <div class="details-row">
            <span><strong>Previous Status:</strong></span>
            <span>{old_status.replace('_', ' ').title()}</span>
        </div>
        <div class="details-row">
            <span><strong>New Status:</strong></span>
            <span class="status {status_class}">{status_emoji} {new_status.replace('_', ' ').title()}</span>
        </div>
        """
        
        html_content = self._render_template({
            "title": f"Application Status Updated! {status_emoji}",
            "message": f"Your application status has been updated.",
            "details": details,
            "action_button": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return self.send_email(
            subject=f"{status_emoji} Status Update: {position} at {company}",
            html_content=html_content
        )
    
    def notify_daily_summary(
        self,
        stats: Dict[str, Any],
        recent_applications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send daily summary email"""
        details = f"""
        <div class="details-row">
            <span><strong>Total Applications:</strong></span>
            <span>{stats.get('total_applications', 0)}</span>
        </div>
        <div class="details-row">
            <span><strong>Response Rate:</strong></span>
            <span>{stats.get('response_rate', 0)}%</span>
        </div>
        <div class="details-row">
            <span><strong>Pending:</strong></span>
            <span>{stats.get('by_status', {}).get('pending', 0)}</span>
        </div>
        <div class="details-row">
            <span><strong>Interviews Scheduled:</strong></span>
            <span>{stats.get('by_status', {}).get('interview_scheduled', 0)}</span>
        </div>
        """
        
        if recent_applications:
            details += "<h3 style='margin-top: 20px;'>Recent Applications:</h3>"
            for app in recent_applications[:5]:
                details += f"""
                <div class="details-row">
                    <span>{app.get('position', 'N/A')}</span>
                    <span>{app.get('company', 'N/A')}</span>
                </div>
                """
        
        html_content = self._render_template({
            "title": "📊 Daily Application Summary",
            "message": "Here's your job application summary for today.",
            "details": details,
            "action_button": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return self.send_email(
            subject=f"📊 Daily Summary - {stats.get('total_applications', 0)} Applications",
            html_content=html_content
        )
    
    def notify_new_jobs_found(
        self,
        jobs: List[Dict[str, Any]],
        search_query: str
    ) -> Dict[str, Any]:
        """Send notification for new jobs found"""
        details = f"""
        <div class="details-row">
            <span><strong>Search Query:</strong></span>
            <span>{search_query}</span>
        </div>
        <div class="details-row">
            <span><strong>Jobs Found:</strong></span>
            <span>{len(jobs)}</span>
        </div>
        <h3 style='margin-top: 20px;'>Top Matches:</h3>
        """
        
        for job in jobs[:10]:
            details += f"""
            <div class="details-row">
                <span><strong>{job.get('title', 'N/A')}</strong></span>
                <span>{job.get('company', 'N/A')}</span>
            </div>
            """
        
        html_content = self._render_template({
            "title": "🔍 New Jobs Found!",
            "message": f"We found {len(jobs)} new jobs matching your search criteria.",
            "details": details,
            "action_button": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return self.send_email(
            subject=f"🔍 {len(jobs)} New Jobs: {search_query}",
            html_content=html_content
        )


# Global notifier instance
email_notifier = EmailNotifier()
