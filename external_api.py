import httpx

ARTIC_BASE = "https://api.artic.edu/api/v1/artworks"

async def fetch_artwork(artwork_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ARTIC_BASE}/{artwork_id}")
        
        if response.status_code != 200:
            return None
        
        json_data = response.json()
        artwork_data = json_data.get("data")

        return {
            "id": artwork_data.get("id"),
            "title": artwork_data.get("title", "Unknown Title"),
        }
    
    