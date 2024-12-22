import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

def is_product_url(url):
    return '/product/' in url or '/item/' in url or '/p/' in url

async def fetch_and_parse(url, session):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            product_urls = [a['href'] for a in soup.find_all('a', href=True) if is_product_url(a['href'])]
            return product_urls
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

async def crawl_domains(domains):
    async with aiohttp.ClientSession() as session:
        tasks = []
        all_product_urls = {}
        
        for domain in domains:
            task = asyncio.create_task(fetch_and_parse(domain, session))
            tasks.append((domain, task))
        
        for domain, task in tasks:
            product_urls = await task
            all_product_urls[domain] = list(set(product_urls))
        
        return all_product_urls

def save_urls_to_csv(all_product_urls, filename="product_urls.csv"):
    data = []
    for domain, urls in all_product_urls.items():
        for url in urls:
            data.append([domain, url])
    
    df = pd.DataFrame(data, columns=["Domain", "Product URL"])
    df.to_csv(filename, index=False)
    print(f"URLs saved to {filename}")

if __name__ == "__main__":
    domains = ["http://example1.com", "http://example2.com", "http://example3.com"]
    all_product_urls = asyncio.run(crawl_domains(domains))
    save_urls_to_csv(all_product_urls)
