from collections import defaultdict
import json
import re
from baidusearch.baidusearch import search
import time
from tqdm import tqdm

frequency_table = defaultdict(list)
def fetch_content(word):
    '''
    使用baidusearch来进行检索，并整合搜索结果的结果，只保留
    'title' 和 'abstract'
    '''
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

def find_case_insensitive_variants(text, keyword):
    '''
    从fetch_content中得到文本后，对文本中出现的keyword及其
    变式进行词频统计
    '''
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    variant_counts = defaultdict(int)

    for match in pattern.finditer(text):
        variant = match.group()
        variant_counts[variant] += 1
    
    sorted_variants = sorted(variant_counts.items(), key=lambda x:x[1], reverse=True)
    return sorted_variants

def extract_keywords(file_path):
    """
    读取json file中的 "keyword"部分并整合到一个Array中
    """
    keywords = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        # Skip the header line
        next(file)
        
        for line in file:
            if line.strip():  # Ignore empty lines
                # Split the line by tab and take the first column (keyword)
                keyword = line.split('\t')[0]
                keywords.append(keyword)
    
    return keywords

def process_word(keywords):
    '''
    对keywords中的每一个keyword进行词频统计
    '''
    results = {}
    with tqdm(total=len(keywords), desc="Processing keywords") as pbar:
        for keyword in keywords:
            text = fetch_content(keyword)
            results[keyword] = find_case_insensitive_variants(text, keyword)
            time.sleep(5)  # Avoid getting blocked
            pbar.update(1)
    return results

def extract_keywords_from_tsv(file_path):
    """
    Reads a TSV (tab-separated values) file and extracts the 'word' column.
    """
    keywords = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)  # Skip the header line
        for line in file:
            if line.strip():  # Ignore empty lines
                word, _ = line.split('\t', 1)  # Split into 'word' and 'type'
                keywords.append(word.strip())  # Add the 'word' part to keywords
                
    return keywords

def save_results_to_json(results, output_path):
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

def main():
    tsv_file_path = "bd_search.txt"  
    output_path = "results.json"
    # Extract keywords 
    keywords = extract_keywords_from_tsv(tsv_file_path)
    # Process the keywords
    results = process_word(keywords)
    # Print frequency table
    # Save the results to a JSON file
    save_results_to_json(results, output_path)

    print(f"\nAll results have been written to '{output_path}'.")

if __name__ == "__main__":
    main()



'''"Pdf": [('pdf', 50), ('PDF', 35)]
"ar": [('AR', 42), ('ar', 21), ('Ar', 2)]
"WiFi": [('WiFi', 30), ('wifi', 19), ('WIFI', 3)]
"sI": [('si', 23), ('Si', 17), ('SI', 11), ('sI', 7)]
"DOOM": [('doom', 31), ('DOOM', 16), ('Doom', 5)]
"Acc线": [('acc线', 25), ('ACC线', 17), ('Acc线', 9)]
"CIPA": [('cipa', 23), ('CIPA', 17), ('CiPA', 2)]
"SP": [('sp', 30), ('SP', 18), ('Sp', 7)]
"hellokittyT恤": [('hellokittyT恤', 4), ('HelloKittyT恤', 1)]
"pnc": [('pnc', 30), ('PNC', 28), ('PnC', 5)]'''


'''
results:
--- Frequency Table ---

"Pdf": [
    ["PDF", 38],
    ["pdf", 48],
    ["Pdf", 2],
],

"ar": [
    ["ar", 23],
    ["AR", 41],
    ["Ar", 4],
    ["aR", 0],
],

"WiFi": [
    ["WiFi", 29],
    ["wifi", 27],
    ["WIFI", 1],
    ["Wifi", 0],
    ["WIfi", 0],
],

"sI": [
    ["SI", 11],
    ["si", 23],
    ["Si", 17],
],

"DOOM": [
    ["doom", 35],
    ["Doom", 5],
    ["DOOM", 14],
],

"Acc线": [
    ["acc线", 33],
    ["ACC线", 14],
    ["Acc线", 4],
],

"CIPA": [
    ["CIPA", 19],
    ["cipa", 23],
    ["CiPA", 2],
],

"SP": [
    ["SP", 20],
    ["sp", 28],
    ["Sp", 3],
],

"hellokittyT恤": [
    ["hellokittyt恤", 0],
    ["HELLOKITTYT恤", 0],
    ["HellokittyT恤", 0],
    ["hellokittyT恤", 4],
],

"pnc": [
    ["PNC", 24],
    ["PnC", 5],
    ["pnc", 28],
],
'''