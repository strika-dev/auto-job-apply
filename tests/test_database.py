"""
Unit tests for database operations
"""

import pytest
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager, Application, Base


class TestDatabaseManager:
    """Test suite for DatabaseManager"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test database"""
        # Use temporary database for testing
        db_path = tmp_path / "test_applications.db"
        os.environ["DATABASE_PATH"] = str(db_path)
        
        self.db = DatabaseManager()
        self.db.engine = self.db.engine.execution_options(echo=False)
        self.db.init_db()
        
        yield
        
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    def test_create_application(self):
        """Test creating a new application"""
        data = {
            "company": "Google",
            "position": "Software Engineer",
            "job_url": "https://careers.google.com/jobs/123",
            "location": "Mountain View, CA",
            "status": "pending"
        }
        
        app = self.db.create_application(data)
        
        assert app.id is not None
        assert app.company == "Google"
        assert app.position == "Software Engineer"
        assert app.status == "pending"
    
    def test_get_application(self):
        """Test retrieving an application by ID"""
        # Create application first
        data = {
            "company": "Meta",
            "position": "Data Scientist"
        }
        created = self.db.create_application(data)
        
        # Retrieve it
        app = self.db.get_application(created.id)
        
        assert app is not None
        assert app.company == "Meta"
        assert app.position == "Data Scientist"
    
    def test_get_application_not_found(self):
        """Test retrieving non-existent application"""
        app = self.db.get_application(99999)
        assert app is None
    
    def test_get_all_applications(self):
        """Test retrieving all applications"""
        # Create multiple applications
        companies = ["Apple", "Amazon", "Netflix"]
        for company in companies:
            self.db.create_application({
                "company": company,
                "position": "Engineer"
            })
        
        apps = self.db.get_all_applications()
        
        assert len(apps) == 3
    
    def test_get_applications_with_filter(self):
        """Test filtering applications by status"""
        # Create applications with different statuses
        self.db.create_application({
            "company": "Company A",
            "position": "Role A",
            "status": "applied"
        })
        self.db.create_application({
            "company": "Company B",
            "position": "Role B",
            "status": "pending"
        })
        self.db.create_application({
            "company": "Company C",
            "position": "Role C",
            "status": "applied"
        })
        
        applied_apps = self.db.get_all_applications(status="applied")
        
        assert len(applied_apps) == 2
    
    def test_update_application(self):
        """Test updating an application"""
        # Create application
        app = self.db.create_application({
            "company": "Startup",
            "position": "Developer",
            "status": "pending"
        })
        
        # Update it
        updated = self.db.update_application(app.id, {
            "status": "applied",
            "notes": "Applied via website"
        })
        
        assert updated.status == "applied"
        assert updated.notes == "Applied via website"
    
    def test_delete_application(self):
        """Test deleting an application"""
        # Create application
        app = self.db.create_application({
            "company": "DeleteMe Inc",
            "position": "Temp"
        })
        
        # Delete it
        result = self.db.delete_application(app.id)
        
        assert result is True
        
        # Verify it's gone
        deleted = self.db.get_application(app.id)
        assert deleted is None
    
    def test_delete_nonexistent_application(self):
        """Test deleting non-existent application"""
        result = self.db.delete_application(99999)
        assert result is False
    
    def test_search_applications(self):
        """Test searching applications"""
        # Create applications
        self.db.create_application({
            "company": "Tech Corp",
            "position": "Python Developer",
            "notes": "Great opportunity"
        })
        self.db.create_application({
            "company": "Data Inc",
            "position": "Java Developer"
        })
        
        # Search by company
        results = self.db.search_applications("Tech")
        assert len(results) == 1
        
        # Search by position
        results = self.db.search_applications("Python")
        assert len(results) == 1
    
    def test_get_statistics(self):
        """Test getting application statistics"""
        # Create applications with various statuses
        statuses = ["pending", "applied", "applied", "interview_scheduled", "rejected"]
        for i, status in enumerate(statuses):
            self.db.create_application({
                "company": f"Company {i}",
                "position": f"Role {i}",
                "status": status,
                "match_score": 75.0 + i
            })
        
        stats = self.db.get_statistics()
        
        assert stats["total_applications"] == 5
        assert stats["by_status"]["applied"] == 2
        assert stats["by_status"]["pending"] == 1
        assert stats["response_rate"] > 0
    
    def test_application_to_dict(self):
        """Test application serialization"""
        app = self.db.create_application({
            "company": "Serialize Corp",
            "position": "Data Engineer",
            "job_url": "https://example.com/job",
            "match_score": 85.5
        })
        
        data = app.to_dict()
        
        assert isinstance(data, dict)
        assert data["company"] == "Serialize Corp"
        assert data["match_score"] == 85.5
        assert "created_at" in data


class TestApplicationModel:
    """Test suite for Application model"""
    
    def test_model_defaults(self):
        """Test default values"""
        app = Application(
            company="Test",
            position="Tester"
        )
        
        assert app.status is None or app.status == "pending"
        assert app.is_favorite is None or app.is_favorite is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
