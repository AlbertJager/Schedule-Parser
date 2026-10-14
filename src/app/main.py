from fastapi import FastAPI
from src.app.routers import schedule_router

app = FastAPI()

app.include_router(schedule_router, prefix="/schedule")


@app.get("/")
def root():
    return {"message": "Добро пожаловать на Schedule Scraper!"}