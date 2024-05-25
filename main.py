from core.common_modules.file_tools import get_abs_path
import uvicorn
import os
import sys
import dotenv
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        app="core.server:app",
        reload=True,
        workers=2,
        port=8000,
        host="0.0.0.0"
    )
