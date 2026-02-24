import os
import requests
import io
from tqdm import tqdm 
from PIL import Image

# --- Configuration ---
API_URL = "https://fortnite.fandom.com/api.php"
OUTPUT_DIR = os.path.join("assets", "backgrounds")

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

def fetch_background_data():
    """Fetches all images embedded on the 'Lobby' wiki page and filters them strictly."""
    print(f"🌍 Connecting to {API_URL}...")
    
    params = {
        "action": "query",
        "generator": "images",     
        "titles": "Lobby",         
        "gimlimit": "500",         
        "prop": "imageinfo",
        "iiprop": "url",           
        "format": "json"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        pages = json_data.get("query", {}).get("pages", {})
        
        if pages:
            valid_backgrounds = []
            for page in pages.values():
                # The Wiki sometimes uses spaces instead of underscores in titles,
                # so we normalize it to underscores to make our check foolproof.
                title = page.get("title", "")
                normalized_title = title.replace(" ", "_")
                
                # STRICT FILTER: Only keep it if it has this exact string
                if "_Lobby_Background_-_Fortnite" in normalized_title:
                    valid_backgrounds.append(page)
                    
            return valid_backgrounds
        else:
            print("❌ API Error: No images found on that page.")
            return []
            
    except Exception as e:
        print(f"❌ Network Error: {e}")
        return []

def download_and_convert_image(url, final_filename):
    filepath = os.path.join(OUTPUT_DIR, final_filename)
    
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return "SKIP"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # --- THE FIX: Convert everything to PNG ---
        # 1. Load the downloaded bytes into Pillow
        image = Image.open(io.BytesIO(response.content))
        
        # 2. Convert to RGBA (just in case it's a weird format or has a palette)
        image = image.convert("RGBA")
        
        # 3. Save it forcefully as a PNG
        image.save(filepath, "PNG")
        # ------------------------------------------
        
        return "SUCCESS"
        
    except Exception as e:
        return f"ERROR: {e}"

def main():
    ensure_dir(OUTPUT_DIR)
    
    backgrounds = fetch_background_data()

    if not backgrounds:
        print("⚠️ No backgrounds found matching that name.")
        return

    print(f"🚀 Found {len(backgrounds)} backgrounds. Starting download and conversion...")

    with tqdm(total=len(backgrounds), unit="img") as pbar:
        for item in backgrounds:
            title = item.get("title", "")
            image_info = item.get("imageinfo", [{}])[0]
            image_url = image_info.get("url")

            if image_url:
                # Normalize the Wiki title (remove "File:" and replace spaces)
                clean_name = title.replace("File:", "").replace(" ", "_")
                
                # Slice out the unwanted suffix
                clean_name = clean_name.replace("_Lobby_Background_-_Fortnite", "")
                
                # Remove any existing file extension (.png, .jpg, etc.)
                clean_name = os.path.splitext(clean_name)[0]
                
                # Clean up any accidental trailing underscores or dashes
                clean_name = clean_name.strip("_-")
                
                # Append the final .png extension
                final_filename = f"{clean_name}.png"
                
                status = download_and_convert_image(image_url, final_filename)
                
                if status == "SUCCESS":
                    pbar.set_postfix_str(f"✅ {final_filename}")
                elif status == "SKIP":
                    pbar.set_postfix_str(f"⏭️ {final_filename}")
                else:
                    pbar.write(f"❌ Failed {final_filename}: {status}")
            else:
                pbar.write(f"⚠️ Skipping item {title}: No URL found")

            pbar.update(1)

    print("\n🎉 Download and conversion complete!")

if __name__ == "__main__":
    main()