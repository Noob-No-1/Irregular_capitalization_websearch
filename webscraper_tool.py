from langchain.agents import Tool
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def web_scraper(query: str) -> str:

    search_url = f"https://www.baidu.com/s?wd={query}"
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }

    try:
        logger.info(f"Fetching content from URL: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Extract and clean text content
        text = soup.get_text(separator=' ', strip=True)
        logger.info(f"Successfully fetched content from {search_url}")
        return text

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching content from {search_url}: {e}")
        return f"Error fetching content: {e}"

# Create an instance of the Tool with 'is_single_input' set to True
web_scraper_tool = Tool(
    name="Web Scraper",
    func=web_scraper,
    description="Fetches and returns web page content based on search queries.",
    is_single_input=True
)
'''
def main():
    query = "iphone"
    content = web_scraper_tool.run(query) 
    print(content[:500])

if __name__ == "__main__":
    main()
    '''