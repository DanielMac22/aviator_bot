import aiohttp
from config import Config
import re

async def fetch_aviator_data():
    """Fetch raw HTML data from Odibets"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                Config.ODIBETS_URL,
                headers=Config.REQUEST_HEADERS,
                timeout=10
            ) as response:
                if response.status != 200:
                    raise Exception(f"HTTP Error {response.status}")
                return await response.text()
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")

def parse_multipliers(html):
    """Extract multipliers from HTML"""
    matches = re.findall(r"(\d+\.\d+)x", html)
    return [float(m) for m in matches][-Config.HISTORY_SIZE:]
