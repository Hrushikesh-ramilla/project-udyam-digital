import os
import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of where this script is called from
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Change current working directory to project root so data/ folder and relative paths resolve
os.chdir(PROJECT_ROOT)
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("  PROJECT UDYAM DIGITAL -- ACCEL BUSINESS BACKEND API")
    print(f"  Working Directory: {PROJECT_ROOT}")
    print("  Backend API: http://127.0.0.1:8000")
    print("  API Docs (Swagger UI): http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
