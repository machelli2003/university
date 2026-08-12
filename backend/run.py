import os
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_env = os.getenv("RELOAD", "true").lower()
    reload = reload_env in ("1", "true", "yes", "on")

    uvicorn.run("app.main:app", host=host, port=port, reload=reload, log_level="info")
