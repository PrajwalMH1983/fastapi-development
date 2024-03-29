from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models , database
from routers import post , user , auth , vote
from configs import settings
#models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"Message" : "Hello It's Prajwal here"}




