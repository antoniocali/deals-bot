import asyncio
import requests
from app.utils.config import Config


def removeSpecialFromPrice(textInput: str) -> str:
    return textInput.replace(".", "").replace(",", ".").replace("€", "")


async def shortenUrl(url: str) -> dict:
    url = "https://api.shorte.st/v1/data/url"
    token = Config.get_instance().shortest_token
    headers = {"public-api-token": token}
    data = {"urlToShorten": url}
    response = requests.put(url, data=data, headers=headers)
    if response.ok:
        print(response.json())
        return response.json()
