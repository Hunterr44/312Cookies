import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import json

df = pd.read_csv("Well_Formed_Domain_Data.csv")
domains = df["Root Domain"].dropna().tolist()
print(domains)

#Function to visit site and collect cookies
async def scrape_cookies(domain):
    try:
        url = f"https://{domain}"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, timeout=15000)
            cookies = await context.cookies()
            await browser.close()
            return domain, cookies
    except Exception as e:
        return domain, {"error": str(e)}

# Run all domains and collect results
async def main():
    results = []
    for domain in domains:
        domain = domain.strip()
        print(f"Scraping: {domain}")
        domain, cookies = await scrape_cookies(domain)
        results.append({"domain": domain, "cookies": cookies})
    
    with open("cookies_output.json", "w") as f:
        json.dump(results, f, indent=2)

#asyncio.run(main())
