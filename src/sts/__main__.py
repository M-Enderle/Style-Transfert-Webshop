""" This file is used to run the streamlit app. """

import sys
from pathlib import Path
import streamlit.web.cli as stcli

parent = Path(__file__).parent

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", str(parent / "app" / "home.py")]
    sys.exit(stcli.main())
