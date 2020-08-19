from fetch_data import fetch_data
from models import DealsModel
from typing import List
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_deals() -> List[DealsModel]:
    return fetch_data()
