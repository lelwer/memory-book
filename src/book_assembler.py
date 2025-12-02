from fpdf import FPDF
import os
from PIL import Image # We need this to read image sizes

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
            self.set_font(PDF_FONT, 'I', 8) 
            self.set_text_color(0, 0, 0) 
            self.cell(0, 10, f"Page {self.page_no() - 1}", 0, 0, 'C')

    @property
    def page_count(self):
        try:
            return self._page_count
        except AttributeError:
            return 0


def create_pdf(title, story_text, image_list, end_message, cover_image_path, theme_color, output_filename):
    """
    Assembles the story text and images into a single PDF file.
    """
    print(f"Assembling PDF at: {output_filename}")
    
    try:
        pdf = PDF(orientation='P', unit='mm', format=(PAGE_SIZE_MM, PAGE_SIZE_MM))
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font(PDF_FONT)
        pdf._page_count = 0 
        
        rgb_color = COLOR_MAP.get(theme_color.lower(), (255, 255, 255))
        
        # --- START FIX (Problem #3) ---
        # --- Title Page with Pattern Background ---
        pdf.add_page()
        if cover_image_path and os.path.exists(cover_image_path):
            pdf.image(cover_image_path, x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM)
        else:
            pdf.set_fill_color(*rgb_color)
            pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')

        # --- RE-ADDING the white "bookplate" (rounded rectangle) for readability ---
        pdf.set_fill_color(255, 255, 255) # White
        try:
            pdf.rounded_rect(x=30, y=80, w=PAGE_SIZE_MM - 60, h=50, r=10, style='F')
        except AttributeError:
            print("[Warning] rounded_rect not found. Using sharp rectangle.")
            pdf.rect(x=30, y=80, w=PAGE_SIZE_MM - 60, h=50, style='F')
        
        # Draw the title text (in black, centered)
        pdf.set_font(PDF_FONT, 'B', 24) # Bold, 24pt
        pdf.set_text_color(0, 0, 0) # Black text
        pdf.set_xy(30, 90) # Position text
        pdf.multi_cell(w=PAGE_SIZE_MM - 60, h=15, text=title, align='C')
        # --- END FIX ---

        
        # --- Story Pages (This layout is working well) ---
        text_pages = story_text.split('\n\n')
        
        for i, text_page in enumerate(text_pages):
            pdf.add_page()
            
            # 1. Set the page background to the theme color
            pdf.set_fill_color(*rgb_color)
            pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')
            
            # --- 2. Image (Preserving Aspect Ratio) ---
            image_area_width = PAGE_SIZE_MM - 20  # 190mm
            image_area_height = PAGE_SIZE_MM - 70 # 140mm
            
            if i < len(image_list) and os.path.exists(image_list[i]):
                img_path = image_list[i]
                with Image.open(img_path) as img:
                    img_w_px, img_h_px = img.size
                
                aspect_ratio = img_h_px / img_w_px
                
                if (image_area_width * aspect_ratio) > image_area_height:
                    new_h = image_area_height
                    new_w = image_area_height / aspect_ratio
                else:
                    new_w = image_area_width
                    new_h = image_area_width * aspect_ratio

                x_pos = 10 + (image_area_width - new_w) / 2
                y_pos = 10 + (image_area_height - new_h) / 2
                
                pdf.image(img_path, x=x_pos, y=y_pos, w=new_w, h=new_h)
                
            else:
                # Placeholder box
                pdf.set_fill_color(200, 200, 200) 
                pdf.rect(x=10, y=10, w=image_area_width, h=image_area_height, style='F')
            
            # 3. Text on bottom 1/3
            pdf.set_font(PDF_FONT, 'B', 16) # Bold
            pdf.set_text_color(0, 0, 0) # Black text
            pdf.set_xy(10, PAGE_SIZE_MM - 55) # Y-position for text
            pdf.multi_cell(
                w=PAGE_SIZE_MM - 20, # 10mm margins
                h=8, 
                text=text_page, 
                align='C'
            )

        # --- START FIX (Problem #4) ---
        # --- End Message Page ---
        if end_message:
            pdf.add_page()
            if cover_image_path and os.path.exists(cover_image_path):
                pdf.image(cover_image_path, x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM)
            else:
                pdf.set_fill_color(*rgb_color)
                pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')

            # --- RE-ADDING the white "bookplate" ---
            pdf.set_fill_color(255, 255, 255) # White
            try:
                pdf.rounded_rect(x=30, y=80, w=PAGE_SIZE_MM - 60, h=50, r=10, style='F')
            except AttributeError:
                pdf.rect(x=30, y=80, w=PAGE_SIZE_MM - 60, h=50, style='F')

            # --- Use Bold as requested, and larger ---
            pdf.set_font(PDF_FONT, 'B', 20) # Bold, 20pt
            pdf.set_text_color(0, 0, 0) # Black text
            pdf.set_xy(30, 95) 
            pdf.multi_cell(w=PAGE_SIZE_MM - 60, h=10, text=end_message, align='C')
        # --- END FIX ---
        
        pdf._page_count = pdf.page_no() 
        pdf.output(output_filename)
        print(f"...PDF assembly complete. Pages created: {pdf.page_no()}")
        return True

    except Exception as e:
        print(f"[Error] Failed to create PDF: {e}")
        return False