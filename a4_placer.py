from PIL import Image
import os

# Constants
A4_WIDTH = 3508  # A4 width in pixels (300 DPI)
A4_HEIGHT = 2480  # A4 height in pixels (300 DPI)
BADGE_WIDTH = 945  # Width of each badge (adjust based on your badge size)
BADGE_HEIGHT = 1181  # Height of each badge (adjust based on your badge size)
MARGIN = 50  # Margin around the A4 sheet
SPACING = 30  # Spacing between badges

# Folder containing badges
BADGES_FOLDER = input("📁 ادخل مسار مجلد البادجات: ")
# Output folder for A4 sheets
OUTPUT_FOLDER = input("📁 ادخل مسار مجلد الناتج النهائي: ")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Get list of badge files
badge_files = [os.path.join(BADGES_FOLDER, f) for f in os.listdir(BADGES_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))]
badge_files.sort()  # Sort to ensure consistent ordering

# Function to create an A4 sheet with 6 badges
def create_a4_sheet(badges, output_path):
    # Create a blank A4 sheet
    a4_sheet = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")

    # Paste badges onto the A4 sheet
    for i, badge_path in enumerate(badges):
        # Calculate row and column
        row = i // 3  # 3 badges per row
        col = i % 3  # 3 columns

        # Calculate position
        x = MARGIN + col * (BADGE_WIDTH + SPACING)
        y = MARGIN + row * (BADGE_HEIGHT + SPACING)

        # Open the badge
        badge = Image.open(badge_path)

        # Resize badge if necessary (optional)
        badge = badge.resize((BADGE_WIDTH, BADGE_HEIGHT))

        # Paste the badge onto the A4 sheet
        a4_sheet.paste(badge, (x, y))

    # Save the A4 sheet
    a4_sheet.save(output_path)
    print(f"✅ Saved A4 sheet: {output_path}")

# Process badges in batches of 6
for i in range(0, len(badge_files), 6):
    # Get 6 badges for one A4 sheet
    badges = badge_files[i:i + 6]

    # Create A4 sheet
    output_path = os.path.join(OUTPUT_FOLDER, f"a4_sheet_{i // 6 + 1}.png")
    create_a4_sheet(badges, output_path)

print("✨ All A4 sheets created successfully!")
