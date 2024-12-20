#lanchain main script
import asyncio
from collections import defaultdict
import json
import os
import logging
import re
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from webscraper_tool import web_scraper_tool
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
from bs4 import BeautifulSoup
from langchain_community.chat_models import ChatOpenAI

# Configure logging for the main script
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI LLM (ChatGPT-4)
try:
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0  # Adjust as needed
    )
    logger.info("OpenAI LLM (ChatGPT-4) initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize OpenAI LLM: {e}")
    exit(1)

# Create the agent with the WebScraperTool
try:
    agent = initialize_agent(
        tools=[web_scraper_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True  # Set to False to reduce detailed logs
    )
    logger.info("LangChain Agent initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize LangChain Agent: {e}")
    exit(1)

# Define your target words and their capitalization variants

TARGET_WORDS = {
    "Pdf": ["PDF", "pdf", "Pdf"],
    "WiFi": ["WiFi", "wifi", "WIFI", "Wifi", "WIfi"],
    "Acc线": ["acc线", "ACC线", "Acc线"],
    "hellokittyT恤": ["hellokittyt恤", "HELLOKITTYT恤", "HellokittyT恤", "hellokittyT恤"],
    "pnc": ["PNC", "PnC", "pnc"]
}
'''
TARGET_WORDS = {
    "Pdf": ["PDF", "pdf", "Pdf"],
    "ar": ["ar", "AR", "Ar", "aR"],
    "WiFi": ["WiFi", "wifi", "WIFI", "Wifi", "WIfi"],
    "sI": ["SI", "si", "Si"],
    "DOOM": ["doom", "Doom", "DOOM"],
    "Acc线": ["acc线", "ACC线", "Acc线"],
    "CIPA": ["CIPA", "cipa", "CiPA"],
    "SP": ["SP", "sp", "Sp"],
    "hellokittyT恤": ["hellokittyt恤", "HELLOKITTYT恤", "HellokittyT恤", "hellokittyT恤"],
    "pnc": ["PNC", "PnC", "pnc"]
}
'''
# Load processed URLs from a JSON file (or initialize as an empty set)
processed_urls_file = 'processed_urls.json'

def load_processed_urls():
    """ Load processed URLs from a JSON file. """
    if os.path.exists(processed_urls_file):
        with open(processed_urls_file, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_urls(processed_urls):
    """ Save processed URLs to a JSON file. """
    with open(processed_urls_file, 'w') as f:
        json.dump(list(processed_urls), f)
    logger.info(f"Processed URLs saved to {processed_urls_file}.")

# Asynchronous function to fetch and process web page content
# Asynchronous function to fetch and process web page content with exponential backoff
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_page_content_async(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Clean the HTML and extract text
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}")
        raise

# Asynchronous function to count variants in text
def count_variants_in_text(text, variants):
    counts = defaultdict(int)
    for variant in variants:
        pattern = rf'\b{re.escape(variant)}\b'
        matches = re.findall(pattern, text)
        counts[variant] += len(matches)
    return counts

# Asynchronous function to process a single word's variants with rate limiting
async def process_word_async(agent, word, variants, processed_urls, num_results=5):
    logger.info(f"Processing word: '{word}' with variants: {variants}")
    try:
        search_query = f'"{word}"'  # Exact match
        search_response = agent.run(search_query)
        urls = re.findall(r'https?://\S+', search_response)

        # Limit to top URLs
        urls = urls[:num_results]
        word_counts = defaultdict(int)

        tasks = []
        for url in urls:
            if url not in processed_urls:
                tasks.append(fetch_page_content_async(url))
            else:
                logger.info(f"Skipping already processed URL: {url}")

        # Rate-limiting: Add a small delay between tasks to avoid hitting API rate limits
        if tasks:
            contents = []
            for i, url in enumerate(urls):
                # Delay to prevent hitting rate limits
                if i > 0 and i % 10 == 0:  # Every 10 requests, wait for 2 seconds
                    logger.info("Sleeping to avoid rate limiting...")
                    await asyncio.sleep(5)
                
                content = await fetch_page_content_async(url)
                contents.append(content)

            for url, content in zip(urls, contents):
                if isinstance(content, Exception):
                    logger.error(f"Failed to fetch content from {url}")
                    continue
                counts = count_variants_in_text(content, variants)
                for variant, count in counts.items():
                    word_counts[variant] += count
                processed_urls.update(urls)

        return word_counts
    except Exception as e:
        logger.error(f"Error processing word '{word}': {e}")
        return {}

# Main function to handle the aggregation and display of results
async def main():
    processed_urls = load_processed_urls()

    frequency_table = defaultdict(list)
    tasks = []

    for word, variants in TARGET_WORDS.items():
        tasks.append(process_word_async(agent, word, variants, processed_urls, num_results=5))

    results = await asyncio.gather(*tasks)

    # Aggregate results into frequency table
    for (word, variants), word_counts in zip(TARGET_WORDS.items(), results):
        for variant, count in word_counts.items():
            frequency_table[word].append([variant, count])

    # Save processed URLs to disk
    save_processed_urls(processed_urls)

    # Print the frequency table
    print("\n--- Frequency Table ---\n")
    for word, counts in frequency_table.items():
        print(f'"{word}": [')
        for variant, count in counts:
            print(f'    ["{variant}", {count}],')
        print('],\n')

if __name__ == "__main__":
    asyncio.run(main())