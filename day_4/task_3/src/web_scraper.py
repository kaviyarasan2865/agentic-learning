"""
Web Scraper - Retrieves astronomy information from free web sources
Implements scraping from Wikipedia, NASA, and other astronomy websites.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import random

class WebScraper:
    """
    Web scraper for retrieving astronomy information from free sources.
    """
    
    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Astronomy-specific websites
        self.astronomy_sources = [
            'nasa.gov',
            'space.com',
            'astronomy.com',
            'skyandtelescope.org',
            'hubblesite.org',
            'esa.int',
            'jpl.nasa.gov'
        ]
    
    def search_and_scrape(self, query: str) -> str:
        """
        Search for astronomy information and scrape relevant content.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Retrieved information
        """
        try:
            # Try Wikipedia first
            wiki_result = self.search_wikipedia(query)
            if wiki_result and len(wiki_result) > 100:
                return wiki_result
            
            # Try NASA sources
            nasa_result = self.search_nasa_sources(query)
            if nasa_result and len(nasa_result) > 100:
                return nasa_result
            
            # Try general astronomy search
            general_result = self._search_general_astronomy(query)
            if general_result and len(general_result) > 100:
                return general_result
            
            return "Information not found. Please try a different query."
            
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
    
    def search_wikipedia(self, query: str) -> str:
        """
        Search Wikipedia for astronomy information.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Retrieved information from Wikipedia
        """
        try:
            # Clean query for Wikipedia search
            clean_query = query.replace(' ', '_').replace('?', '').strip()
            
            # Try direct Wikipedia URL
            wiki_url = f"https://en.wikipedia.org/wiki/{clean_query}"
            response = self.session.get(wiki_url, timeout=10)
            
            if response.status_code == 200:
                return self._extract_wikipedia_content(response.text)
            
            # Try searching Wikipedia
            search_url = f"https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['query']['search']:
                    page_title = data['query']['search'][0]['title']
                    page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                    page_response = self.session.get(page_url, timeout=10)
                    if page_response.status_code == 200:
                        return self._extract_wikipedia_content(page_response.text)
            
            return ""
            
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return ""
    
    def search_nasa_sources(self, query: str) -> str:
        """
        Search NASA websites for astronomy information.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Retrieved information from NASA sources
        """
        try:
            # NASA websites to search
            nasa_sites = [
                'https://science.nasa.gov',
                'https://www.nasa.gov',
                'https://hubblesite.org',
                'https://www.jpl.nasa.gov'
            ]
            
            for site in nasa_sites:
                try:
                    search_url = f"{site}/search"
                    params = {'q': query}
                    response = self.session.get(search_url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        content = self._extract_content(response.text)
                        if content and len(content) > 100:
                            return content
                except:
                    continue
            
            return ""
            
        except Exception as e:
            print(f"NASA search error: {e}")
            return ""
    
    def _search_general_astronomy(self, query: str) -> str:
        """
        Search general astronomy websites.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Retrieved information
        """
        try:
            # Try space.com
            space_url = f"https://www.space.com/search?q={query.replace(' ', '+')}"
            response = self.session.get(space_url, timeout=10)
            
            if response.status_code == 200:
                content = self._extract_content(response.text)
                if content and len(content) > 100:
                    return content
            
            # Try astronomy.com
            astro_url = f"https://astronomy.com/search?q={query.replace(' ', '+')}"
            response = self.session.get(astro_url, timeout=10)
            
            if response.status_code == 200:
                content = self._extract_content(response.text)
                if content and len(content) > 100:
                    return content
            
            return ""
            
        except Exception as e:
            print(f"General astronomy search error: {e}")
            return ""
    
    def _extract_wikipedia_content(self, html: str) -> str:
        """
        Extract content from Wikipedia HTML.
        
        Args:
            html (str): Wikipedia HTML content
            
        Returns:
            str: Extracted text content
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Find main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                return ""
            
            # Extract paragraphs
            paragraphs = content_div.find_all('p')
            text_content = []
            
            for p in paragraphs[:10]:  # Limit to first 10 paragraphs
                text = p.get_text().strip()
                if text and len(text) > 50:  # Only meaningful paragraphs
                    text_content.append(text)
            
            return '\n\n'.join(text_content)
            
        except Exception as e:
            print(f"Wikipedia content extraction error: {e}")
            return ""
    
    def _extract_content(self, html: str) -> str:
        """
        Extract content from general HTML.
        
        Args:
            html (str): HTML content
            
        Returns:
            str: Extracted text content
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'menu']):
                element.decompose()
            
            # Find main content areas
            content_selectors = [
                'main', 'article', '.content', '.main-content', 
                '#content', '#main', '.post-content', '.entry-content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text()
                    break
            
            if not content:
                # Fallback to body text
                content = soup.get_text()
            
            # Clean up content
            lines = content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line and len(line) > 30:  # Only meaningful lines
                    cleaned_lines.append(line)
            
            return '\n\n'.join(cleaned_lines[:20])  # Limit to first 20 lines
            
        except Exception as e:
            print(f"Content extraction error: {e}")
            return ""
    
    def get_astronomy_facts(self, topic: str) -> List[str]:
        """
        Get multiple facts about an astronomy topic.
        
        Args:
            topic (str): Astronomy topic
            
        Returns:
            List[str]: List of facts
        """
        facts = []
        
        # Try different search queries
        queries = [
            f"{topic} astronomy facts",
            f"{topic} space science",
            f"{topic} cosmic phenomena",
            f"{topic} astronomical discoveries"
        ]
        
        for query in queries:
            try:
                fact = self.search_and_scrape(query)
                if fact and len(fact) > 100:
                    facts.append(fact)
                
                time.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                print(f"Error getting facts for query '{query}': {e}")
                continue
        
        return facts 