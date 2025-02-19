import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
from arabic_reshaper import reshape  # For reshaping Arabic text
from bidi.algorithm import get_display  # For correct Arabic text display

# File and folder paths
EXCEL_FILE = input("🏢 ادخل مسار ملف الإكسل: ")  # Path to your Excel file
PHOTOS_FOLDER = input("📸 ادخل مسار مجلد الصور: ")  # Folder containing photos named by passport numbers
BADGE_TEMPLATE = "badge_template.jpg"  # Path to your badge template
OUTPUT_FOLDER = input("📁 ادخل مسار مجلد الخطابات: ")  # Folder to save generated badges
FONT_FILE = "TheSans Bold.ttf"  # Path to your font file (e.g., arial.ttf)

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load the Excel sheet
try:
    df = pd.read_excel(EXCEL_FILE)
except Exception as e:
    print(f"❌ خطأ في تحميل ملف الإكسل: {e}")
    exit()

# Load the badge template
try:
    badge_template = Image.open(BADGE_TEMPLATE)
except Exception as e:
    print(f"❌ خطأ في تحميل قالب البادج: {e}")
    exit()

# Load the font
try:
    font = ImageFont.truetype(FONT_FILE, 50)  # Adjust font size as needed
    font2 = ImageFont.truetype(FONT_FILE, 57)  # Adjust font size as needed
    n_font = ImageFont.truetype(FONT_FILE, 57)  # Adjust font size as needed

except Exception as e:
    print(f"❌ خطأ في تحميل الخط: {e}")
    exit()

# Function to reshape and display Arabic text correctly
def format_arabic_text(text):
    reshaped_text = reshape(text)  # Reshape Arabic text
    bidi_text = get_display(reshaped_text)  # Apply bidirectional algorithm
    return bidi_text

# Function to create a badge
def create_badge(name, passport_number, birth_date, output_path, company_name, suppliers_name="", w_number="", s_number=""):
    # Find the photo by passport number (supports .jpg, .jpeg, .png)
    photo_path = None
    for ext in ['.jpg', '.jpeg', '.png']:
        possible_path = os.path.join(PHOTOS_FOLDER, f"{passport_number}{ext}")
        if os.path.exists(possible_path):
            photo_path = possible_path
            break
    
    if not photo_path:
        print(f"⚠️ لا توجد صورة لرقم الجواز: {passport_number}")
        return  # Skip this person if no photo exists

    # Open and resize the photo
    try:
        photo = Image.open(photo_path).resize((260, 270))  # Resize photo to fit the specified area
    except Exception as e:
        print(f"❌ خطأ في معالجة الصورة لـ {name}: {e}")
        return

    # Create a copy of the badge template
    badge = badge_template.copy()

    # Draw text on the badge
    draw = ImageDraw.Draw(badge)

    # Format and place the company name (from right to left)
    company_name_text = format_arabic_text(company_name)
    draw.text(((badge.width // 2), 50), company_name_text, font=font2, fill="black", anchor="ma")  # Company name placement (centered)

    # Format and place the name (from right to left)
    name_text = format_arabic_text(name)
    draw.text((695, 300), name_text, font=font, fill="black", anchor="ra")  # Name placement (right-aligned)

    # Format and place the birth date (from right to left)
    birth_date_text = format_arabic_text(birth_date)
    draw.text((690, 395), birth_date_text, font=font, fill="black", anchor="ra")  # Birth date placement (right-aligned)

    # Format and place the passport number (from right to left)
    passport_text = format_arabic_text(passport_number)
    draw.text((595, 580), passport_text, font=font, fill="black", anchor="ra")  # Passport number placement (right-aligned)

    # Format and place the MOTA3AHEDS name (from right to left)
    if suppliers_name:  # Only add if suppliers_name is not empty
        rect_box = (120, 700, 825, 825)  # Same dimensions as your oval box
        radius = 30  # Adjust corner roundness (higher = more rounded)

        # Draw rounded rectangle
        draw.rounded_rectangle(
            rect_box,
            radius=radius,
            outline="#ffa220",
            fill="#fcd672"  # Light yellow    
        )
        # Format supplier text
        supplier_title = "المتعهد:"
        supplier_title_text = format_arabic_text(supplier_title)
        text_x = rect_box[2] - 20  # 120px padding from right edge
        text_y = rect_box[1] + (rect_box[3] - rect_box[1] - n_font.size) // 2 - 15  # Moved up by 15 pixels
        
        draw.text(
            (text_x, text_y),
            supplier_title_text,
            font=n_font,
            fill="black",
            anchor="ra"  # Right alignment
        )

        supplier_text = format_arabic_text(suppliers_name)

        # Calculate text position (right-aligned inside the rectangle)
        text_x = rect_box[2] - 250  # 120px padding from right edge
        text_y = rect_box[1] + (rect_box[3] - rect_box[1] - n_font.size) // 2 - 15  # Moved up by 15 pixels
        
        draw.text(
            (text_x, text_y),
            supplier_text,
            font=n_font,
            fill="black",
            anchor="ra"  # Right alignment
        )

    # Format and place the WHATSAPP number (from right to left)
    if w_number:  # Only add if w_number is not empty
        w_number_text = format_arabic_text(w_number)
        draw.text((680, 845), w_number_text, font=n_font, fill="black", anchor="ra")  # Name placement (right-aligned)
    
    # Format and place the SAUDI number (from right to left)
    if s_number:  # Only add if s_number is not empty
        s_number_text = format_arabic_text(s_number)
        draw.text((610, 940), s_number_text, font=n_font, fill="black", anchor="ra")  # Name placement (right-aligned)

    # Paste the photo onto the badge (adjust position (x1, y1, x2, y2))
    badge.paste(photo, (60, 390, 320, 660))  # Adjusted photo placement coordinates

    # Save the badge
    try:
        badge.save(output_path)
        print(f"✅ تم إنشاء البادج لـ {name} في {output_path}")
    except Exception as e:
        print(f"❌ خطأ في حفظ البادج لـ {name}: {e}")

        
# Identify columns dynamically based on the first cell containing Arabic headers
name_column = None
birth_date_column = None
passport_column = None

for col in df.columns:
    if col == "الاسم":
        name_column = col
    elif "تاريخ الميلاد" in col:
        birth_date_column = col
    elif "رقم الجواز" in col:
        passport_column = col

if not name_column or not birth_date_column or not passport_column:
    print("❌ تأكد من وجود الأعمدة التالية في ملف الإكسل: الاسم, تاريخ الميلاد, رقم الجواز")
    exit()

# Remove the header row (since the first row contains the headers)
company_name = input("🏢 ادخل اسم الشركة: ")
suppliers_name = input("🏢 ادخل اسم المتعهد: ")
w_number = input("🏢 ادخل رقم الواتساب: ")
s_number = input("🏢 ادخل رقم السعودي: ")

# Loop through the Excel sheet and create badges
for index, row in df.iterrows():
    name = row[name_column]
    passport_number = row[passport_column]
    birth_date = row[birth_date_column]


    # Generate output file path
    output_path = os.path.join(OUTPUT_FOLDER, f"{name}_badge.png")
    
    # Create the badge
    create_badge(name, passport_number, birth_date, output_path, company_name,suppliers_name,w_number,s_number)


print("✨ تم إنشاء جميع البادجات بنجاح!")