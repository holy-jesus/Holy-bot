import sys

from fastapi import FastAPI, Request, Response

app = FastAPI()


@app.get("/")
async def index(request: Request):
    return "Hello world"
