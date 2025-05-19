import re
from decimal import Decimal, ROUND_HALF_UP
from httpx import Response
from html import unescape
from bs4 import BeautifulSoup
from json import loads
from typing import List, Dict, Optional


class Soup:
    def __init__(self, response: Response, bid: Decimal, *args, **kwargs):
        self.tree = self.create(response, *args, **kwargs)
        self.bid = bid
    
    def create(self, response: Response, *args, **kwargs) -> BeautifulSoup:
        decoded = unescape(response.text).replace("\\/", "/")
        return BeautifulSoup(decoded, "lxml", *args, **kwargs)

    def clean_html(self, raw: str) -> str:
        soup = BeautifulSoup(raw, "lxml")
        return soup.get_text(separator=" ").strip()

    def _parse_usd_number(self, s: str) -> Optional[Decimal]:
        # Remove espaços e troca pontos usados como separador de milhares
        s = s.strip()
        # Remove pontos que são separadores de milhar e substitui vírgula por ponto decimal
        s = s.replace(".", "").replace(",", ".")
        try:
            return Decimal(s)
        except:
            return None

    def convert_budget(self, budget_str: str) -> Optional[str]:
        match_less = re.match(r"Menos de USD\s*([\d.,]+)", budget_str)
        if match_less:
            val_usd = self._parse_usd_number(match_less.group(1))
            if val_usd is None:
                return budget_str
            val_brl = (val_usd * self.bid).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
            val_fmt = f"R$ {val_brl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"Menos de {val_fmt}"

        # Faixa USD x - y
        match_range_usd = re.match(r"USD\s*([\d.,]+)\s*-\s*([\d.,]+)", budget_str)
        if match_range_usd:
            low_usd = self._parse_usd_number(match_range_usd.group(1))
            high_usd = self._parse_usd_number(match_range_usd.group(2))
            if low_usd is None or high_usd is None:
                return budget_str
            low_brl = (low_usd * self.bid).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
            high_brl = (high_usd * self.bid).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
            low_fmt = f"R$ {low_brl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            high_fmt = f"R$ {high_brl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{low_fmt} - {high_fmt}"

        # Valor único USD
        match_usd = re.match(r"USD\s*([\d.,]+)", budget_str)
        if match_usd:
            val_usd = self._parse_usd_number(match_usd.group(1))
            if val_usd is None:
                return budget_str
            val_brl = (val_usd * self.bid).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
            val_fmt = f"R$ {val_brl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return val_fmt

        # Caso padrão
        return budget_str

    def clean_project_data(self, projects: List[Dict]) -> List[Dict]:
        cleaned_projects = []
        for project in projects:
            cleaned_project = project.copy()

            # Limpar campos com HTML
            for key in ['title', 'description', 'country', 'profileLogo', 'infoImg', 'popoverContent']:
                if key in cleaned_project and isinstance(cleaned_project[key], str):
                    cleaned_project[key] = self.clean_html(cleaned_project[key])

            # Limpar HTML das skills
            if 'skills' in cleaned_project and isinstance(cleaned_project['skills'], list):
                for skill in cleaned_project['skills']:
                    for field in ['anchorText', 'title']:
                        if field in skill and isinstance(skill[field], str):
                            skill[field] = self.clean_html(skill[field])

            # Converter budget
            if 'budget' in cleaned_project and isinstance(cleaned_project['budget'], str):
                converted = self.convert_budget(cleaned_project['budget'])
                if converted:
                    cleaned_project['budget'] = converted

            cleaned_projects.append(cleaned_project)
        return cleaned_projects

    def projects(self) -> Optional[List[Dict]]:
        tag = self.tree.find(attrs={":results-initials": True})
        results = loads(tag[":results-initials"])["results"]
        if not results:
            return None
        return self.clean_project_data(results)
