import sys

from fastapi import FastAPI, Form
from pydantic import BaseModel

from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase

app = FastAPI()


@app.get("/info")
async def info():
    return sys.version


@app.post("/")
async def get_named_entities(text: str = Form("")):
    entities = NamedEntitiesFromTextUseCase().get_entities(text)
    return entities
