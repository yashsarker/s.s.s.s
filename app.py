import requests
from bs4 import BeautifulSoup
import json
import os
import glob

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "referer": "https://speedostream1.com/"
}

CACHE_FILE = 'iframe_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)

def process_movies():
    input_files = glob.glob('input*.json')

    if not input_files:
        print("Error: No input files found!")
        return

    session = requests.Session()
    session.headers.update(headers)
    
    iframe_cache = load_cache()

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

            iframe_src = None

            try:
                resp = session.get(watch_url, timeout=20)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    iframe = soup.find('iframe')
                    
                    if iframe and 'src' in iframe.attrs:
                        iframe_src = iframe['src']
                        iframe_cache[watch_url] = iframe_src
                        save_cache(iframe_cache)
            except Exception as e:
                print(f"Warning: watch_url failed for {title} - {e}")

            if not iframe_src:
                if watch_url in iframe_cache:
                    print(f"-> Using CACHED iframe for {title}...")
                    iframe_src = iframe_cache[watch_url]
                else:
                    print(f"-> Failed! No live response and no cache found for {title}.")
                    continue 

            if iframe_src:
                try:
                    php_hook_url = "https://allinonedev.top/hook.php" 
                    
                    params = {
                        "url": iframe_src,
                        "referer": "https://speedostream1.com/"
                    }
                    
                    print(f"-> Calling PHP Hook for {title}...")
                    hook_res = session.get(php_hook_url, params=params, timeout=30)
                    
                    try:
                        hook_data = hook_res.json()
                    except ValueError:
                        print(f"-> Error: Hook returned invalid JSON. Response snippet: {hook_res.text[:100]}")
                        continue
                    
                    if hook_data.get("success"):
                        m3u8_url = hook_data.get("m3u8")
                        extracted_items.append({
                            "id": title,
                            "title": title,
                            "poster": movie.get('thumbnail'),
                            "stream_url": m3u8_url,
                            "headers": {"Referer": "https://speedostream1.com/"}
                        })
                        print(f"-> Success! .")
                    else:
                        print(f"-> PHP Hook failed for {title}. Error: {hook_data.get('error')}")
                        
                except Exception as e:
                    print(f"Error calling PHP Hook for {title}: {e}")

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
