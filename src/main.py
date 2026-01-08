"""
Auto Job Apply - Main Application Entry Point
"""

from flask import Flask, render_template_string
from flask_cors import CORS

from .config import get_config
from .database import init_db
from .api import api

config = get_config()


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    
    # Enable CORS
    CORS(app)
    
    # Register API blueprint
    app.register_blueprint(api)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Root route - API documentation
    @app.route("/")
    def index():
        return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Job Apply API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .header h1 { font-size: 3rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .card h2 { color: #333; margin-bottom: 20px; font-size: 1.5rem; }
        .endpoint {
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .endpoint:last-child { border-bottom: none; }
        .method {
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8rem;
            margin-right: 15px;
            min-width: 60px;
            text-align: center;
        }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
        .put { background: #fca130; color: white; }
        .delete { background: #f93e3e; color: white; }
        .path { font-family: monospace; color: #333; flex: 1; }
        .desc { color: #666; font-size: 0.9rem; }
        .badge {
            display: inline-block;
            padding: 5px 15px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 5px;
        }
        .stats { display: flex; gap: 20px; flex-wrap: wrap; }
        .stat-item { text-align: center; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Auto Job Apply</h1>
            <p>Intelligent Job Application Automation API</p>
        </div>
        
        <div class="card">
            <h2>📊 Features</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <span class="badge">AI-Powered Customization</span>
                <span class="badge">Multi-Platform Scraping</span>
                <span class="badge">Application Tracking</span>
                <span class="badge">Email Notifications</span>
                <span class="badge">Interview Prep</span>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Application Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/applications</span>
                <span class="desc">List all applications</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/applications/:id</span>
                <span class="desc">Get application details</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/applications</span>
                <span class="desc">Create new application</span>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <span class="path">/api/applications/:id</span>
                <span class="desc">Update application</span>
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span>
                <span class="path">/api/applications/:id</span>
                <span class="desc">Delete application</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/stats</span>
                <span class="desc">Get statistics</span>
            </div>
        </div>
        
        <div class="card">
            <h2>🤖 AI Endpoints</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/customize</span>
                <span class="desc">Generate customized CV & cover letter</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/analyze-job</span>
                <span class="desc">Analyze job posting</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/interview-prep</span>
                <span class="desc">Generate interview prep materials</span>
            </div>
        </div>
        
        <div class="card">
            <h2>🔍 Job Scraping Endpoints</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/scrape</span>
                <span class="desc">Scrape jobs from platforms</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/job-details</span>
                <span class="desc">Get full job details</span>
            </div>
        </div>
        
        <div class="card">
            <h2>🏥 Health</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/health</span>
                <span class="desc">API health check</span>
            </div>
        </div>
    </div>
</body>
</html>
        """)
    
    return app


def main():
    """Run the application"""
    app = create_app()
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🚀 Auto Job Apply API                                  ║
    ║                                                          ║
    ║   Server running at: http://localhost:{config.PORT}             ║
    ║   Debug mode: {config.DEBUG}                                    ║
    ║                                                          ║
    ║   Endpoints:                                             ║
    ║   • GET  /api/applications - List applications           ║
    ║   • POST /api/applications - Create application          ║
    ║   • POST /api/customize    - AI customization            ║
    ║   • POST /api/scrape       - Scrape jobs                 ║
    ║   • GET  /api/stats        - Statistics                  ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)

app = create_app()

if __name__ == "__main__":
    main()
