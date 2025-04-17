import os
import sys
from pathlib import Path

# Add the register-api directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up environment variables if needed
os.environ["ENVIRONMENT"] = "test" 