from collections import defaultdict
import json
import re
from baidusearch.baidusearch import search
import time

frequency_table = defaultdict(list)
def fetch_content(word):
    results = search(word)
    text = list()
    for result in results:
        result.pop('url', None)
        result.pop('rank', None)
        text.append(result.get('title'))  # Title
        text.append(result.get('abstract'))  # Abstract

        # Concatenate the title and abstract fields, then remove spaces and punctuation
    single_string = json.dumps(text, ensure_ascii=False)

    # Remove all spaces, punctuation, and special characters using regex
    cleaned_string = re.sub(r'[^\w\u4e00-\u9fa5]', '', single_string)
    return cleaned_string

def count_frequency(text, variants):
    counts = defaultdict(int)
    for variant in variants:
        pattern = re.escape(variant)
        matches = re.findall(pattern, text)  # Use re.findall to get all exact matches

        counts[variant] = len(matches)

    return counts

def process_word(word, variants):
    word_counts = defaultdict(int)
    text = fetch_content(word)
    
    counts = defaultdict(int)  # Initialize counts here to avoid the UnboundLocalError
    
    if text:
        counts = count_frequency(text, variants)  # Now counts will be assigned properly
    
    for variant, count in counts.items():
        word_counts[variant] += count
    
    # Add it into frequency table
    for variant, count in word_counts.items():
        frequency_table[word].append([variant, count])

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
        process_word(word, variants)
        time.sleep(5)

    display_results()

if __name__ == "__main__":
    main()