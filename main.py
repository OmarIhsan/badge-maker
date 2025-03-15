import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Get current script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths (automatically set to script directory)
BADGE_TEMPLATE = os.path.join(SCRIPT_DIR, "badge_template.jpg")
FONT_FILE = os.path.join(SCRIPT_DIR, "TheSans Bold.ttf")

# Function to reshape and display Arabic text correctly
def format_arabic_text(text):
    reshaped_text = reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_badge(name, passport_number, birth_date, output_path, company_name, suppliers_name="", w_number="", s_number=""):
    # Find the photo by passport number
    photo_path = None
    for ext in ['.jpg', '.jpeg', '.png']:
        possible_path = os.path.join(PHOTOS_FOLDER, f"{passport_number}{ext}")
        if os.path.exists(possible_path):
            photo_path = possible_path
            break
    
    if not photo_path:
        print(f"⚠️ لا توجد صورة لرقم الجواز: {passport_number}")
        return None

    try:
        photo = Image.open(photo_path).resize((260, 270))
    except Exception as e:
        print(f"❌ خطأ في معالجة الصورة لـ {name}: {e}")
        return None

    try:
        badge = badge_template.copy()
    except Exception as e:
        messagebox.showerror("خطأ", f"❌ تعذر تحميل قالب البادج: {e}")
        return None

    draw = ImageDraw.Draw(badge)

    # Company name
    company_name_text = format_arabic_text(company_name)
    draw.text(((badge.width // 2), 50), company_name_text, font=font2, fill="black", anchor="ma")

    # Name
    name_text = format_arabic_text(name)
    draw.text((695, 300), name_text, font=font, fill="black", anchor="ra")

    # Birth date
    birth_date_text = format_arabic_text(str(birth_date))
    draw.text((690, 395), birth_date_text, font=font, fill="black", anchor="ra")

    # Passport number
    passport_text = format_arabic_text(passport_number)
    draw.text((595, 580), passport_text, font=font, fill="black", anchor="ra")

    if suppliers_name:
        rect_box = (120, 700, 825, 825)
        radius = 30
        draw.rounded_rectangle(rect_box, radius=radius, outline="#ffa220", fill="#fcd672")
        
        supplier_title = format_arabic_text("المتعهد:")
        draw.text((rect_box[2]-20, rect_box[1]+30), supplier_title, font=n_font, fill="black", anchor="ra")
        
        supplier_text = format_arabic_text(suppliers_name)
        draw.text((rect_box[2]-250, rect_box[1]+30), supplier_text, font=n_font, fill="black", anchor="ra")

    if w_number:
        w_number_text = format_arabic_text(w_number)
        draw.text((680, 845), w_number_text, font=n_font, fill="black", anchor="ra")
    
    if s_number:
        s_number_text = format_arabic_text(s_number)
        draw.text((610, 940), s_number_text, font=n_font, fill="black", anchor="ra")

    badge.paste(photo, (60, 390, 320, 660))

    try:
        badge.save(output_path)
        print(f"✅ تم إنشاء البادج لـ {name} في {output_path}")
    except Exception as e:
        print(f"❌ خطأ في حفظ البادج لـ {name}: {e}")

    return badge

def generate_badges():
    global PHOTOS_FOLDER, badge_template, font, font2, n_font

    # Get values from UI
    EXCEL_FILE = excel_file_entry.get()
    PHOTOS_FOLDER = photos_folder_entry.get()
    OUTPUT_FOLDER = output_folder_entry.get()
    company_name = company_name_entry.get()
    suppliers_name = suppliers_name_entry.get()
    w_number = whatsapp_number_entry.get()
    s_number = saudi_number_entry.get()

    # Validate required fields
    if not all([EXCEL_FILE, PHOTOS_FOLDER, OUTPUT_FOLDER, company_name]):
        messagebox.showerror("خطأ", "❌ الرجاء ملء جميع الحقول المطلوبة")
        return

    try:
        # Load resources
        badge_template = Image.open(BADGE_TEMPLATE)
        font = ImageFont.truetype(FONT_FILE, 50)
        font2 = ImageFont.truetype(FONT_FILE, 57)
        n_font = ImageFont.truetype(FONT_FILE, 57)
    except Exception as e:
        messagebox.showerror("خطأ", f"❌ خطأ في تحميل الملفات الأساسية: {e}")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        messagebox.showerror("خطأ", f"❌ خطأ في تحميل ملف الإكسل: {e}")
        return

    # Find required columns
    required_columns = {"الاسم": None, "تاريخ الميلاد": None, "رقم الجواز": None}
    for col in df.columns:
        if col in required_columns:
            required_columns[col] = col

    if None in required_columns.values():
        missing = [k for k, v in required_columns.items() if v is None]
        messagebox.showerror("خطأ", f"❌ الأعمدة الناقصة: {', '.join(missing)}")
        return

    # Create badges
    badge_files = []
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    for index, row in df.iterrows():
        name = row[required_columns["الاسم"]]
        passport = row[required_columns["رقم الجواز"]]
        birth_date = row[required_columns["تاريخ الميلاد"]]
        
        output_path = os.path.join(OUTPUT_FOLDER, f"{name}_badge.png")
        badge = create_badge(name, passport, birth_date, output_path, 
                           company_name, suppliers_name, w_number, s_number)
        if badge:
            badge_files.append(output_path)

    # Create A4 sheets
    A4_WIDTH = 3508
    A4_HEIGHT = 2480
    BADGE_SIZE = (945, 1181)
    
    for i in range(0, len(badge_files), 6):
        a4_sheet = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
        for j, path in enumerate(badge_files[i:i+6]):
            row = j // 3
            col = j % 3
            x = 50 + col * (BADGE_SIZE[0] + 30)
            y = 50 + row * (BADGE_SIZE[1] + 30)
            
            try:
                badge = Image.open(path).resize(BADGE_SIZE)
                a4_sheet.paste(badge, (x, y))
            except Exception as e:
                print(f"❌ خطأ في تحميل البادج {path}: {e}")
        
        output_path = os.path.join(OUTPUT_FOLDER, f"a4_sheet_{i//6 + 1}.png")
        a4_sheet.save(output_path)
        print(f"✅ تم حفظ صفحة A4: {output_path}")

    messagebox.showinfo("نجاح", "✨ تم إنشاء جميع البادجات وصفحات A4 بنجاح!")

def browse_file(entry):
    filename = filedialog.askopenfilename()
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def browse_folder(entry):
    foldername = filedialog.askdirectory()
    if foldername:
        entry.delete(0, tk.END)
        entry.insert(0, foldername)

# Create main window
root = tk.Tk()
root.title("إنشاء البادجات")

# Create UI elements
fields = [
    ("🏢 ملف الإكسل:", excel_file_entry := tk.Entry(width=40)),
    ("📸 مجلد الصور:", photos_folder_entry := tk.Entry(width=40)),
    ("📁 مجلد الحفظ:", output_folder_entry := tk.Entry(width=40)),
    ("🏢 اسم الشركة:", company_name_entry := tk.Entry(width=40)),
    ("🏢 اسم المتعهد:", suppliers_name_entry := tk.Entry(width=40)),
    ("🏢 رقم الواتساب:", whatsapp_number_entry := tk.Entry(width=40)),
    ("🏢 رقم السعودي:", saudi_number_entry := tk.Entry(width=40)),
]

for i, (label, entry) in enumerate(fields):
    tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='e')
    entry.grid(row=i, column=1, padx=10, pady=5)
    if i == 0:  # Browse file for Excel
        tk.Button(root, text="تصفح", command=lambda e=entry: browse_file(e)).grid(row=i, column=2, padx=10, pady=5)
    elif i in [1, 2]:  # Browse folder for Photos and Output
        tk.Button(root, text="تصفح", command=lambda e=entry: browse_folder(e)).grid(row=i, column=2, padx=10, pady=5)

generate_btn = tk.Button(root, text="إنشاء البادجات", command=generate_badges, bg='#4CAF50', fg='white')
generate_btn.grid(row=len(fields), column=1, pady=20, sticky='ew')

# Add status label
status_label = tk.Label(root, text="", fg='green')
status_label.grid(row=len(fields)+1, column=0, columnspan=3)

root.mainloop()
