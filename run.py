import uvicorn
import asyncio
from app import create_admin

# Server startup script
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    asyncio.run(create_admin.create_admin())
