import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os
import glob

def process_movies():

    input_files = glob.glob('input*.json')

    if not input_files:
        print("Error: No input files found (e.g., input.json, input1.json)!")
        return

    scraper = cloudscraper.create_scraper()

    for file_path in input_files:
      
        output_file = file_path.replace('input', 'output')
        
        print(f"\n--- Processing: {file_path} to {output_file} ---")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        extracted_items = []

        for movie in input_data.get('movies', []):
            title = movie.get('title')
            watch_url = movie.get('links', {}).get('watch')
            print(f"Fetching: {title}")

            try:
                resp = scraper.get(watch_url, timeout=20)
                soup = BeautifulSoup(resp.text, 'html.parser')
                iframe = soup.find('iframe')
                
                if iframe and 'src' in iframe.attrs:
                    iframe_src = iframe['src']
                    iframe_res = scraper.get(iframe_src, headers={'Referer': watch_url}, timeout=20)
                    
           
                    m3u8_match = re.search(r'file\s*:\s*"(https?://[^"]+\.m3u8[^"]*)"', iframe_res.text)
                    
                    if m3u8_match:
                        extracted_items.append({
                            "id": title,
                            "title": title,
                            "poster": movie.get('thumbnail'),
                            "stream_url": m3u8_match.group(1),
                            "headers": {"Referer": "https://speedostream1.com/"}
                        })
            except Exception as e:
                print(f"Error processing {title}: {e}")


        if extracted_items:
            final_output = {
                "hero": [extracted_items[0]],
                "categories": [
                    {
                        "name": f"Latest from {file_path}", 
                        "items": extracted_items 
                    }
                ]
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved to {output_file}")
        else:
            print(f"No items extracted for {file_path}")

if __name__ == "__main__":
    process_movies()
