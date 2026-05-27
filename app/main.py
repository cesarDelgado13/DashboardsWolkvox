from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.routes.wolkvox import router as wolkvox_router

app = FastAPI()

app.include_router(wolkvox_router)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("app/templates/index.html", encoding="utf-8") as f:
        return f.read()