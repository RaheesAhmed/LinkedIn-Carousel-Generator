THEMES = {
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

def get_available_themes():
    return list(THEMES.keys())

def get_theme_config(theme_name):
    return THEMES.get(theme_name, THEMES["default"]) 