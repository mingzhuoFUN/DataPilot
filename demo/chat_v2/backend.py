import uvicorn

from backend_app.app import app
from backend_app.settings import settings


if __name__ == "__main__":
    print("Starting DataPilot backend...")
    print(f"API: http://localhost:{settings.backend_port}")
    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port)
