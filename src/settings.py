"""
Settings management for user configuration
"""

import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict, field

DATA_DIR = Path(__file__).parent.parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"
RESUME_FILE = DATA_DIR / "base_resume.txt"


@dataclass
class UserSettings:
    """User configuration settings"""
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_email: str = ""
    smtp_password: str = ""
    notification_email: str = ""
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # User profile
    full_name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    # Job search preferences
    target_positions: str = ""
    target_locations: str = ""
    min_salary: str = ""
    remote_only: bool = False
    
    # Notification preferences
    email_notifications: bool = True
    daily_summary: bool = False
    
    # Resume stored as text
    base_resume: str = ""
    
    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """Convert to dictionary, optionally masking sensitive data"""
        data = asdict(self)
        
        if not include_sensitive:
            # Mask sensitive fields but indicate if they're set
            sensitive = ['smtp_password', 'openai_api_key']
            for field_name in sensitive:
                if data.get(field_name):
                    data[f'{field_name}_set'] = True
                    data[field_name] = ''
                else:
                    data[f'{field_name}_set'] = False
        
        return data


class SettingsManager:
    """Manage user settings persistence"""
    
    def __init__(self):
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> UserSettings:
        """Load settings from file"""
        try:
            if SETTINGS_FILE.exists():
                data = json.loads(SETTINGS_FILE.read_text())
                # Handle legacy resume file
                if not data.get('base_resume') and RESUME_FILE.exists():
                    data['base_resume'] = RESUME_FILE.read_text()
                return UserSettings(**{k: v for k, v in data.items() if hasattr(UserSettings, k)})
        except Exception as e:
            print(f"Error loading settings: {e}")
        return UserSettings()
    
    def save(self, settings: UserSettings) -> bool:
        """Save settings to file"""
        try:
            SETTINGS_FILE.write_text(json.dumps(asdict(settings), indent=2))
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def update(self, data: Dict[str, Any]) -> UserSettings:
        """Update specific settings fields"""
        settings = self.load()
        
        for key, value in data.items():
            # Skip masked password fields
            if key in ['smtp_password', 'openai_api_key'] and value == '':
                continue
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        self.save(settings)
        return settings
    
    def get_resume(self) -> str:
        """Get resume text"""
        settings = self.load()
        return settings.base_resume
    
    def test_email(self) -> Dict[str, Any]:
        """Test SMTP connection"""
        import smtplib
        settings = self.load()
        
        if not settings.smtp_email or not settings.smtp_password:
            return {"success": False, "error": "Email not configured"}
        
        try:
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(settings.smtp_email, settings.smtp_password)
            return {"success": True, "message": "✅ Connection successful!"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_openai(self) -> Dict[str, Any]:
        """Test OpenAI API"""
        settings = self.load()
        
        if not settings.openai_api_key:
            return {"success": False, "error": "API key not configured"}
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return {"success": True, "message": "✅ OpenAI connected!"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
settings_manager = SettingsManager()
