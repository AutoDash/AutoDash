import os
import sys
from pathlib import Path

def get_project_root():
    application_path = Path(os.path.abspath(__file__)).parent.absolute() / ".."
    if getattr(sys, 'frozen', False):
    	application_path = Path(sys.executable).parent.absolute()
    return str(application_path)
