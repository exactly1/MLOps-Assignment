"""
Simple API runner without auto-reload
"""

import uvicorn
from src.api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
