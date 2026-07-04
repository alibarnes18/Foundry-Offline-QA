import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ingest import ingest_all
ingest_all()