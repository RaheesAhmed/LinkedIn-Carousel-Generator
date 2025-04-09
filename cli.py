import argparse
import os
from linkedin_carousel_generator import LinkedInCarouselGenerator

def parse_slide_data(slide_file):
    """Parse slide data from a text file with format:
    [Slide X]
    Heading: Your Heading
    Content: Your content here
    More content on new lines
    
    [Slide Y]
    ...and so on
    """
    slides = []
    current_slide = None
    
    with open(slide_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('[Slide ') and line.endswith(']'):
            if current_slide:
                slides.append(current_slide)
            current_slide = {"heading": "", "content": ""}
        elif line.startswith('Heading:') and current_slide:
            current_slide["heading"] = line[8:].strip()
        elif line.startswith('Content:') and current_slide:
            current_slide["content"] = line[8:].strip()
        elif current_slide and current_slide["content"]:
            # Append additional content lines
            current_slide["content"] += "\n" + line
    
    # Add the last slide
    if current_slide:
        slides.append(current_slide)
        
    return slides

def main():
    parser = argparse.ArgumentParser(description='LinkedIn Carousel Generator')
    parser.add_argument('--title', type=str, help='Carousel title')
    parser.add_argument('--slides', type=int, help='Number of slides to create interactively')
    parser.add_argument('--file', type=str, help='File containing slide data')
    parser.add_argument('--theme', type=str, choices=['default', 'dark', 'light', 'creative', 'tech'], 
                        default='default', help='Visual theme for the carousel')
    parser.add_argument('--logo', type=str, help='Path to logo image to add to slides')
    parser.add_argument('--individual-backgrounds', action='store_true', 
                        help='Generate unique background for each slide')
    parser.add_argument('--custom-style', type=str, 
                        help='Custom style description for background generation')
    
    args = parser.parse_args()
    generator = LinkedInCarouselGenerator(theme=args.theme)
    
    if not args.title:
        args.title = input("Enter carousel title: ")
    
    slides_content = []
    
    if args.file and os.path.exists(args.file):
        # Load slides from file
        slides_content = parse_slide_data(args.file)
    elif args.slides:
        # Create slides interactively
        for i in range(1, args.slides + 1):
            print(f"\n--- Slide {i} ---")
            heading = input(f"Enter heading for slide {i}: ")
            content = input(f"Enter content for slide {i} (use newlines for bullet points): ")
            slides_content.append({
                "heading": heading,
                "content": content
            })
    else:
        # Default to interactive mode
        num_slides = int(input("How many slides do you want to create? "))
        for i in range(1, num_slides + 1):
            print(f"\n--- Slide {i} ---")
            heading = input(f"Enter heading for slide {i}: ")
            content = input(f"Enter content for slide {i} (use newlines for bullet points): ")
            slides_content.append({
                "heading": heading,
                "content": content
            })
    
    # Check if logo exists
    logo_path = args.logo
    if logo_path and not os.path.exists(logo_path):
        print(f"Warning: Logo file not found at {logo_path}. Continuing without logo.")
        logo_path = None
    
    # Generate the carousel
    result = generator.generate_carousel(
        args.title, 
        slides_content,
        custom_style=args.custom_style,
        logo_path=logo_path,
        individual_backgrounds=args.individual_backgrounds
    )
    
    print("\nCarousel generation completed!")
    print(f"PDF saved to: {result['pdf_path']}")
    print(f"JSON data saved to: {result['json_path']}")
    print(f"Individual slides saved in: {generator.output_dir}/")
    print(f"Theme used: {generator.theme}")

if __name__ == "__main__":
    main() 