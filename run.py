import uvicorn
import asyncio
from app import create_admin

# Server startup script
if __name__ == "__main__":
    asyncio.run(create_admin.create_admin())
    uvicorn.run("app.main:main", host="127.0.0.1", port=8000, reload=True)
