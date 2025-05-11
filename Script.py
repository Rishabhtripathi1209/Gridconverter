import fitz  # PyMuPDF
from PIL import Image
import os

def convert_pdf_to_images(pdf_path):
    print(f"Opening PDF file: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    images = []
    total_pages = len(doc)
    
    # Skip the first page
    for page_num in range(1, total_pages):  # Start from 1 to skip the first page
        page = doc.load_page(page_num)
        print(f"Converting page {page_num + 1}")  # Showing the actual page number (after skipping)
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    
    print(f"Converted {len(images)} pages to images.")
    return images

def arrange_images_in_grid(images, rows, cols, output_pdf_path):
    if not images:
        print("No images to arrange. Exiting.")
        return

    print(f"Arranging images in a {rows}x{cols} grid (4x2 - Up-Down Layout).")
    W, H = images[0].size
    page_width = cols * W  # Width of page, based on columns
    page_height = rows * H  # Height of page, based on rows
    grid_pages = []

    # Handle images in chunks of rows * cols, ensure last page does not repeat images
    total_images = len(images)
    total_grid_size = rows * cols

    # Loop through images in chunks of rows * cols, ensure no repeats
    for i in range(0, total_images, total_grid_size):
        print(f"Creating grid for pages {i + 1} to {i + total_grid_size}")
        
        # Only take the remaining images for the last page (without repeating)
        images_on_page = images[i:i + total_grid_size]
        canvas = Image.new('RGB', (page_width, page_height), 'white')

        num_images = len(images_on_page)

        # Place images vertically in a 4x2 grid (up-down layout)
        for index, img in enumerate(images_on_page):
            row = index % rows  # Vertical positioning (next rows)
            col = index // rows  # Horizontal positioning (columns)
            canvas.paste(img, (col * W, row * H))  # Place image in correct position

        # Add the canvas to the grid pages
        grid_pages.append(canvas)

    # Save as PDF
    if grid_pages:
        print(f"Saving grid pages to {output_pdf_path}")
        try:
            grid_pages[0].save(output_pdf_path, save_all=True, append_images=grid_pages[1:])
            print("PDF saved successfully.")
        except Exception as e:
            print(f"Error saving PDF: {e}")
    else:
        print("No grid pages to save.")

# ✅ Usage

# Ensure the output PDF path includes the file name and extension
pdf_file = r"D:\nervous system structure\SkeletalMuscle_1.pdf"
output_pdf = r"D:\nervous system structure\grid_output_4x2_up_down_corrected.pdf"  # Ensure the file name ends with .pdf

# Convert PDF to images (skipping the first page)
images = convert_pdf_to_images(pdf_file)

# Arrange images in a 4x2 vertical grid and save as PDF
arrange_images_in_grid(images, rows=4, cols=2, output_pdf_path=output_pdf)
