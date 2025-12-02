from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = r"c:\Users\Md Sahimuzzaman\Desktop\GST_DEMO\app\static\brand\placeholders"
BG_COLOR = "#111111"
TEXT_COLOR = "#60A5FA"  # Blue-400
BORDER_COLOR = "#333333"
FONT_SIZE_LARGE = 40
FONT_SIZE_SMALL = 20

def create_placeholder(filename, width, height, text, subtext="Preview – Asset Updating"):
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    d = ImageDraw.Draw(img)
    
    # Draw border
    d.rectangle([0, 0, width-1, height-1], outline=BORDER_COLOR, width=2)
    
    # Draw text (centered)
    # Since we might not have a specific font, we'll use default but try to center it roughly
    # For better quality, we'd load a font, but default is safer for script execution
    
    # Draw main text
    bbox = d.textbbox((0, 0), text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    d.text(((width-w)/2, (height-h)/2 - 10), text, fill=TEXT_COLOR)
    
    # Draw subtext
    bbox_sub = d.textbbox((0, 0), subtext)
    w_sub = bbox_sub[2] - bbox_sub[0]
    h_sub = bbox_sub[3] - bbox_sub[1]
    d.text(((width-w_sub)/2, (height-h)/2 + 20), subtext, fill="#666666")
    
    # Save
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path)
    print(f"Created {path}")

# Feature Screenshots
features = [
    ("dashboard.png", "Dashboard Analytics"),
    ("invoice.png", "Invoice Creation"),
    ("gst.png", "GST Reports"),
    ("whatsapp.png", "WhatsApp Integration"),
    ("customer.png", "Customer Management"),
    ("pdf.png", "PDF Generation")
]

for name, label in features:
    create_placeholder(name, 800, 600, label)

# Avatars
for i in range(1, 7):
    create_placeholder(f"avatar_{i}.png", 100, 100, f"User {i}", "")

# Video Thumbnail
create_placeholder("video_thumb.png", 1280, 720, "Product Demo Video", "Click to Play")

# OG Preview
create_placeholder("og_preview.png", 1200, 630, "WinderInvoice", "Social Preview")

print("All placeholders generated successfully.")
