"""
Symlink redirect to the main Streamlit application
=================================================

This file provides backward compatibility for the command:
`streamlit run notebooks/app.py`

The actual Streamlit application is located at:
viz/streamlit/app.py
"""

import sys
from pathlib import Path

# Add the streamlit directory to the path
streamlit_path = Path(__file__).parent.parent / "viz" / "streamlit"
sys.path.insert(0, str(streamlit_path))

# Import and run the main app
if __name__ == "__main__":
    # Import the main function to avoid star imports
    from app import main
    main()
