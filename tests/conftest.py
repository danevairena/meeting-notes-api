import sys
from pathlib import Path


# add project root to python path for test imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))