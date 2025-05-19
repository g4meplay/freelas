from pathlib import Path
from os import getenv
from importlib.util import find_spec as find

BASE_DIR = Path(__file__).parent.parent
PROJECT_DIR = BASE_DIR.parent


if find("dotenv") is not None:
    from dotenv import load_dotenv
    
    load_dotenv(PROJECT_DIR / ".env", 
                override=True)
    
    load_dotenv(PROJECT_DIR / ".env.example", 
                override=False)

WEB_HOOK = getenv("WEB_HOOK")
WORKANA_URL = getenv("WORKANA_URL")
WORKANA_JOBS = WORKANA_URL + "jobs?language=pt&publication=1d"
ECONOMY_URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
