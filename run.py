import uvicorn

from app.create_admin import create_admin

if __name__ == "__main__":
    uvicorn.run("app.main:main", host="127.0.0.1", port=8000, reload=True)
