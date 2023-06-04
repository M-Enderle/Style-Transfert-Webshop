""" This file is used to run the fastAPI using uvicorn when the package is run as a module. """

import sys
from pathlib import Path

root = Path(__file__).parent

if __name__ == "__main__":
    sys.argv = [
        "uvicorn",
        "style_ai.api:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]
    sys.path.append(str(root))
    sys.exit(__import__("uvicorn").main())
