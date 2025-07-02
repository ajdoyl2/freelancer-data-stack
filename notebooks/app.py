"""
Symlink redirect to the main Streamlit application
=================================================

This file provides backward compatibility for the command:
`streamlit run notebooks/app.py`

The actual Streamlit application is located at:
viz/streamlit/app.py
"""

import os
import sys

# Add the streamlit directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "viz", "streamlit"))

# Import and run the main app
from app import *

# This allows `streamlit run notebooks/app.py` to work correctly
