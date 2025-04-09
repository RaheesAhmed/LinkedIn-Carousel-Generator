import os
import json
import uuid
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
import random

load_dotenv()

class TemplateCarouselGenerator:
    def __init__(self, theme="default"):
        self.carousel_data = {}
        self.output_dir = "output"
        
        # Set theme
        self.theme = theme
        self.themes = {
            "default": {
                "text_color": (255, 255, 255),
                "heading_font_size": 60,
                "subheading_font_size": 48,
                "content_font_size": 36,
                "slide_size": (1080, 1080),
                "primary_color": (52, 152, 219),  # Blue
                "secondary_color": (41, 128, 185),  # Darker blue
                "accent_color": (46, 204, 113),  # Green
                "template": "gradient"
            },
            "dark": {
                "text_color": (230, 230, 230),
                "heading_font_size": 65,
                "subheading_font_size": 50,
                "content_font_size": 40,
                "slide_size": (1080, 1080),
                "primary_color": (44, 62, 80),  # Dark blue
                "secondary_color": (52, 73, 94),  # Slightly lighter dark blue
                "accent_color": (231, 76, 60),  # Red
                "template": "blocks"
            },
            "light": {
                "text_color": (70, 70, 70),
                "heading_font_size": 60,
                "subheading_font_size": 45,
                "content_font_size": 36,
                "slide_size": (1080, 1080),
                "primary_color": (236, 240, 241),  # Light gray
                "secondary_color": (189, 195, 199),  # Slightly darker light gray
                "accent_color": (241, 196, 15),  # Yellow
                "template": "minimal"
            },
            "creative": {
                "text_color": (250, 250, 250),
                "heading_font_size": 70,
                "subheading_font_size": 50,
                "content_font_size": 40,
                "slide_size": (1080, 1080),
                "primary_color": (155, 89, 182),  # Purple
                "secondary_color": (142, 68, 173),  # Darker purple
                "accent_color": (230, 126, 34),  # Orange
                "template": "geometric"
            },
            "tech": {
                "text_color": (220, 240, 255),
                "heading_font_size": 65,
                "subheading_font_size": 48,
                "content_font_size": 38,
                "slide_size": (1080, 1080),
                "primary_color": (26, 188, 156),  # Teal
                "secondary_color": (22, 160, 133),  # Darker teal
                "accent_color": (52, 152, 219),  # Blue
                "template": "circuit"
            }
        }
        
        self.template_factories = {
            "gradient": self._create_gradient_template,
            "blocks": self._create_blocks_template,
            "minimal": self._create_minimal_template,
            "geometric": self._create_geometric_template,
            "circuit": self._create_circuit_template
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _create_gradient_template(self, slide_number, theme_colors):
        """Create a gradient template with modern business style"""
        width, height = self.themes[self.theme]["slide_size"]
        primary, secondary, accent = theme_colors
        
        # Create base image
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Draw gradient background
        for y in range(height):
            # Calculate ratio of position (0 at top, 1 at bottom)
            ratio = y / height
            # Calculate color at this position by linear interpolation
            r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
            g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
            b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
            
            # Draw a line with this color
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        # Add design elements - diagonal accent lines
        for i in range(5):
            line_width = random.randint(2, 6)
            x1 = random.randint(-100, width//2)
            y1 = random.randint(-100, height//4)
            x2 = x1 + random.randint(400, 800)
            y2 = y1 + random.randint(400, 800)
            
            # Use accent color with transparency
            accent_color = (*accent, 100)  # RGBA with alpha
            line_color = (accent[0], accent[1], accent[2], 100)
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=line_width)
            
        # Add circular highlight in corner
        highlight_radius = 200
        highlight_pos = (width - 150, 150)
        
        # Create a circle with radial gradient
        for r in range(highlight_radius, 0, -1):
            opacity = int(100 * (1 - r/highlight_radius))
            highlight_color = (accent[0], accent[1], accent[2], opacity)
            draw.ellipse(
                [(highlight_pos[0]-r, highlight_pos[1]-r), 
                 (highlight_pos[0]+r, highlight_pos[1]+r)], 
                outline=highlight_color,
                width=1
            )
            
        # Add slide number indicator
        self._add_slide_number_indicator(draw, slide_number, (50, 50), accent, 40)
            
        return image
    
    def _create_blocks_template(self, slide_number, theme_colors):
        """Create a template with modern block design"""
        width, height = self.themes[self.theme]["slide_size"]
        primary, secondary, accent = theme_colors
        
        # Create base image with primary color
        image = Image.new("RGB", (width, height), primary)
        draw = ImageDraw.Draw(image)
        
        # Add a large rectangle on the left
        rect_width = width // 3
        draw.rectangle([(0, 0), (rect_width, height)], fill=secondary)
        
        # Add accent color blocks
        block_size = 80
        for i in range(6):
            x = random.randint(rect_width + 50, width - block_size - 50)
            y = random.randint(50, height - block_size - 50)
            
            # Create a slight transparency in the blocks
            block_color = accent
            outline_color = (255, 255, 255)
            
            draw.rectangle(
                [(x, y), (x + block_size, y + block_size)], 
                fill=block_color,
                outline=outline_color,
                width=2
            )
            
        # Add slide number indicator in a prominent box
        num_box_size = 80
        num_box_pos = (rect_width - num_box_size - 30, 50)
        draw.rectangle(
            [num_box_pos, (num_box_pos[0] + num_box_size, num_box_pos[1] + num_box_size)],
            fill=accent
        )
        self._add_slide_number_indicator(
            draw, 
            slide_number, 
            (num_box_pos[0] + num_box_size//2, num_box_pos[1] + num_box_size//2), 
            (255, 255, 255), 
            40,
            center=True
        )
            
        return image
    
    def _create_minimal_template(self, slide_number, theme_colors):
        """Create a minimal, clean template"""
        width, height = self.themes[self.theme]["slide_size"]
        primary, secondary, accent = theme_colors
        
        # Create base image with primary color
        image = Image.new("RGB", (width, height), primary)
        draw = ImageDraw.Draw(image)
        
        # Add subtle texture
        for i in range(1000):
            x = random.randint(0, width)
            y = random.randint(0, height)
            # Very subtle dots
            draw.point((x, y), fill=(secondary[0], secondary[1], secondary[2]))
            
        # Add a thin horizontal line
        line_y = height // 4
        draw.line([(50, line_y), (width - 50, line_y)], fill=accent, width=2)
        
        # Add a clean border
        border_width = 10
        draw.rectangle(
            [(border_width//2, border_width//2), (width - border_width//2, height - border_width//2)],
            outline=secondary,
            width=border_width
        )
        
        # Add slide number in a clean, minimal style
        self._add_slide_number_indicator(
            draw, 
            slide_number, 
            (width - 80, height - 80), 
            accent, 
            36
        )
            
        return image
    
    def _create_geometric_template(self, slide_number, theme_colors):
        """Create a template with geometric patterns"""
        width, height = self.themes[self.theme]["slide_size"]
        primary, secondary, accent = theme_colors
        
        # Create base image with primary color
        image = Image.new("RGB", (width, height), primary)
        draw = ImageDraw.Draw(image)
        
        # Create geometric pattern in the background
        # Triangles
        for i in range(15):
            # Random triangle
            points = [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height))
            ]
            
            # Random color based on theme
            r = random.randint(min(primary[0], secondary[0]), max(primary[0], secondary[0]))
            g = random.randint(min(primary[1], secondary[1]), max(primary[1], secondary[1]))
            b = random.randint(min(primary[2], secondary[2]), max(primary[2], secondary[2]))
            
            draw.polygon(points, fill=(r, g, b))
        
        # Add an accent colored diagonal stripe
        stripe_width = 150
        points = [
            (0, height - stripe_width),
            (0, height),
            (width, height),
            (width, height - stripe_width)
        ]
        draw.polygon(points, fill=accent)
        
        # Add slide number on the accent stripe
        self._add_slide_number_indicator(
            draw, 
            slide_number, 
            (width - 80, height - stripe_width//2), 
            (255, 255, 255), 
            40
        )
            
        return image
    
    def _create_circuit_template(self, slide_number, theme_colors):
        """Create a tech-themed template with circuit board patterns"""
        width, height = self.themes[self.theme]["slide_size"]
        primary, secondary, accent = theme_colors
        
        # Create base image with gradient from primary to secondary
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Draw gradient background
        for y in range(height):
            ratio = y / height
            r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
            g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
            b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Create circuit board pattern
        # Start points for circuit lines
        nodes = []
        for i in range(10):
            nodes.append((random.randint(0, width), random.randint(0, height)))
        
        # Draw circuit lines connecting nodes
        for i in range(len(nodes)):
            # Connect to 2-3 other nodes
            connections = random.randint(2, 3)
            for j in range(connections):
                target = random.randint(0, len(nodes)-1)
                if target != i:
                    # Draw right-angled lines (like circuit traces)
                    start = nodes[i]
                    end = nodes[target]
                    
                    # Choose a point to create the right angle
                    if random.random() > 0.5:
                        mid = (start[0], end[1])
                    else:
                        mid = (end[0], start[1])
                    
                    # Draw the two segments with accent color
                    draw.line([start, mid], fill=accent, width=2)
                    draw.line([mid, end], fill=accent, width=2)
                    
                    # Add a node point at the connection
                    node_size = random.randint(4, 10)
                    draw.ellipse(
                        [(end[0]-node_size//2, end[1]-node_size//2), 
                         (end[0]+node_size//2, end[1]+node_size//2)],
                        fill=accent
                    )
        
        # Add a tech-themed slide number indicator
        indicator_size = 80
        indicator_pos = (width - indicator_size - 50, 50)
        
        # Draw a hexagon for the slide number
        self._draw_hexagon(
            draw, 
            (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2),
            indicator_size//2,
            accent
        )
        
        # Add the number
        self._add_slide_number_indicator(
            draw, 
            slide_number, 
            (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
            (255, 255, 255), 
            36,
            center=True
        )
            
        return image
    
    def _draw_hexagon(self, draw, center, size, color):
        """Helper method to draw a hexagon"""
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = center[0] + size * math.cos(angle)
            y = center[1] + size * math.sin(angle)
            points.append((x, y))
        
        draw.polygon(points, fill=color)
        
    def _add_slide_number_indicator(self, draw, number, position, color, size, center=False):
        """Add a slide number indicator to the template"""
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except IOError:
            font = ImageFont.load_default()
            
        text = f"{number}"
        
        if center:
            draw.text(position, text, fill=color, font=font, anchor="mm")
        else:
            draw.text(position, text, fill=color, font=font)
    
    def _draw_icon(self, draw, icon_type, position, size, color):
        """Draw icons for slides"""
        x, y = position
        
        if icon_type == "lightbulb":
            # Draw a lightbulb icon
            # Bulb
            draw.ellipse([(x-size//2, y-size//2), (x+size//2, y+size//5)], outline=color, width=3, fill=None)
            # Base
            draw.rectangle([(x-size//4, y+size//5), (x+size//4, y+size//2)], outline=color, width=3, fill=None)
            # Filament
            draw.line([(x, y-size//4), (x, y+size//8)], fill=color, width=3)
            
        elif icon_type == "graph":
            # Draw a bar graph icon
            bar_width = size // 5
            heights = [size//3, size//1.5, size//2, size//2.5, size//1.8]
            
            for i, height in enumerate(heights):
                bar_x = x - size//2 + i * bar_width
                draw.rectangle(
                    [(bar_x, y+size//2-height), (bar_x+bar_width-2, y+size//2)],
                    outline=color,
                    width=2,
                    fill=color
                )
                
        elif icon_type == "gear":
            # Draw a gear icon
            outer_radius = size // 2
            inner_radius = size // 3
            teeth = 8
            
            # Draw outer circle
            draw.ellipse(
                [(x-outer_radius, y-outer_radius), (x+outer_radius, y+outer_radius)],
                outline=color,
                width=2
            )
            
            # Draw teeth
            for i in range(teeth):
                angle = i * 2 * math.pi / teeth
                x1 = x + inner_radius * math.cos(angle)
                y1 = y + inner_radius * math.sin(angle)
                x2 = x + outer_radius * math.cos(angle)
                y2 = y + outer_radius * math.sin(angle)
                draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
                
            # Draw center circle
            draw.ellipse(
                [(x-inner_radius//2, y-inner_radius//2), 
                 (x+inner_radius//2, y+inner_radius//2)],
                outline=color,
                width=2
            )
            
        elif icon_type == "chat":
            # Draw a chat bubble icon
            draw.ellipse(
                [(x-size//2, y-size//2), (x+size//2, y+size//2)],
                outline=color,
                width=3,
                fill=None
            )
            
            # Add three dots for text
            dot_size = size // 15
            for i in range(3):
                offset = (i - 1) * size // 6
                draw.ellipse(
                    [(x+offset-dot_size, y-dot_size), (x+offset+dot_size, y+dot_size)],
                    fill=color
                )
            
        elif icon_type == "person":
            # Draw a person icon
            # Head
            head_radius = size // 4
            draw.ellipse(
                [(x-head_radius, y-size//2), (x+head_radius, y-size//2+head_radius*2)],
                outline=color,
                width=3,
                fill=None
            )
            # Body
            draw.line([(x, y-size//2+head_radius*2), (x, y+size//4)], fill=color, width=3)
            # Arms
            draw.line([(x-size//3, y-size//6), (x+size//3, y-size//6)], fill=color, width=3)
            # Legs
            draw.line([(x, y+size//4), (x-size//4, y+size//2)], fill=color, width=3)
            draw.line([(x, y+size//4), (x+size//4, y+size//2)], fill=color, width=3)
            
        elif icon_type == "star":
            # Draw a star icon
            points = []
            outer_radius = size // 2
            inner_radius = size // 4
            
            for i in range(10):
                angle = math.pi/2 + i * math.pi / 5
                radius = outer_radius if i % 2 == 0 else inner_radius
                points.append((
                    x + radius * math.cos(angle),
                    y + radius * math.sin(angle)
                ))
                
            draw.polygon(points, outline=color, fill=color)
    
    def generate_template(self, slide_number):
        """Generate a slide template based on the theme"""
        # Get theme colors
        theme_colors = (
            self.themes[self.theme]["primary_color"],
            self.themes[self.theme]["secondary_color"],
            self.themes[self.theme]["accent_color"]
        )
        
        # Get the template type for this theme
        template_type = self.themes[self.theme]["template"]
        
        # Use the appropriate template factory
        if template_type in self.template_factories:
            return self.template_factories[template_type](slide_number, theme_colors)
        else:
            # Fallback to gradient template
            return self._create_gradient_template(slide_number, theme_colors)
    
    def create_slide(self, heading, content, slide_number, logo_path=None, custom_text_color=None):
        """Create a slide using a template"""
        # Generate template
        image = self.generate_template(slide_number)
        
        # Create a drawing context
        draw = ImageDraw.Draw(image)
        
        # Get colors and font sizes from theme
        text_color = custom_text_color if custom_text_color else self.themes[self.theme]["text_color"]
        heading_font_size = self.themes[self.theme]["heading_font_size"]
        subheading_font_size = self.themes[self.theme]["subheading_font_size"]
        content_font_size = self.themes[self.theme]["content_font_size"]
        
        # Try to load fonts, use default if not available
        try:
            heading_font = ImageFont.truetype("arial.ttf", heading_font_size)
            subheading_font = ImageFont.truetype("arial.ttf", subheading_font_size)
            content_font = ImageFont.truetype("arial.ttf", content_font_size)
        except IOError:
            heading_font = ImageFont.load_default()
            subheading_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # Get image dimensions
        width, height = self.themes[self.theme]["slide_size"]
        
        # Add heading (centered)
        draw.text((width//2, height//6), heading, fill=text_color, font=heading_font, anchor="mm")
        
        # Select an appropriate icon based on slide content
        icon_type = "lightbulb"  # default
        if "AI" in heading or "data" in heading.lower() or "machine" in heading.lower():
            icon_type = "gear"
        elif "analytics" in heading.lower() or "growth" in heading.lower() or "increase" in heading.lower():
            icon_type = "graph"
        elif "customer" in heading.lower() or "service" in heading.lower() or "support" in heading.lower() or "conversation" in heading.lower():
            icon_type = "chat"
        elif "personalization" in heading.lower() or "user" in heading.lower() or "people" in heading.lower():
            icon_type = "person"
        elif "start" in heading.lower() or "best" in heading.lower() or "top" in heading.lower() or "key" in heading.lower():
            icon_type = "star"
            
        # Draw an icon related to the content
        self._draw_icon(
            draw,
            icon_type,
            (width//6, height//2.5),
            120,
            self.themes[self.theme]["accent_color"]
        )
        
        # Add content as bullet points
        y_position = height//2.5
        content_lines = content.split('\n')
        for line in content_lines:
            if line.strip():
                # Draw bullet point
                bullet_size = 10
                draw.ellipse(
                    [(width//3 - bullet_size - 10, y_position + content_font_size//2 - bullet_size//2),
                     (width//3 - 10, y_position + content_font_size//2 + bullet_size//2)],
                    fill=text_color
                )
                
                # Draw text
                draw.text((width//3, y_position), line.strip(), fill=text_color, font=content_font)
                y_position += content_font_size + 20
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                # Resize logo to reasonable size (e.g., 100x100)
                logo = logo.resize((100, 100))
                # Place logo in bottom right corner
                image.paste(logo, (width - 120, height - 120), logo if logo.mode == 'RGBA' else None)
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        # Save the slide
        slide_path = f"{self.output_dir}/slide_{slide_number}.png"
        image.save(slide_path)
        
        return slide_path
    
    def generate_carousel(self, title, slides_content, logo_path=None, custom_text_color=None):
        """Generate a full LinkedIn carousel"""
        self.carousel_data = {
            "title": title,
            "theme": self.theme,
            "slides": []
        }
        
        slide_paths = []
        
        # Create each slide
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
    generator = TemplateCarouselGenerator()
    
    # Print available themes
    print("Available themes:", generator.get_available_themes())
    
    # Get user input
    theme = input("Select a theme (default, dark, light, creative, tech) [default]: ") or "default"
    generator.theme = theme if theme in generator.get_available_themes() else "default"
    
    title = input("Enter carousel title: ")
    num_slides = int(input("How many slides do you want to create? "))
    
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
        logo_path=logo_path
    )
    
    print("\nCarousel generation completed!")
    print(f"PDF saved to: {result['pdf_path']}")
    print(f"JSON data saved to: {result['json_path']}")


if __name__ == "__main__":
    main() 