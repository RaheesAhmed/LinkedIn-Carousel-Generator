import os
import json
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Use relative imports within the package
from .themes import get_theme_config, get_available_themes
from .utils import (create_output_dir, create_pdf, save_carousel_data, 
                   draw_icon, select_icon, add_slide_number_indicator)
from .templates import TEMPLATE_FACTORIES, create_gradient_template

load_dotenv()

class CarouselGenerator:
    def __init__(self, theme="default", output_dir="output"):
        self.carousel_data = {}
        self.output_dir = output_dir
        self.set_theme(theme)
        create_output_dir(self.output_dir)

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self.theme_config = get_theme_config(theme_name)
        self.theme_colors = (
            self.theme_config["primary_color"],
            self.theme_config["secondary_color"],
            self.theme_config["accent_color"]
        )
        self.template_type = self.theme_config["template"]

    def generate_template(self, slide_number):
        """Generate a slide template based on the theme"""
        template_func = TEMPLATE_FACTORIES.get(self.template_type, create_gradient_template)
        return template_func(slide_number, self.theme_config, self.theme_colors)

    def create_slide(self, heading, content, slide_number, logo_path=None, custom_text_color=None):
        """Create a slide using a template"""
        image = self.generate_template(slide_number)
        draw = ImageDraw.Draw(image)
        
        text_color = custom_text_color if custom_text_color else self.theme_config["text_color"]
        heading_font_size = self.theme_config["heading_font_size"]
        content_font_size = self.theme_config["content_font_size"]
        
        try:
            heading_font = ImageFont.truetype("arial.ttf", heading_font_size)
            content_font = ImageFont.truetype("arial.ttf", content_font_size)
        except IOError:
            heading_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        width, height = self.theme_config["slide_size"]
        
        # Add heading (centered)
        draw.text((width//2, height//6), heading, fill=text_color, font=heading_font, anchor="mm")
        
        # Draw icon
        icon_type = select_icon(heading)
        draw_icon(
            draw,
            icon_type,
            (width//6, height//2.5),
            120,
            self.theme_config["accent_color"]
        )
        
        # Add content as bullet points
        y_position = height//2.5
        content_lines = content.split('\n')
        for line in content_lines:
            if line.strip():
                bullet_size = 10
                draw.ellipse(
                    [(width//3 - bullet_size - 10, y_position + content_font_size//2 - bullet_size//2),
                     (width//3 - 10, y_position + content_font_size//2 + bullet_size//2)],
                    fill=text_color
                )
                draw.text((width//3, y_position), line.strip(), fill=text_color, font=content_font)
                y_position += content_font_size + 20
        
        # Add logo
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert("RGBA") # Ensure RGBA for transparency
                logo = logo.resize((100, 100))
                image.paste(logo, (width - 120, height - 120), logo)
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        # Save the slide
        slide_path = os.path.join(self.output_dir, f"slide_{slide_number}.png")
        image.save(slide_path)
        return slide_path

    def generate_carousel(self, title, slides_content, logo_path=None, custom_text_color=None):
        """Generate a full LinkedIn carousel"""
        self.carousel_data = {
            "title": title,
            "theme": self.theme_name,
            "slides": []
        }
        
        slide_paths = []
        for i, slide in enumerate(slides_content, 1):
            slide_path = self.create_slide(
                slide.get("heading", ""),
                slide.get("content", ""),
                i,
                logo_path,
                custom_text_color
            )
            slide_paths.append(slide_path)
            
            self.carousel_data["slides"].append({
                "number": i,
                "heading": slide.get("heading", ""),
                "content": slide.get("content", ""),
                "image_path": slide_path
            })
        
        pdf_path = create_pdf(slide_paths, title, self.output_dir)
        json_path = save_carousel_data(self.carousel_data, title, self.output_dir)
        
        return {
            "pdf_path": pdf_path,
            "json_path": json_path,
            "slide_paths": slide_paths
        }

    def get_available_themes(self):
        return get_available_themes() 