"""
Job scraping module for multiple platforms
"""

import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from .config import get_config

config = get_config()


@dataclass
class JobListing:
    """Standardized job listing data structure"""
    title: str
    company: str
    location: str
    description: str
    url: str
    platform: str
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract


class BaseScraper(ABC):
    """Base class for job scrapers"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.delay = config.SCRAPE_DELAY
    
    @abstractmethod
    def search(self, query: str, location: str, num_jobs: int) -> List[JobListing]:
        """Search for jobs"""
        pass
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make HTTP request with error handling"""
        try:
            time.sleep(self.delay)  # Rate limiting
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None


class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper (public listings only)"""
    
    PLATFORM = "LinkedIn"
    BASE_URL = "https://www.linkedin.com/jobs/search"
    
    def search(self, query: str, location: str = "", num_jobs: int = 25) -> List[JobListing]:
        """
        Search LinkedIn jobs
        Note: This scrapes public job listings only
        """
        jobs = []
        encoded_query = quote_plus(query)
        encoded_location = quote_plus(location)
        
        url = f"{self.BASE_URL}?keywords={encoded_query}&location={encoded_location}&f_TPR=r86400"
        
        soup = self._make_request(url)
        if not soup:
            return jobs
        
        job_cards = soup.find_all("div", class_="base-card")[:num_jobs]
        
        for card in job_cards:
            try:
                title_elem = card.find("h3", class_="base-search-card__title")
                company_elem = card.find("h4", class_="base-search-card__subtitle")
                location_elem = card.find("span", class_="job-search-card__location")
                link_elem = card.find("a", class_="base-card__full-link")
                
                if title_elem and company_elem:
                    job = JobListing(
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip(),
                        location=location_elem.text.strip() if location_elem else "",
                        description="",  # Would need to fetch individual page
                        url=link_elem["href"] if link_elem else "",
                        platform=self.PLATFORM
                    )
                    jobs.append(job)
            except Exception as e:
                print(f"Error parsing LinkedIn job card: {e}")
                continue
        
        return jobs


class IndeedScraper(BaseScraper):
    """Indeed job scraper"""
    
    PLATFORM = "Indeed"
    BASE_URL = "https://www.indeed.com/jobs"
    
    def search(self, query: str, location: str = "", num_jobs: int = 25) -> List[JobListing]:
        """Search Indeed jobs"""
        jobs = []
        encoded_query = quote_plus(query)
        encoded_location = quote_plus(location)
        
        url = f"{self.BASE_URL}?q={encoded_query}&l={encoded_location}&fromage=1"
        
        soup = self._make_request(url)
        if not soup:
            return jobs
        
        job_cards = soup.find_all("div", class_="job_seen_beacon")[:num_jobs]
        
        for card in job_cards:
            try:
                title_elem = card.find("h2", class_="jobTitle")
                company_elem = card.find("span", {"data-testid": "company-name"})
                location_elem = card.find("div", {"data-testid": "text-location"})
                
                # Get job URL
                link_elem = card.find("a", class_="jcs-JobTitle")
                job_url = f"https://www.indeed.com{link_elem['href']}" if link_elem else ""
                
                if title_elem and company_elem:
                    job = JobListing(
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip(),
                        location=location_elem.text.strip() if location_elem else "",
                        description="",
                        url=job_url,
                        platform=self.PLATFORM
                    )
                    jobs.append(job)
            except Exception as e:
                print(f"Error parsing Indeed job card: {e}")
                continue
        
        return jobs


class GlassdoorScraper(BaseScraper):
    """Glassdoor job scraper"""
    
    PLATFORM = "Glassdoor"
    BASE_URL = "https://www.glassdoor.com/Job"
    
    def search(self, query: str, location: str = "", num_jobs: int = 25) -> List[JobListing]:
        """Search Glassdoor jobs"""
        jobs = []
        
        # Glassdoor requires specific URL format
        query_slug = query.lower().replace(" ", "-")
        location_slug = location.lower().replace(" ", "-").replace(",", "") if location else "united-states"
        
        url = f"{self.BASE_URL}/{location_slug}-{query_slug}-jobs-SRCH_IL.0,13_IN1_KO14,31.htm"
        
        soup = self._make_request(url)
        if not soup:
            return jobs
        
        job_cards = soup.find_all("li", class_="react-job-listing")[:num_jobs]
        
        for card in job_cards:
            try:
                title_elem = card.find("a", {"data-test": "job-link"})
                company_elem = card.find("div", class_="employer-name")
                location_elem = card.find("span", class_="loc")
                
                if title_elem:
                    job = JobListing(
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip() if company_elem else "",
                        location=location_elem.text.strip() if location_elem else "",
                        description="",
                        url=f"https://www.glassdoor.com{title_elem['href']}" if title_elem.get('href') else "",
                        platform=self.PLATFORM
                    )
                    jobs.append(job)
            except Exception as e:
                print(f"Error parsing Glassdoor job card: {e}")
                continue
        
        return jobs


class JobScraper:
    """Main job scraping orchestrator"""
    
    def __init__(self):
        self.scrapers = {
            "linkedin": LinkedInScraper(),
            "indeed": IndeedScraper(),
            "glassdoor": GlassdoorScraper()
        }
    
    def search_all(
        self,
        query: str,
        location: str = "",
        platforms: Optional[List[str]] = None,
        num_jobs_per_platform: int = 25
    ) -> Dict[str, List[JobListing]]:
        """
        Search for jobs across multiple platforms
        
        Args:
            query: Job search query
            location: Location filter
            platforms: List of platforms to search (default: all)
            num_jobs_per_platform: Max jobs to fetch per platform
        
        Returns:
            Dict mapping platform names to lists of job listings
        """
        if platforms is None:
            platforms = list(self.scrapers.keys())
        
        results = {}
        
        for platform in platforms:
            if platform.lower() in self.scrapers:
                print(f"Searching {platform}...")
                scraper = self.scrapers[platform.lower()]
                jobs = scraper.search(query, location, num_jobs_per_platform)
                results[platform] = jobs
                print(f"Found {len(jobs)} jobs on {platform}")
        
        return results
    
    def search_single(
        self,
        platform: str,
        query: str,
        location: str = "",
        num_jobs: int = 25
    ) -> List[JobListing]:
        """Search a single platform"""
        if platform.lower() not in self.scrapers:
            raise ValueError(f"Unknown platform: {platform}")
        
        scraper = self.scrapers[platform.lower()]
        return scraper.search(query, location, num_jobs)
    
    def get_job_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full job details from a job URL
        
        Returns:
            Dict with full job description and details
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try to find job description - varies by platform
            description = ""
            
            # Common selectors for job descriptions
            description_selectors = [
                {"class": "description"},
                {"class": "job-description"},
                {"id": "jobDescriptionText"},
                {"class": "jobsearch-jobDescriptionText"},
                {"class": "show-more-less-html__markup"}
            ]
            
            for selector in description_selectors:
                elem = soup.find("div", selector)
                if elem:
                    description = elem.get_text(separator="\n", strip=True)
                    break
            
            return {
                "url": url,
                "description": description,
                "raw_html": str(soup)[:5000]  # First 5000 chars for debugging
            }
            
        except Exception as e:
            print(f"Error fetching job details: {e}")
            return None


# Global scraper instance
job_scraper = JobScraper()


if __name__ == "__main__":
    # Test the scraper
    results = job_scraper.search_all(
        query="Software Engineer",
        location="Montreal",
        num_jobs_per_platform=5
    )
    
    for platform, jobs in results.items():
        print(f"\n=== {platform} ===")
        for job in jobs:
            print(f"  - {job.title} at {job.company}")
