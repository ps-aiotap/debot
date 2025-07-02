import asyncio
import aiohttp
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import trafilatura
from cache_utils import cache_crawled_content, get_cached_crawled_content

class WebCrawler:
    def __init__(self, max_pages: int = 50, crawl_depth: int = 2, respect_robots: bool = True):
        self.max_pages = max_pages
        self.crawl_depth = crawl_depth
        self.respect_robots = respect_robots
        self.visited_urls: Set[str] = set()
        self.documents: List[Dict[str, str]] = []
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be crawled according to robots.txt."""
        if not self.respect_robots:
            return True
        
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch('*', url)
        except:
            return True
    
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        """Fetch and extract clean text from a webpage."""
        # Check cache first
        cached_content = get_cached_crawled_content(url)
        if cached_content:
            return cached_content
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    # Extract clean text using trafilatura
                    content = trafilatura.extract(html)
                    if content:
                        # Cache the extracted content
                        cache_crawled_content(url, content)
                        return content
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        
        return ""
    
    async def crawl_urls(self, start_urls: List[str]) -> List[Dict[str, str]]:
        """Crawl URLs and extract content."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for url in start_urls:
                if len(self.visited_urls) >= self.max_pages:
                    break
                
                if url not in self.visited_urls and self.can_fetch(url):
                    self.visited_urls.add(url)
                    tasks.append(self._process_url(session, url))
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.documents
    
    async def _process_url(self, session: aiohttp.ClientSession, url: str):
        """Process a single URL."""
        content = await self.fetch_page(session, url)
        if content:
            self.documents.append({
                'content': content,
                'source': url,
                'filename': urlparse(url).path.split('/')[-1] or 'index',
                'type': 'web'
            })

async def crawl_websites(urls: List[str], max_pages: int = 50, crawl_depth: int = 2) -> List[Dict[str, str]]:
    """Main function to crawl websites."""
    crawler = WebCrawler(max_pages=max_pages, crawl_depth=crawl_depth)
    return await crawler.crawl_urls(urls)