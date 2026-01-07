"""
Database models and operations for job application tracking
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import get_config

config = get_config()
Base = declarative_base()


class Application(Base):
    """Job application model"""
    
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    job_url = Column(String(500))
    job_description = Column(Text)
    location = Column(String(255))
    salary_range = Column(String(100))
    
    # Application details
    status = Column(String(50), default="pending")
    applied_date = Column(DateTime)
    response_date = Column(DateTime)
    
    # Customized documents
    custom_resume = Column(Text)
    custom_cover_letter = Column(Text)
    
    # Tracking
    platform = Column(String(100))  # LinkedIn, Indeed, etc.
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    notes = Column(Text)
    
    # AI Analysis
    match_score = Column(Float)  # 0-100 compatibility score
    keywords_matched = Column(Text)  # JSON list of matched keywords
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "job_url": self.job_url,
            "job_description": self.job_description,
            "location": self.location,
            "salary_range": self.salary_range,
            "status": self.status,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "response_date": self.response_date.isoformat() if self.response_date else None,
            "custom_resume": self.custom_resume,
            "custom_cover_letter": self.custom_cover_letter,
            "platform": self.platform,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "notes": self.notes,
            "match_score": self.match_score,
            "keywords_matched": self.keywords_matched,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_favorite": self.is_favorite
        }


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
        print("✅ Database initialized successfully!")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # CRUD Operations
    def create_application(self, data: Dict[str, Any]) -> Application:
        """Create a new application"""
        session = self.get_session()
        try:
            application = Application(**data)
            session.add(application)
            session.commit()
            session.refresh(application)
            return application
        finally:
            session.close()
    
    def get_application(self, app_id: int) -> Optional[Application]:
        """Get application by ID"""
        session = self.get_session()
        try:
            return session.query(Application).filter(Application.id == app_id).first()
        finally:
            session.close()
    
    def get_all_applications(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Application]:
        """Get all applications with optional filters"""
        session = self.get_session()
        try:
            query = session.query(Application)
            
            if status:
                query = query.filter(Application.status == status)
            if company:
                query = query.filter(Application.company.ilike(f"%{company}%"))
            
            return query.order_by(Application.created_at.desc()).offset(offset).limit(limit).all()
        finally:
            session.close()
    
    def update_application(self, app_id: int, data: Dict[str, Any]) -> Optional[Application]:
        """Update an application"""
        session = self.get_session()
        try:
            application = session.query(Application).filter(Application.id == app_id).first()
            if application:
                for key, value in data.items():
                    if hasattr(application, key):
                        setattr(application, key, value)
                session.commit()
                session.refresh(application)
            return application
        finally:
            session.close()
    
    def delete_application(self, app_id: int) -> bool:
        """Delete an application"""
        session = self.get_session()
        try:
            application = session.query(Application).filter(Application.id == app_id).first()
            if application:
                session.delete(application)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get application statistics"""
        session = self.get_session()
        try:
            total = session.query(Application).count()
            
            stats = {
                "total_applications": total,
                "by_status": {},
                "by_platform": {},
                "response_rate": 0,
                "average_match_score": 0
            }
            
            # Count by status
            for status in config.STATUS_OPTIONS:
                count = session.query(Application).filter(Application.status == status).count()
                stats["by_status"][status] = count
            
            # Count by platform
            platforms = session.query(Application.platform).distinct().all()
            for (platform,) in platforms:
                if platform:
                    count = session.query(Application).filter(Application.platform == platform).count()
                    stats["by_platform"][platform] = count
            
            # Calculate response rate
            responded = session.query(Application).filter(
                Application.status.in_(["interview_scheduled", "interviewed", "offer_received", "rejected"])
            ).count()
            stats["response_rate"] = round((responded / total * 100), 2) if total > 0 else 0
            
            # Average match score
            from sqlalchemy import func
            avg_score = session.query(func.avg(Application.match_score)).scalar()
            stats["average_match_score"] = round(avg_score, 2) if avg_score else 0
            
            return stats
        finally:
            session.close()
    
    def search_applications(self, query: str) -> List[Application]:
        """Search applications by company, position, or notes"""
        session = self.get_session()
        try:
            return session.query(Application).filter(
                (Application.company.ilike(f"%{query}%")) |
                (Application.position.ilike(f"%{query}%")) |
                (Application.notes.ilike(f"%{query}%"))
            ).all()
        finally:
            session.close()


# Global database manager instance
db = DatabaseManager()


def init_db():
    """Initialize the database"""
    db.init_db()


if __name__ == "__main__":
    init_db()
