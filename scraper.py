import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Some sites block default User-Agents
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

async def get_article_urls_from_page(page_url: str) -> List[str]:
    """Scrapes a TechCrunch topic page and returns a list of article URLs."""
    html = await fetch_html(page_url)
    soup = BeautifulSoup(html, "html.parser")
    
    urls = []
    # TechCrunch typically has post blocks with titles containing links
    # This might need adjustment based on their current DOM structure
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        # Basic filter to get article links from the techcrunch domain that look like articles
        # Techcrunch articles usually have a date pattern like /202X/MM/DD/title/
        if "techcrunch.com/20" in href and href not in urls:
            urls.append(href)
            
    return urls

async def scrape_article(url: str) -> Dict[str, str]:
    """Scrapes a single article and returns its title, author, and text."""
    html = await fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    
    title = ""
    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text(strip=True)
        
    # Authors are often in specific blocks
    author = ""
    author_tag = soup.find(class_="article__byline") or soup.find(class_="byline-wrapper")
    if author_tag:
        author = author_tag.get_text(strip=True)
        
    # Extract paragraphs
    paragraphs = soup.find_all("p")
    text_content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    return {
        "url": url,
        "title": title,
        "author": author,
        "text": text_content
    }
