import asyncio
from playwright.async_api import async_playwright


async def get_page_html(url: str, timeout: int = 30_000, headless: bool = True):
    """Fetch the HTML content of `url` using Playwright.

    - `timeout` is in milliseconds and is passed to navigation/wait calls.
    - `headless` controls whether the browser is headless.
    """
    async with async_playwright() as p:
        # Launch browser with common flags for headless Linux environments
        browser = await p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        # Use a fresh context to avoid shared state
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate and wait for network to be mostly idle
            await page.goto(url, wait_until="load", timeout=timeout)
            try:
                await page.wait_for_load_state("networkidle", timeout=timeout)
            except Exception:
                # networkidle can be flaky; continue if it times out
                pass

            html_content = await page.content()
            return html_content
        finally:
            await browser.close()


async def main():
    url = "https://example.com"
    html = await get_page_html(url)
    print(html[:500])  # Print the first 500 characters of the HTML


if __name__ == "__main__":
    asyncio.run(main())
