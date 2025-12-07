from fpdf import FPDF, XPos, YPos
import os
import random
import math
from PIL import Image, ImageDraw

PDF_FONT = "Helvetica" 
PAGE_SIZE_MM = 210 # 210mm x 210mm square

COLOR_MAP = {
    "light blue": (204, 229, 255),
    "light pink": (255, 204, 229),
    "light green": (204, 255, 204),
    "light yellow": (255, 255, 204),
    "light gray": (230, 230, 230),
    "white": (255, 255, 255)
}

class PDF(FPDF):
    """ Custom PDF class to handle headers and footers. """
    def footer(self):
        """ Renders the page number at the bottom of each page. """
        if self.page_no() > 1 and self.page_no() < self.page_count:
            self.set_y(-15) 
            self.set_font(PDF_FONT, 'I', 10) 
            self.set_text_color(0, 0, 0) 
            self.cell(0, 10, f"{self.page_no() - 1}", border=0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

    @property
    def page_count(self):
        try:
            return self._page_count
        except AttributeError:
            return 0

def create_rough_mask(size, wobble=3):
    """
    Generates a mask with slightly 'wobbly' hand-drawn edges.
    USES A FIXED SEED so every page looks exactly the same.
    """
    # ---------------------------------------------------------
    # CRITICAL FIX: Fixed seed ensures consistency across pages
    random.seed(42) 
    # ---------------------------------------------------------
    
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Generate points for a wobbly rectangle
    points = []
    steps = 40 
    
    # Top edge
    for x in range(0, width, width // steps):
        points.append((x, random.randint(0, wobble)))
    points.append((width, 0))
    
    # Right edge
    for y in range(0, height, height // steps):
        points.append((width - random.randint(0, wobble), y))
    points.append((width, height))
    
    # Bottom edge
    for x in range(width, 0, -(width // steps)):
        points.append((x, height - random.randint(0, wobble)))
    points.append((0, height))

    # Left edge
    for y in range(height, 0, -(height // steps)):
        points.append((random.randint(0, wobble), y))
        
    draw.polygon(points, fill=255)
    return mask

def style_image_organic(image_path):
    """
    Applies a rough/organic mask to the image.
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            
            # Create the wobbly mask (Wobble size set to 5 for visible effect)
            mask = create_rough_mask(img.size, wobble=5)
            
            img.putalpha(mask)
            
            dir_name = os.path.dirname(image_path)
            base_name = os.path.basename(image_path)
            temp_name = os.path.join(dir_name, f"organic_{base_name}")
            
            img.save(temp_name, format="PNG")
            return temp_name
    except Exception as e:
        print(f"[Warning] Could not style image: {e}")
        return image_path

def calculate_optimal_font_size(pdf, text, max_width, max_height):
    """
    Iteratively reduces font size until the text fits within the max_height.
    """
    size = 18 # Start big
    min_size = 10
    
    while size >= min_size:
        pdf.set_font(PDF_FONT, 'B', size)
        
        # Calculate how many lines this text will take
        lines = pdf.multi_cell(w=max_width, h=size/2, text=text, split_only=True)
        num_lines = len(lines)
        
        # Approximate height
        line_height_mm = size * 0.45 
        total_height = num_lines * line_height_mm
        
        if total_height <= max_height:
            return size, line_height_mm
            
        size -= 1
        
    return min_size, (min_size * 0.45)

def create_pdf(title, story_text, image_list, end_message, cover_image_path, theme_color, output_filename):
    print(f"Assembling PDF at: {output_filename}")
    
    try:
        pdf = PDF(orientation='P', unit='mm', format=(PAGE_SIZE_MM, PAGE_SIZE_MM))
        pdf.set_auto_page_break(auto=False) 
        pdf.set_font(PDF_FONT)
        pdf._page_count = 0 
        
        rgb_color = COLOR_MAP.get(theme_color.lower(), (255, 255, 255))
        
        # ==========================================
        # 1. FRONT COVER
        # ==========================================
        pdf.add_page()
        if cover_image_path and os.path.exists(cover_image_path):
            pdf.image(cover_image_path, x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM)
        else:
            pdf.set_fill_color(*rgb_color)
            pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')

        # Title: Massive & Bold
        pdf.set_font(PDF_FONT, 'B', 42) 
        pdf.set_text_color(0, 0, 0) 
        pdf.set_xy(10, 80) 
        pdf.multi_cell(w=PAGE_SIZE_MM - 20, h=16, text=title, align='C')
        
        # ==========================================
        # 2. STORY PAGES
        # ==========================================
        text_pages = story_text.split('\n\n')
        
        for i, text_page in enumerate(text_pages):
            pdf.add_page()
            
            # A. Background
            pdf.set_fill_color(*rgb_color)
            pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')
            
            # B. Image Frame 
            sq_size = 140 
            frame_y = 15 
            frame_x = (PAGE_SIZE_MM - sq_size) / 2
            
            pdf.set_fill_color(255, 255, 255)
            
            try:
                pdf.rounded_rect(x=frame_x, y=frame_y, w=sq_size, h=sq_size, r=5, style='F')
            except AttributeError:
                pdf.rect(x=frame_x, y=frame_y, w=sq_size, h=sq_size, style='F')
            
            # C. Image Placement (Organic Style)
            if i < len(image_list) and os.path.exists(image_list[i]):
                styled_img_path = style_image_organic(image_list[i])
                
                with Image.open(styled_img_path) as img:
                    img_w_px, img_h_px = img.size
                
                padding = 5 
                img_max_size = sq_size - (padding * 2) 
                
                aspect_ratio = img_h_px / img_w_px
                if aspect_ratio > 1:
                    new_h = img_max_size
                    new_w = img_max_size / aspect_ratio
                else:
                    new_w = img_max_size
                    new_h = img_max_size * aspect_ratio

                img_x = frame_x + padding + (img_max_size - new_w) / 2
                img_y = frame_y + padding + (img_max_size - new_h) / 2
                
                pdf.image(styled_img_path, x=img_x, y=img_y, w=new_w, h=new_h)
                
                if "organic_" in styled_img_path:
                    try:
                        os.remove(styled_img_path)
                    except: pass
            
            # D. Auto-Fit Text
            space_below = PAGE_SIZE_MM - (frame_y + sq_size) - 15 
            text_x = 15
            text_width = PAGE_SIZE_MM - 30
            
            opt_size, line_height = calculate_optimal_font_size(pdf, text_page, text_width, space_below)
            
            pdf.set_font(PDF_FONT, 'B', opt_size)
            pdf.set_text_color(0, 0, 0)
            
            lines = pdf.multi_cell(w=text_width, h=line_height, text=text_page, split_only=True)
            block_height = len(lines) * line_height
            
            text_y_start = (frame_y + sq_size) + (space_below - block_height) / 2
            
            pdf.set_xy(text_x, text_y_start)
            pdf.multi_cell(w=text_width, h=line_height, text=text_page, align='C')

        # ==========================================
        # 3. BACK COVER
        # ==========================================
        if end_message:
            pdf.add_page()
            if cover_image_path and os.path.exists(cover_image_path):
                pdf.image(cover_image_path, x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM)
            else:
                pdf.set_fill_color(*rgb_color)
                pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')

            pdf.set_font(PDF_FONT, 'BI', 24)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(15, 90) 
            pdf.multi_cell(w=PAGE_SIZE_MM - 30, h=10, text=end_message, align='C')

        pdf._page_count = pdf.page_no() 
        pdf.output(output_filename)
        print(f"...PDF assembly complete. Pages created: {pdf.page_no()}")
        return True

    except Exception as e:
        print(f"[Error] Failed to create PDF: {e}")
        return False