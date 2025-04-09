import random
from PIL import Image, ImageDraw
from .utils import add_slide_number_indicator, draw_hexagon # Use relative import

def create_gradient_template(slide_number, theme_config, theme_colors):
    """Create a gradient template with modern business style"""
    width, height = theme_config["slide_size"]
    primary, secondary, accent = theme_colors
    
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    
    for y in range(height):
        ratio = y / height
        r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
        g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
        b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    for i in range(5):
        line_width = random.randint(2, 6)
        x1 = random.randint(-100, width//2)
        y1 = random.randint(-100, height//4)
        x2 = x1 + random.randint(400, 800)
        y2 = y1 + random.randint(400, 800)
        line_color = (accent[0], accent[1], accent[2], 100)
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=line_width)
        
    highlight_radius = 200
    highlight_pos = (width - 150, 150)
    for r in range(highlight_radius, 0, -1):
        opacity = int(100 * (1 - r/highlight_radius))
        highlight_color = (accent[0], accent[1], accent[2], opacity)
        draw.ellipse(
            [(highlight_pos[0]-r, highlight_pos[1]-r), 
             (highlight_pos[0]+r, highlight_pos[1]+r)], 
            outline=highlight_color,
            width=1
        )
        
    add_slide_number_indicator(draw, slide_number, (50, 50), accent, 40)
    return image

def create_blocks_template(slide_number, theme_config, theme_colors):
    """Create a template with modern block design"""
    width, height = theme_config["slide_size"]
    primary, secondary, accent = theme_colors
    
    image = Image.new("RGB", (width, height), primary)
    draw = ImageDraw.Draw(image)
    
    rect_width = width // 3
    draw.rectangle([(0, 0), (rect_width, height)], fill=secondary)
    
    block_size = 80
    for i in range(6):
        x = random.randint(rect_width + 50, width - block_size - 50)
        y = random.randint(50, height - block_size - 50)
        block_color = accent
        outline_color = (255, 255, 255)
        draw.rectangle(
            [(x, y), (x + block_size, y + block_size)], 
            fill=block_color,
            outline=outline_color,
            width=2
        )
        
    num_box_size = 80
    num_box_pos = (rect_width - num_box_size - 30, 50)
    draw.rectangle(
        [num_box_pos, (num_box_pos[0] + num_box_size, num_box_pos[1] + num_box_size)],
        fill=accent
    )
    add_slide_number_indicator(
        draw, 
        slide_number, 
        (num_box_pos[0] + num_box_size//2, num_box_pos[1] + num_box_size//2), 
        (255, 255, 255), 
        40,
        center=True
    )
    return image

def create_minimal_template(slide_number, theme_config, theme_colors):
    """Create a minimal, clean template"""
    width, height = theme_config["slide_size"]
    primary, secondary, accent = theme_colors
    
    image = Image.new("RGB", (width, height), primary)
    draw = ImageDraw.Draw(image)
    
    for i in range(1000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(secondary[0], secondary[1], secondary[2]))
        
    line_y = height // 4
    draw.line([(50, line_y), (width - 50, line_y)], fill=accent, width=2)
    
    border_width = 10
    draw.rectangle(
        [(border_width//2, border_width//2), (width - border_width//2, height - border_width//2)],
        outline=secondary,
        width=border_width
    )
    
    add_slide_number_indicator(
        draw, 
        slide_number, 
        (width - 80, height - 80), 
        accent, 
        36
    )
    return image

def create_geometric_template(slide_number, theme_config, theme_colors):
    """Create a template with geometric patterns"""
    width, height = theme_config["slide_size"]
    primary, secondary, accent = theme_colors
    
    image = Image.new("RGB", (width, height), primary)
    draw = ImageDraw.Draw(image)
    
    for i in range(15):
        points = [
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height))
        ]
        r = random.randint(min(primary[0], secondary[0]), max(primary[0], secondary[0]))
        g = random.randint(min(primary[1], secondary[1]), max(primary[1], secondary[1]))
        b = random.randint(min(primary[2], secondary[2]), max(primary[2], secondary[2]))
        draw.polygon(points, fill=(r, g, b))
    
    stripe_width = 150
    points = [
        (0, height - stripe_width),
        (0, height),
        (width, height),
        (width, height - stripe_width)
    ]
    draw.polygon(points, fill=accent)
    
    add_slide_number_indicator(
        draw, 
        slide_number, 
        (width - 80, height - stripe_width//2), 
        (255, 255, 255), 
        40
    )
    return image

def create_circuit_template(slide_number, theme_config, theme_colors):
    """Create a tech-themed template with circuit board patterns"""
    width, height = theme_config["slide_size"]
    primary, secondary, accent = theme_colors
    
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    
    for y in range(height):
        ratio = y / height
        r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
        g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
        b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    nodes = []
    for i in range(10):
        nodes.append((random.randint(0, width), random.randint(0, height)))
    
    for i in range(len(nodes)):
        connections = random.randint(2, 3)
        for j in range(connections):
            target = random.randint(0, len(nodes)-1)
            if target != i:
                start = nodes[i]
                end = nodes[target]
                
                if random.random() > 0.5:
                    mid = (start[0], end[1])
                else:
                    mid = (end[0], start[1])
                
                draw.line([start, mid], fill=accent, width=2)
                draw.line([mid, end], fill=accent, width=2)
                
                node_size = random.randint(4, 10)
                draw.ellipse(
                    [(end[0]-node_size//2, end[1]-node_size//2), 
                     (end[0]+node_size//2, end[1]+node_size//2)],
                    fill=accent
                )
    
    indicator_size = 80
    indicator_pos = (width - indicator_size - 50, 50)
    
    draw_hexagon(
        draw, 
        (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2),
        indicator_size//2,
        accent
    )
    
    add_slide_number_indicator(
        draw, 
        slide_number, 
        (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
        (255, 255, 255), 
        36,
        center=True
    )
    return image

# Dictionary mapping template names to functions
TEMPLATE_FACTORIES = {
    "gradient": create_gradient_template,
    "blocks": create_blocks_template,
    "minimal": create_minimal_template,
    "geometric": create_geometric_template,
    "circuit": create_circuit_template
} 