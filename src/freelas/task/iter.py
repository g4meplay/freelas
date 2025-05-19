from freelas.scraping.soup import Soup
from freelas.http.client import Client
from freelas.settings import WORKANA_JOBS, ECONOMY_URL
from freelas.discord.webhook import Webhook
from asyncio import sleep
from decimal import Decimal, getcontext

async def get_usd_brl_bid() -> Decimal:
    response = await Client.get(ECONOMY_URL)
    data = response.json()
    return Decimal(data["USDBRL"]["bid"])
    
async def iter():
    page = 1
    bid = await get_usd_brl_bid()
    while True:
        print(f"Page: {page}")
        workana_response = await Client.get(f"{WORKANA_JOBS}&page={page}")
        print(f"Workana status-code: {workana_response.status_code}")
        projects = Soup(workana_response, bid).projects()

        if not projects:
            break

        for project in projects:
            discord_response = await Webhook.send(project)
            print(f"Discord status-code: {discord_response.status_code}")
            await sleep(5)

        page += 1
        await sleep(15)