from fastapi import FastAPI, Query
import httpx
import os

app = FastAPI()

STEAM_API = "https://steamcommunity.com/market/priceoverview/"

@app.get("/")
def home():
    return {"message": "Zikkapy is live 🚀"}

async def get_price(item: str):
    params = {
        "appid": 730,
        "currency": 1,
        "market_hash_name": item
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(STEAM_API, params=params)
        data = r.json()

    if not data.get("success"):
        return None

    return data

@app.get("/price")
async def price(item: str = Query(...)):
    data = await get_price(item)

    if not data:
        return {"error": "Item not found"}

    return {
        "item": item,
        "lowest_price": data.get("lowest_price"),
        "median_price": data.get("median_price")
    }