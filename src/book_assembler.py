from fpdf import FPDF, XPos, YPos
import os
from PIL import Image

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
        
        # ==========================================
        # 1. FRONT COVER
        # ==========================================
        pdf.add_page()
        
        # Background: Pattern or Solid Color
        if cover_image_path and os.path.exists(cover_image_path):
            pdf.image(cover_image_path, x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM)
        else:
            pdf.set_fill_color(*rgb_color)
            pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')

        # Title Text: MASSIVE, BOLD, Centered directly on pattern
        # Placing it vertically in the center (approx 85mm down)
        pdf.set_font(PDF_FONT, 'B', 36) 
        pdf.set_text_color(0, 0, 0) 
        # Add a subtle white glow/stroke effect by printing slightly offset (optional hack), 
        # but standard black on pattern is what the user asked for.
        pdf.set_xy(10, 85) 
        pdf.multi_cell(w=PAGE_SIZE_MM - 20, h=14, text=title, align='C')

        
        # ==========================================
        # 2. STORY PAGES
        # ==========================================
        text_pages = story_text.split('\n\n')
        
        for i, text_page in enumerate(text_pages):
            pdf.add_page()
            
            # A. Background Color (Full Page)
            pdf.set_fill_color(*rgb_color)
            pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')
            
            # B. White "Polaroid" Frame (Rounded Rect)
            #    This creates the white background behind the image
            frame_margin = 15
            frame_width = PAGE_SIZE_MM - (frame_margin * 2) # 180mm
            frame_height = 135 # Height of the white box
            frame_y = 20
            
            pdf.set_fill_color(255, 255, 255) # White
            try:
                # Rounded corners for that soft look
                pdf.rounded_rect(x=frame_margin, y=frame_y, w=frame_width, h=frame_height, r=8, style='F')
            except AttributeError:
                pdf.rect(x=frame_margin, y=frame_y, w=frame_width, h=frame_height, style='F')
            
            # C. Image Placement (Centered Inside the White Frame)
            #    We add padding so the image doesn't touch the white edges
            padding = 10
            img_max_w = frame_width - (padding * 2)
            img_max_h = frame_height - (padding * 2)
            
            if i < len(image_list) and os.path.exists(image_list[i]):
                img_path = image_list[i]
                with Image.open(img_path) as img:
                    img_w_px, img_h_px = img.size
                
                # Calculate aspect ratio to fit INSIDE the padding
                aspect_ratio = img_h_px / img_w_px
                
                if (img_max_w * aspect_ratio) > img_max_h:
                    new_h = img_max_h
                    new_w = img_max_h / aspect_ratio
                else:
                    new_w = img_max_w
                    new_h = img_max_w * aspect_ratio

                # Center the image inside the white frame
                x_pos = frame_margin + padding + (img_max_w - new_w) / 2
                y_pos = frame_y + padding + (img_max_h - new_h) / 2
                
                pdf.image(img_path, x=x_pos, y=y_pos, w=new_w, h=new_h)
            
            # D. Text Placement (Below the White Frame)
            #    Bold text directly on the colored background
            pdf.set_font(PDF_FONT, 'B', 18) 
            pdf.set_text_color(0, 0, 0)
            
            # Position text starting 15mm below the frame
            text_y_start = frame_y + frame_height + 15
            pdf.set_xy(15, text_y_start)
            
            pdf.multi_cell(
                w=PAGE_SIZE_MM - 30, 
                h=9, 
                text=text_page, 
                align='C'
            )

        # ==========================================
        # 3. BACK COVER / END MESSAGE
        # ==========================================
        if end_message:
            pdf.add_page()
            
            # Background
            if cover_image_path and os.path.exists(cover_image_path):
                pdf.image(cover_image_path, x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM)
            else:
                pdf.set_fill_color(*rgb_color)
                pdf.rect(x=0, y=0, w=PAGE_SIZE_MM, h=PAGE_SIZE_MM, style='F')

            # End Message Text: Bold, Large, Centered directly on pattern
            # NO white box here.
            pdf.set_font(PDF_FONT, 'B', 24)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(15, 90) 
            pdf.multi_cell(w=PAGE_SIZE_MM - 30, h=12, text=end_message, align='C')

        # Finalize
        pdf._page_count = pdf.page_no() 
        pdf.output(output_filename)
        print(f"...PDF assembly complete. Pages created: {pdf.page_no()}")
        return True

    except Exception as e:
        print(f"[Error] Failed to create PDF: {e}")
        return False