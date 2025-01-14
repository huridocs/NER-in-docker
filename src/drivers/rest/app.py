import sys

from fastapi import FastAPI

from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase

app = FastAPI()


@app.get("/info")
async def info():
    return sys.version


@app.get("/")
async def get_named_entities(text: str):
    return NamedEntitiesFromTextUseCase().get_entities(text)
