import os
import requests
from playwright.async_api import async_playwright
import pdfplumber


# Constants
BASE_URL = "https://rules.cityofnewyork.us/"
SEARCH_URL = f"{BASE_URL}/?s="
PDF_OUTPUT_FOLDER = "output"

class RuleScraper:
    def __init__(self, playwright, headless=True):
        """Initialize the Playwright Browser."""
        self.playwright = playwright
        self.headless = headless
        self.browser = None
        self.page = None

    async def setup_browser(self):
        """Setup Playwright browser and page."""
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()

    async def search_rules(self, query):
        """Search for rules on NYC's rule website and return valid rule page URLs."""
        search_url = f"{SEARCH_URL}{query.replace(' ', '+')}"
        await self.page.goto(search_url, wait_until="domcontentloaded")

        # Extract valid rule page links
        rule_links = set()
        for link in await self.page.locator("a").all():
            href = await link.get_attribute("href")
            if href and BASE_URL in href and href != BASE_URL and not ("#" in href and not href.endswith(".pdf")):
                rule_links.add(href)

        return list(rule_links)

    async def extract_pdf_link(self, rule_page_url):
        """Extract the PDF link from a rule page."""
        await self.page.goto(rule_page_url, wait_until="domcontentloaded")

        # Look for links with specific text
        link_elements = await self.page.locator("a").all()
        for link in link_elements:
            text = await link.inner_text()
            href = await link.get_attribute("href")
            if href and any(text_part in text for text_part in ["Adopted Rule Full Text", "Proposed Rule Full Text", "Rule Full Text"]):
                return href if href.startswith("http") else f"{BASE_URL}{href}"
        
        return None

    async def download_pdf(self, url, output_folder=PDF_OUTPUT_FOLDER):
        """Download a PDF from the given URL and save it to the output folder."""
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.join(output_folder, os.path.basename(url))

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename

        return None

    async def extract_text_from_pdf(self, pdf_path):
        """Extract text from a downloaded PDF."""
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(filter(None, [page.extract_text() for page in pdf.pages]))

    async def close(self):
        """Close browser session."""
        if self.browser:
            await self.browser.close()