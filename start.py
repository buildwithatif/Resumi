"""
Startup script for ResumiV1
Runs the FastAPI application with proper Python path setup
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the main application
if __name__ == "__main__":
    from orchestration.main import app
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting ResumiV1 Server")
    print("=" * 60)
    print(f"📁 Project Root: {project_root}")
    print(f"🌐 Server URL: http://127.0.0.1:8000")
    print(f"📝 Upload your resume to get started!")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
