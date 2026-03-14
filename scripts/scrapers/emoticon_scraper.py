import os
import requests
from tqdm import tqdm 

# --- Configuration ---
API_URL = "https://fortnite-api.com/v2/cosmetics/br"
OUTPUT_DIR = os.path.join("assets", "emoticons")

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

def fetch_emoticon_data():
    """Fetches the cosmetics JSON data and filters for emoticons."""
    print(f"🌍 Connecting to {API_URL}...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        
        if json_data.get('status') == 200:
            all_cosmetics = json_data.get('data', [])
            
            # Filter the massive list down to strictly emoticons
            emoticons = [
                item for item in all_cosmetics 
                if item.get('type', {}).get('value') == 'emoji'
            ]
            return emoticons
        else:
            print(f"❌ API Error: Status {json_data.get('status')}")
            return []
            
    except Exception as e:
        print(f"❌ Network Error: {e}")
        return []

def download_image(url, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Check if the file already exists and isn't empty to avoid re-downloading
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return "SKIP"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return "SUCCESS"
        
    except Exception as e:
        return f"ERROR: {e}"

def main():
    ensure_dir(OUTPUT_DIR)
    
    # 1. Get the filtered list of emoticons
    emoticons = fetch_emoticon_data()

    if not emoticons:
        print("⚠️ No emoticons found to download.")
        return

    print(f"🚀 Found {len(emoticons)} emoticons. Starting download...")

    # 2. Iterate and download using your progress bar logic
    with tqdm(total=len(emoticons), unit="img") as pbar:
        for item in emoticons:
            item_id = item.get('id')
            images = item.get('images', {})
            
            # Emoticons usually have an 'icon', fallback to 'smallIcon' just in case
            image_url = images.get('icon') or images.get('smallIcon')

            if item_id and image_url:
                filename = f"{item_id}.png"
                status = download_image(image_url, filename)
                
                # Update status text next to the bar
                if status == "SUCCESS":
                    pbar.set_postfix_str(f"✅ {item_id}.png")
                elif status == "SKIP":
                    pbar.set_postfix_str(f"⏭️ {item_id}.png")
                else:
                    pbar.write(f"❌ Failed {item_id}.png: {status}")
            else:
                pbar.write(f"⚠️ Skipping item {item_id}: No URL found")

            pbar.update(1)

    print("\n🎉 Download complete!")

if __name__ == "__main__":
    main()