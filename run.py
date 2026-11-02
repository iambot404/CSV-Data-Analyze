import os
import sys

from app import create_app
from app.config import PORT, DEBUG

app = create_app()

if __name__ == "__main__":
    print(f"[*] Starting SynapseCSV Data Analyzer on http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
