import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def scrape_domains():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://moz.com/top500", timeout=60000)

        # Wait for table to load
        await page.wait_for_selector("table tbody tr td.url", timeout=15000)

        # Extract domain names
        domain_elements = await page.query_selector_all("table tbody tr td.url")
        domains = ["https://" + (await el.inner_text()).strip() for el in domain_elements]

        await browser.close()

        # Save to CSV
        df = pd.DataFrame(domains, columns=["URL"])
        df.to_csv("moz_top_500_urls.csv", index=False)
        print(f"✅ Scraped {len(domains)} domains.")

async def scrape_cookies():
    df = pd.read_csv("moz_top_500_urls.csv")
    domains = df["URL"].tolist()
    
    all_cookies = []
    failed_sites = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for url in domains:
            try:
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(url, timeout=10000)
                await page.wait_for_timeout(5000)  # let cookies populate

                cookies = await context.cookies()
                for cookie in cookies:
                    cookie["source_site"] = url
                    all_cookies.append(cookie)

                await context.close()
            except Exception as e:
                print(f"❌ Failed to scrape cookies from {url}: {e}")
                failed_sites.append(url)

        await browser.close()

    # Save cookies and failures
    cookies_df = pd.DataFrame(all_cookies)
    cookies_df.to_csv("all_cookies.csv", index=False)

    with open("failed_sites.txt", "w") as f:
        for site in failed_sites:
            f.write(site + "\n")

    print(f"✅ Scraped cookies from {len(domains) - len(failed_sites)} sites.")
    print(f"❌ Failed on {len(failed_sites)} sites.")

async def main():
    await scrape_domains()
    await scrape_cookies()

if __name__ == "__main__":
    asyncio.run(main())
