from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import httpx

app = FastAPI()

STEAM_API = "https://steamcommunity.com/market/priceoverview/"

# ── Serve Frontend ─────────────────────────────
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


# ── Helpers ────────────────────────────────────
def parse_price(price_str: str):
    try:
        return float(price_str.replace("$", "").replace(",", ""))
    except:
        return None


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


# ── API Endpoint ───────────────────────────────
@app.get("/price")
async def price(item: str = Query(...)):
    data = await get_price(item)

    if not data:
        return {"error": "Item not found"}

    lowest = data.get("lowest_price")
    median = data.get("median_price")

    low_val = parse_price(lowest)
    med_val = parse_price(median)

    discount = 0
    underpriced = False

    if low_val and med_val and med_val > 0:
        discount = round(((med_val - low_val) / med_val) * 100, 2)
        underpriced = discount > 5  # tweak later

    return {
        "item": item,
        "lowest_price": lowest,
        "median_price": median,
        "discount_percent": discount,
        "underpriced": underpriced
    }