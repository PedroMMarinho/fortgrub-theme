from helpers.utils import load_image, EMOTICONS_DIR, THEME_DIR
import os
from PIL import Image

def change_emoticon(config):
    filename = config["progress-bar-emoticon"]
    emoticon_path = os.path.join(EMOTICONS_DIR, filename)
    emoticon = load_image(emoticon_path)

    if emoticon is None:
        print(f"❌ Error: Emoticon '{filename}' not found in {EMOTICONS_DIR}")
        return None

    bbox = emoticon.getbbox()
    if bbox:
        emoticon = emoticon.crop(bbox)

    template_path = os.path.join(THEME_DIR, "template", "progress_highlight_e.png")
    highlight_template = load_image(template_path)

    scale = 64.0 / max(emoticon.width, emoticon.height)
    new_size = (int(emoticon.width * scale), int(emoticon.height * scale))
    
    emoticon = emoticon.resize(new_size, resample=Image.Resampling.LANCZOS)

    y = (highlight_template.height - emoticon.height) // 2
    x = highlight_template.width - emoticon.width

    highlight_template.paste(emoticon, (x, y), emoticon)

    output_path = os.path.join(THEME_DIR , "progress_highlight_e.png")
    highlight_template.save(output_path)
    
    print(f"✅ Emoticon '{filename}' inserted into highlight template")