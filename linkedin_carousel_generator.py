import os
import json
import uuid
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
import base64
import io
import mimetypes
from google import genai
from google.genai import types
import random

load_dotenv()

class LinkedInCarouselGenerator:
    def __init__(self, theme="default"):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.generated_images = []
        self.carousel_data = {}
        self.output_dir = "output"
        
        # Set theme
        self.theme = theme
        self.themes = {
            "default": {
                "text_color": (255, 255, 255),
                "heading_font_size": 60,
                "content_font_size": 40,
                "slide_size": (1080, 1080),
                "prompt_style": "corporate style, minimal design, with soft colors appropriate for business content",
                "bg_color": (52, 152, 219),  # Blue
                "gradient_color": (41, 128, 185)  # Darker blue
            },
            "dark": {
                "text_color": (220, 220, 220),
                "heading_font_size": 65,
                "content_font_size": 45,
                "slide_size": (1080, 1080),
                "prompt_style": "dark theme, modern business style with bold contrasts and minimal design",
                "bg_color": (44, 62, 80),  # Dark blue
                "gradient_color": (52, 73, 94)  # Slightly lighter dark blue
            },
            "light": {
                "text_color": (50, 50, 50),
                "heading_font_size": 60,
                "content_font_size": 40,
                "slide_size": (1080, 1080),
                "prompt_style": "light theme, bright and airy design, subtle pastel colors, professional and clean",
                "bg_color": (236, 240, 241),  # Light gray
                "gradient_color": (189, 195, 199)  # Slightly darker light gray
            },
            "creative": {
                "text_color": (240, 240, 240),
                "heading_font_size": 70,
                "content_font_size": 45,
                "slide_size": (1080, 1080),
                "prompt_style": "creative style, artistic design with vibrant colors, innovative layout, suitable for creative industries",
                "bg_color": (155, 89, 182),  # Purple
                "gradient_color": (142, 68, 173)  # Darker purple
            },
            "tech": {
                "text_color": (200, 230, 255),
                "heading_font_size": 65,
                "content_font_size": 40,
                "slide_size": (1080, 1080),
                "prompt_style": "tech theme, digital aesthetic with blue tones, futuristic design elements, minimal and sleek",
                "bg_color": (52, 152, 219),  # Blue
                "gradient_color": (25, 97, 142)  # Darker tech blue
            }
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_background_image(self, prompt, custom_style=None):
        """Generate a background image with a simple gradient based on theme"""
        # Get colors from theme
        bg_color = self.themes[self.theme]["bg_color"]
        gradient_color = self.themes[self.theme]["gradient_color"]
        
        # Create a new image with gradient background
        width, height = self.themes[self.theme]["slide_size"]
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create a simple gradient background
        for y in range(height):
            # Calculate ratio of position (0 at top, 1 at bottom)
            ratio = y / height
            # Calculate color at this position by linear interpolation
            r = int(bg_color[0] * (1 - ratio) + gradient_color[0] * ratio)
            g = int(bg_color[1] * (1 - ratio) + gradient_color[1] * ratio)
            b = int(bg_color[2] * (1 - ratio) + gradient_color[2] * ratio)
            
            # Draw a line with this color
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add some subtle pattern or texture based on theme
        if self.theme == "tech":
            # Add some circuit-like lines for tech theme
            for _ in range(20):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(max(0, x1-200), min(width, x1+200))
                y2 = random.randint(max(0, y1-200), min(height, y1+200))
                line_color = (max(bg_color[0]-30, 0), max(bg_color[1]-30, 0), max(bg_color[2]-30, 0))
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)
        
        # Generate a unique filename
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"{self.output_dir}/bg_image_{unique_id}"
        full_path = f"{file_name}.png"
        
        # Save the image file
        image.save(full_path)
        print(f"Background image saved to: {full_path}")
        
        return full_path, None
    
    def create_slide(self, background_image_path, heading, content, slide_number, logo_path=None, custom_text_color=None):
        """Create a slide using PIL"""
        # Open the background image
        bg = Image.open(background_image_path)
        
        # Resize to the slide size from theme
        slide_size = self.themes[self.theme]["slide_size"]
        bg = bg.resize(slide_size)
        
        # Create a drawing context
        draw = ImageDraw.Draw(bg)
        
        # Get colors and font sizes from theme
        text_color = custom_text_color if custom_text_color else self.themes[self.theme]["text_color"]
        heading_font_size = self.themes[self.theme]["heading_font_size"]
        content_font_size = self.themes[self.theme]["content_font_size"]
        
        # Try to load fonts, use default if not available
        try:
            heading_font = ImageFont.truetype("arial.ttf", heading_font_size)
            content_font = ImageFont.truetype("arial.ttf", content_font_size)
        except IOError:
            heading_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # Add slide number
        draw.text((50, 50), f"Slide {slide_number}", fill=text_color, font=content_font)
        
        # Add heading (centered)
        width, height = slide_size
        draw.text((width//2, height//5), heading, fill=text_color, font=heading_font, anchor="mm")
        
        # Add content as bullet points
        y_position = height//3
        content_lines = content.split('\n')
        for line in content_lines:
            if line.strip():
                draw.text((100, y_position), f"• {line.strip()}", fill=text_color, font=content_font)
                y_position += content_font_size + 20
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                # Resize logo to reasonable size (e.g., 100x100)
                logo = logo.resize((100, 100))
                # Place logo in bottom right corner
                bg.paste(logo, (width - 120, height - 120), logo if logo.mode == 'RGBA' else None)
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        # Save the slide
        slide_path = f"{self.output_dir}/slide_{slide_number}.png"
        bg.save(slide_path)
        
        return slide_path
    
    def generate_carousel(self, title, slides_content, custom_style=None, logo_path=None, custom_text_color=None, individual_backgrounds=False):
        """Generate a full LinkedIn carousel"""
        self.carousel_data = {
            "title": title,
            "theme": self.theme,
            "slides": []
        }
        
        slide_paths = []
        
        # Generate a background image for all slides or individual backgrounds
        if individual_backgrounds:
            bg_image_paths = []
            for i, slide in enumerate(slides_content, 1):
                heading = slide.get("heading", "")
                bg_prompt = f"Professional background for LinkedIn slide about {heading}"
                bg_image_path, _ = self.generate_background_image(bg_prompt, custom_style)
                bg_image_paths.append(bg_image_path)
        else:
            bg_prompt = f"Professional background for LinkedIn carousel about {title}"
            bg_image_path, _ = self.generate_background_image(bg_prompt, custom_style)
            bg_image_paths = [bg_image_path] * len(slides_content)
        
        # Create each slide
        for i, slide in enumerate(slides_content, 1):
            slide_path = self.create_slide(
                bg_image_paths[i-1],
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
                "image_path": slide_path,
                "background_path": bg_image_paths[i-1]
            })
        
        # Generate PDF
        pdf_path = self.create_pdf(slide_paths, title)
        
        # Save carousel data as JSON
        json_path = f"{self.output_dir}/{title.replace(' ', '_')}_carousel_data.json"
        with open(json_path, 'w') as f:
            json.dump(self.carousel_data, f, indent=4)
        
        return {
            "pdf_path": pdf_path,
            "json_path": json_path,
            "slide_paths": slide_paths
        }
    
    def create_pdf(self, image_paths, title):
        """Create a PDF from the slide images"""
        pdf_path = f"{self.output_dir}/{title.replace(' ', '_')}_carousel.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        for img_path in image_paths:
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate aspect ratio to fit on letter page
            page_width, page_height = letter
            ratio = min(page_width / img_width, page_height / img_height) * 0.9
            
            # Calculate new dimensions
            new_width = img_width * ratio
            new_height = img_height * ratio
            
            # Calculate position to center the image
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            
            # Add the image to the PDF
            c.drawImage(img_path, x, y, width=new_width, height=new_height)
            c.showPage()
        
        c.save()
        print(f"PDF saved to: {pdf_path}")
        return pdf_path
    
    def get_available_themes(self):
        """Return list of available themes"""
        return list(self.themes.keys())


def main():
    generator = LinkedInCarouselGenerator()
    
    # Print available themes
    print("Available themes:", generator.get_available_themes())
    
    # Get user input
    theme = input("Select a theme (default, dark, light, creative, tech) [default]: ") or "default"
    generator.theme = theme if theme in generator.get_available_themes() else "default"
    
    title = input("Enter carousel title: ")
    num_slides = int(input("How many slides do you want to create? "))
    
    individual_backgrounds = input("Generate individual background for each slide? (y/n) [n]: ").lower() == 'y'
    logo_path = input("Path to logo image (optional): ") or None
    if logo_path and not os.path.exists(logo_path):
        print(f"Warning: Logo file not found at {logo_path}. Continuing without logo.")
        logo_path = None
    
    slides_content = []
    for i in range(1, num_slides + 1):
        print(f"\n--- Slide {i} ---")
        heading = input(f"Enter heading for slide {i}: ")
        content = input(f"Enter content for slide {i} (use newlines for bullet points): ")
        slides_content.append({
            "heading": heading,
            "content": content
        })
    
    # Generate the carousel
    result = generator.generate_carousel(
        title, 
        slides_content,
        logo_path=logo_path,
        individual_backgrounds=individual_backgrounds
    )
    
    print("\nCarousel generation completed!")
    print(f"PDF saved to: {result['pdf_path']}")
    print(f"JSON data saved to: {result['json_path']}")


if __name__ == "__main__":
    main() 