#webcrawler_test
#author: Zhao Zhihao
#Date: 19/12/2024
import time
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from collections import defaultdict
#import jieba

load_dotenv()
#personal API KEYS and CSE ID, for other use can use conmapny account to get the api keys and cse id 
# and put it under .env in the SAME directory as this script
API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')
#instead of .env file 
#API_KEY = 'apikeys'
#CSE_ID = 'customised search engine'

processed_urls = set() #prevent reaccessing the same urls during search
frequency_table = defaultdict(list)

def google_search(query, num_results=10):
#use google search to get a list of urls
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': CSE_ID,
        'q': query,
        'num': num_results
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        results = response.json()
        urls = [item['link'] for item in results.get('items', [])]
        return urls
    except Exception as e:
        print(f"Error performing Google Search: {e}")
        return []


def fetch_page_content(url):
#given an url, return the text content of this url excluding the <script> and <style> part 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        text = soup.get_text(separator=' ')
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""
'''
def count_variants_in_text(text, variants):
#Count the frequency of each variant in the provided text.
    counts = defaultdict(int)
    for variant in variants:
        # Use word boundaries to ensure accurate matches
        pattern = rf'\b{re.escape(variant)}\b'
        matches = re.findall(pattern, text) #case sensitive search
        counts[variant] += len(matches)
    return counts
'''
def count_variants_in_text(text, variants):
#changed the logic to match the exact keyword rather than tokenization first 
#if need more complex logic need to rewrite this to tokenization and possibally new packages (it might get complex for multiligual text)
    counts = defaultdict(int)

    for variant in variants:
        pattern = re.escape(variant)
        matches = re.findall(pattern, text)  # Use re.findall to get all exact matches

        counts[variant] = len(matches)

    return counts

def search_frequency(target_word, variants, num_results = 10):
    #search and return frequencies of a single word
    #combined the logic of google_search, fetch_page_content and count_variants_in_text
    urls = google_search(target_word)

    word_counts = defaultdict(int)

    for url in urls:
        if url in processed_urls:
            print(f"URL already processed: {url}. Skipping.")
            continue

        text = fetch_page_content(url)
        if text:
            counts = count_variants_in_text(text, variants)
            for variant, count in counts.items():
                word_counts[variant] += count
        processed_urls.add(url)
        time.sleep(0.5)

    # Store results
    for variant, count in word_counts.items():
        frequency_table[target_word].append([variant, count])
        #print(f"Word '{target_word}' Variant '{variant}': {count} occurrences.")

def display_results():
    """
    Display the frequency table in a readable format.
    """
    print("--- Frequency Table ---\n")
    for word, counts in frequency_table.items():
        print(f'"{word}": [')
        for variant, count in counts:
            print(f'    ["{variant}", {count}],')
        print('],\n')

def main():
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
    "pnc": ["PNC", "PnC", "pnc"]}


    for word, variants in TARGET_WORDS.items():
        search_frequency(word, variants)

    display_results()

if __name__ == "__main__":
    main()

'''
results: 
"Pdf": [
    ["PDF", 675],
    ["pdf", 11],
    ["Pdf", 0],
],

"ar": [
    ["ar", 1],
    ["AR", 254],
    ["Ar", 0],
    ["aR", 0],
],

"WiFi": [
    ["WiFi", 167],
    ["wifi", 3],
    ["WIFI", 25],
    ["Wifi", 72],
    ["WIfi", 0],
],

"sI": [
    ["SI", 257],
    ["si", 4],
    ["Si", 41],
],

"DOOM": [
    ["doom", 34],
    ["Doom", 334],
    ["DOOM", 60],
],

"Acc线": [
    ["acc线", 0],
    ["ACC线", 2],
    ["Acc线", 0],
],

"CIPA": [
    ["CIPA", 158],
    ["cipa", 0],
    ["CiPA", 12],
],

"SP": [
    ["SP", 92],
    ["sp", 60],
    ["Sp", 39],
],

"hellokittyT恤": [
    ["hellokittyt恤", 0],
    ["HELLOKITTYT恤", 0],
    ["HellokittyT恤", 0],
    ["hellokittyT恤", 0],
],

"pnc": [
    ["PNC", 262],
    ["PnC", 0],
    ["pnc", 12],
]
'''