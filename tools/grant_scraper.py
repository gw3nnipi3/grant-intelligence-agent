import requests
from bs4 import BeautifulSoup

class GrantScraper:

    def fetch_page(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.text


    def extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        # remove junk
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        # clean whitespace
        return " ".join(text.split())


    def scrape_grant(self, url: str) -> dict:
        html = self.fetch_page(url)
        text = self.extract_text(html)

        return {
            "url": url,
            "content": text[:10000]  # limit for now
        }