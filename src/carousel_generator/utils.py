import os
import math
import json
import random
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_output_dir(output_dir="output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def draw_hexagon(draw, center, size, color):
    """Helper method to draw a hexagon"""
    points = []
    for i in range(6):
        angle = i * math.pi / 3
        x = center[0] + size * math.cos(angle)
        y = center[1] + size * math.sin(angle)
        points.append((x, y))
    
    draw.polygon(points, fill=color)

def add_slide_number_indicator(draw, number, position, color, size, center=False):
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

def draw_icon(draw, icon_type, position, size, color):
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

def select_icon(heading):
    """Select an appropriate icon based on slide heading"""
    heading_lower = heading.lower()
    if "AI" in heading or "data" in heading_lower or "machine" in heading_lower:
        return "gear"
    elif "analytics" in heading_lower or "growth" in heading_lower or "increase" in heading_lower:
        return "graph"
    elif "customer" in heading_lower or "service" in heading_lower or "support" in heading_lower or "conversation" in heading_lower:
        return "chat"
    elif "personalization" in heading_lower or "user" in heading_lower or "people" in heading_lower:
        return "person"
    elif "start" in heading_lower or "best" in heading_lower or "top" in heading_lower or "key" in heading_lower:
        return "star"
    return "lightbulb"  # default

def create_pdf(image_paths, title, output_dir="output"):
    """Create a PDF from the slide images"""
    pdf_path = os.path.join(output_dir, f"{title.replace(' ', '_')}_carousel.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    for img_path in image_paths:
        try:
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
        except Exception as e:
            print(f"Error adding image {img_path} to PDF: {e}")
    
    c.save()
    print(f"PDF saved to: {pdf_path}")
    return pdf_path

def save_carousel_data(carousel_data, title, output_dir="output"):
    """Save carousel metadata to a JSON file."""
    json_path = os.path.join(output_dir, f"{title.replace(' ', '_')}_carousel_data.json")
    try:
        with open(json_path, 'w') as f:
            json.dump(carousel_data, f, indent=4)
        print(f"JSON data saved to: {json_path}")
        return json_path
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        return None 