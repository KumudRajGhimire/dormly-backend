from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from sqlalchemy.orm import Session 
from sqlalchemy import text
from app.auth.router import router as auth_router
from app.listings.router import router as list_router
from app.categories.router import router as category_router
from app.campuses.router import router as campus_router
from app.hostels.router import router as hostel_router
from app.users.router import router as user_router
from app.wishlist.router import router as wishlist_router
from app.chat.router import router as chat_router
from app.chat.ws_router import router as chat_ws_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "https://dormlyshop.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(list_router)
app.include_router(category_router)
app.include_router(campus_router)
app.include_router(hostel_router)
app.include_router(user_router)
app.include_router(wishlist_router)
app.include_router(chat_router)
app.include_router(chat_ws_router)


@app.get("/")
def root():
    return {"message":"Welcome to Dormly"}

@app.get("/health")
def health():
    return {"status":"healthy"}