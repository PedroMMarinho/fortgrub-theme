import os
import requests
from tqdm import tqdm  # pip install tqdm if you haven't yet

# --- Configuration ---
API_URL = "https://fortnite-api.com/v1/banners"
OUTPUT_DIR = os.path.join("assets", "banners", "icons")

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

def fetch_banner_data():
    """Fetches the raw JSON data from the API."""
    print(f"🌍 Connecting to {API_URL}...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        
        if json_data.get('status') == 200:
            return json_data.get('data', [])
        else:
            print(f"❌ API Error: Status {json_data.get('status')}")
            return []
            
    except Exception as e:
        print(f"❌ Network Error: {e}")
        return []

def download_image(url, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
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
    
    # 1. Get the list of banners
    banners = fetch_banner_data()

    if not banners:
        print("⚠️ No banners found to download.")
        return

    print(f"🚀 Found {len(banners)} banners. Starting download...")

    with tqdm(total=len(banners), unit="img") as pbar:
        for item in banners:
            # Extract ID and URL from the JSON object you showed me
            item_id = item.get('id')
            images = item.get('images', {})
            
            # Try high-res 'icon' first, fallback to 'smallIcon'
            image_url = images.get('icon')
            if not image_url:
                image_url = images.get('smallIcon')
                print(f"⚠️ No 'icon' found for {item_id}, using 'smallIcon' instead.")

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
                pbar.write(f"⚠️ Skipping item {item_id}.png: No URL found")

            pbar.update(1)

    print("\n🎉 Download complete!")

if __name__ == "__main__":
    main()