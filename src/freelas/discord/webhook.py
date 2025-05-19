import re
from freelas.http.client import Client
from freelas.settings import WEB_HOOK, WORKANA_URL


class Webhook:
    @staticmethod
    async def send(response):
        embed = Webhook.embed(response)
        return await Client.post(WEB_HOOK, json=embed)
        
    @staticmethod
    def embed(response: dict) -> dict:
        title = response["title"]
        url = WORKANA_URL + f"job/{response['slug']}"
        country = response["country"]
        budget = response["budget"]
        description = Webhook.clear_description(response["description"])
        
        return {
            "embeds": [
                {
                    "title": title,
                    "url": url,
                    "description": description,
                    "color": 0x3498db,
                    "fields": [
                        {
                            "name": "País",
                            "value": country,
                            "inline": True
                        },
                        {
                            "name": "Orçamento",
                            "value": budget,
                            "inline": True
                        },
                    ]
                }
            ]
        }
    
    @staticmethod
    def clear_description(texto: str) -> str:
        return re.sub(r"Categoría\s?:.*", "", texto, flags=re.DOTALL).strip()