# Auto Job Apply

A job application automation system that helps track applications, customize resumes using AI, and scrape job postings from multiple platforms.

## What it does

- **Track applications**: Store and manage all your job applications in one place with status updates, notes, and statistics
  <img width="1896" height="864" alt="image" src="https://github.com/user-attachments/assets/05b34a25-2917-4c2a-afd2-c3169cd00f2f" />

- **AI customization**: Generate tailored resumes and cover letters for each job posting using OpenAI's GPT
<img width="1560" height="856" alt="Capture d’écran 2026-01-06 193434" src="https://github.com/user-attachments/assets/c1850e08-859b-48c9-a9bb-7880b17633b0" />

- **Job scraping**: Search and collect job postings from LinkedIn, Indeed, and Glassdoor
  <img width="1917" height="857" alt="image" src="https://github.com/user-attachments/assets/8feb8136-38ec-41f9-99d1-3971604ee028" />

- **Email notifications**: Get notified when application statuses change

## Project structure

```
auto-job-apply/
├── src/
│   ├── main.py           # Flask app entry point
│   ├── api.py            # REST API endpoints
│   ├── database.py       # SQLite database models
│   ├── settings.py       # User configuration management
│   ├── openai_service.py # AI document generation
│   ├── job_scraper.py    # Job platform scrapers
│   └── email_notifier.py # Email notifications
├── frontend/
│   └── index.html        # React dashboard (single file)
├── data/                 # Database and settings storage
├── tests/
└── templates/
```

## Setup

Requirements: Python 3.9+

```bash
# Clone and enter directory
git clone https://github.com/strika-dev/auto-job-apply.git
cd auto-job-apply

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m src.main
```

The API runs on `http://localhost:5000`. Open `frontend/index.html` in your browser to use the dashboard.

## Configuration

All settings can be configured through the Settings page in the frontend:
<img width="1877" height="846" alt="Capture d’écran 2026-01-06 193313" src="https://github.com/user-attachments/assets/d6651fff-65c7-4e49-9aaa-a60857c8544c" />

- Your resume/CV text
  <img width="1554" height="766" alt="Capture d’écran 2026-01-06 193333" src="https://github.com/user-attachments/assets/541f660a-4a43-4d9d-91f2-3ff663d96e3d" />

- OpenAI API key (get one at platform.openai.com)
- Email settings for notifications (optional)
- Profile information

Settings are stored in `data/settings.json`.

## API endpoints

**Applications**
- `GET /api/applications` - List all applications
- `POST /api/applications` - Create application
- `PUT /api/applications/:id` - Update application
- `DELETE /api/applications/:id` - Delete application
- `GET /api/stats` - Get statistics

**AI**
- `POST /api/customize` - Generate custom resume and cover letter
- `POST /api/analyze-job` - Analyze a job posting

**Jobs**
- `POST /api/scrape` - Search jobs from platforms

**Settings**
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/test-email` - Test email connection
- `POST /api/settings/test-openai` - Test OpenAI connection

## Notes

This tool helps manage the job search process but does not automatically apply to jobs on your behalf. You still need to submit applications manually through each company's website.

The job scraping feature depends on the structure of external websites and may break if those sites change their layout.

## License

MIT
