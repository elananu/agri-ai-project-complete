"""
conftest.py
Ensures the backend/ directory (parent of tests/) is on sys.path so
test files can import main, recommendations, detection, database, etc.
directly, the same way they import each other in the app itself.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))