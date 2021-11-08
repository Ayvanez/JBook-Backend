from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .routers import books

app = FastAPI()

app.include_router(books.router, prefix='/api', )
# origins = [
#     "http://localhost:3001",
#     "localhost:3001"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Jbook!"}
