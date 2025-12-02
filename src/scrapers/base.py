from playwright.async_api import async_playwright, Page, Browser
from config.settings import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper:
    """Scraper de base avec gestion navigateur, retry, timeout."""

    def __init__(self):
        self.browser: Browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            user_agent=settings.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Bloquer images/CSS/fonts pour accelerer le chargement sur Railway
        await self.context.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda route: route.abort())
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def new_page(self) -> Page:
        page = await self.context.new_page()
        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9'
        })
        return page

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def safe_goto(self, page: Page, url: str):
        """Navigation avec retry automatique."""
        logger.info(f"Navigation vers: {url}")
        await page.goto(url, timeout=settings.timeout, wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)  # Attente anti-detection
