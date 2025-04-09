import argparse
import os
import traceback
from linkedin_carousel_generator import TemplateCarouselGenerator

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
    
    try:
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
            
        print(f"Parsed {len(slides)} slides from {slide_file}")
        return slides
    except Exception as e:
        print(f"Error parsing slide data: {e}")
        traceback.print_exc()
        return []

def main():
    try:
        parser = argparse.ArgumentParser(description='LinkedIn Carousel Generator with Beautiful Templates')
        parser.add_argument('--title', type=str, help='Carousel title')
        parser.add_argument('--slides', type=int, help='Number of slides to create interactively')
        parser.add_argument('--file', type=str, help='File containing slide data')
        parser.add_argument('--theme', type=str, choices=['default', 'dark', 'light', 'creative', 'tech'], 
                            default='default', help='Visual theme for the carousel')
        parser.add_argument('--logo', type=str, help='Path to logo image to add to slides')
        
        args = parser.parse_args()
        print("Args parsed:", args)
        
        try:
            generator = TemplateCarouselGenerator(theme=args.theme)
            print(f"Generator created with theme: {args.theme}")
        except Exception as e:
            print(f"Error creating generator: {e}")
            traceback.print_exc()
            return
        
        if not args.title:
            args.title = input("Enter carousel title: ")
        
        slides_content = []
        
        if args.file and os.path.exists(args.file):
            # Load slides from file
            print(f"Loading slide content from {args.file}...")
            slides_content = parse_slide_data(args.file)
            print(f"Loaded {len(slides_content)} slides.")
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
        
        print(f"\nGenerating carousel with {len(slides_content)} slides using {args.theme} theme...")
        print("First slide content:", slides_content[0] if slides_content else "No slides")
        
        # Generate the carousel
        try:
            result = generator.generate_carousel(
                args.title, 
                slides_content,
                logo_path=logo_path
            )
            
            print("\nCarousel generation completed!")
            print(f"PDF saved to: {result['pdf_path']}")
            print(f"JSON data saved to: {result['json_path']}")
            print(f"Individual slides saved in: {generator.output_dir}/")
            print(f"Theme used: {generator.theme}")
            
            print("\nTo preview your carousel, run:")
            print(f"python preview_carousel.py {result['json_path']}")
        except Exception as e:
            print(f"Error generating carousel: {e}")
            traceback.print_exc()
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

 