import fitz  # PyMuPDF
from PIL import Image, ImageChops
import os

def crop_whitespace(im, border_color=(255, 255, 255)):
    """Crop white margins around the image."""
    bg = Image.new(im.mode, im.size, border_color)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def convert_pdf_to_images(pdf_path, resize_factor=0.8):
    print(f"\nOpening PDF file: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    images = []
    total_pages = len(doc)

    for page_num in range(1, total_pages):  # Skip first slide
        page = doc.load_page(page_num)
        print(f"Converting page {page_num + 1}")
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Crop white space and resize
        cropped_img = crop_whitespace(img)
        W, H = cropped_img.size
        resized_img = cropped_img.resize(
            (int(W * resize_factor), int(H * resize_factor)),
            resample=Image.Resampling.LANCZOS
        )
        images.append(resized_img)

    print(f"Converted {len(images)} pages to processed images.")
    return images

def arrange_images_in_grid(images, rows, cols, output_pdf_path):
    if not images:
        print("No images to arrange.")
        return

    print(f"Arranging images in {rows}x{cols} grid (vertical layout).")
    W, H = images[0].size
    page_width = cols * W
    page_height = rows * H
    grid_pages = []

    total_grid_size = rows * cols
    total_images = len(images)
    used_images = set()

    for i in range(0, total_images, total_grid_size):
        print(f"Creating grid for slides {i + 1} to {min(i + total_grid_size, total_images)}")
        images_on_page = images[i:i + total_grid_size]

        # Avoid re-using already placed images
        images_on_page = [img for j, img in enumerate(images_on_page, start=i) if j not in used_images]
        used_images.update(range(i, i + len(images_on_page)))

        canvas = Image.new('RGB', (page_width, page_height), 'white')

        for index, img in enumerate(images_on_page):
            row = index % rows
            col = index // rows
            canvas.paste(img, (col * W, row * H))

        grid_pages.append(canvas)

    try:
        print(f"Saving to {output_pdf_path}")
        grid_pages[0].save(output_pdf_path, save_all=True, append_images=grid_pages[1:])
        print("Saved successfully.")
    except Exception as e:
        print(f"Error saving PDF: {e}")

def process_all_pdfs_in_folder(folder_path, rows=4, cols=2, resize_factor=0.8):
    print(f"Scanning folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            input_pdf_path = os.path.join(folder_path, filename)
            base_name = os.path.splitext(filename)[0]
            output_pdf_path = os.path.join(folder_path, f"{base_name}_update.pdf")

            images = convert_pdf_to_images(input_pdf_path, resize_factor=resize_factor)
            arrange_images_in_grid(images, rows, cols, output_pdf_path)

# ✅ USAGE
folder_path = r"xyz"  # Change to your folder path
process_all_pdfs_in_folder(folder_path, rows=4, cols=2, resize_factor=0.8)
