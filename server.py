from mcp.server.mcpserver import MCPServer
import httpx
import asyncio
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent/".env"
load_dotenv(env_path)

mcp = MCPServer("GEOAPIFY")
apikey = os.getenv("GEOAPIFY_KEY")

@mcp.tool()
async def geocode_address(city:str)->dict:
    '''gives the latitude and longitude from the given city name'''
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "apiKey":apikey,
        "city":city
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url,params=params)
            response.raise_for_status()
            data=response.json()
        except Exception as e:
            print(e)

    return {
        "status":"success",
        "data":data.get("features")[0]["geometry"]["coordinates"]
    }

@mcp.tool()
async def reverse_geocode(lat:float,long:float)->dict:
    '''gives the address from latitude and longitude'''
    url = "https://api.geoapify.com/v1/geocode/reverse"
    params = {
            "apiKey":apikey,
            "lat":lat,
            "lon":long
        }
    async with httpx.AsyncClient() as client:
        response = await client.get(url,params=params)
        response.raise_for_status()
        data = response.json()

    return {
        "status":"success",
        "data":data.get("features")[0]["properties"].get("name")
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
