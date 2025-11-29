from fastapi import FastAPI
from app.routers import web
import os
from pathlib import Path
from dotenv import load_dotenv

app = FastAPI(title=os.getenv("APP_NAME"))

# router 
app.include_router(web.router)

