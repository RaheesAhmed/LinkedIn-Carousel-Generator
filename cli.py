import argparse
import os
import sys
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.carousel_generator.generator import CarouselGenerator
from src.carousel_generator.themes import get_available_themes

def parse_slide_data(slide_file):
    """Parse slide data from a text file."""
    slides = []
    current_slide = None
    try:
        with open(slide_file, 'r', encoding='utf-8') as f: # Specify encoding
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('[Slide ') and line.endswith(']'):
                if current_slide:
                    # Ensure content is properly added before starting new slide
                    if "content" not in current_slide: 
                        current_slide["content"] = ""
                    slides.append(current_slide)
                current_slide = {"heading": "", "content": ""} # Reset for new slide
            elif line.startswith('Heading:') and current_slide is not None:
                current_slide["heading"] = line[len('Heading:'):].strip()
            elif line.startswith('Content:') and current_slide is not None:
                current_slide["content"] = line[len('Content:'):].strip()
            elif current_slide is not None and "content" in current_slide: # Check if content started
                # Append additional content lines
                current_slide["content"] += "\n" + line
            elif current_slide is not None:
                 # Handle case where content might not start with 'Content:'
                 # Treat the line as content if a slide block has started
                 current_slide["content"] = line

        # Add the last slide if it exists
        if current_slide:
            if "content" not in current_slide: # Ensure last slide has content key
                 current_slide["content"] = ""
            slides.append(current_slide)
            
        print(f"Parsed {len(slides)} slides from {slide_file}")
        return slides
    except FileNotFoundError:
        print(f"Error: Slide file not found at {slide_file}")
        return []
    except Exception as e:
        print(f"Error parsing slide data from {slide_file}: {e}")
        traceback.print_exc()
        return []

def get_interactive_slides(num_slides):
    """Get slide content interactively from the user."""
    slides_content = []
    for i in range(1, num_slides + 1):
        print(f"\n--- Slide {i} ---")
        heading = input(f"Enter heading for slide {i}: ")
        print(f"Enter content for slide {i} (end with empty line or Ctrl+D/Z):")
        content_lines = []
        try:
            while True:
                line = input()
                if not line: # Stop on empty line
                    break
                content_lines.append(line)
        except EOFError: # Handle Ctrl+D/Z
            pass 
        content = "\n".join(content_lines)
        slides_content.append({"heading": heading, "content": content})
    return slides_content

def main():
    available_themes = get_available_themes()
    parser = argparse.ArgumentParser(description='LinkedIn Carousel Generator')
    parser.add_argument('--title', type=str, help='Carousel title (required)')
    parser.add_argument('--slides', type=int, help='Number of slides to create interactively')
    parser.add_argument('--file', type=str, help='File containing slide data (e.g., slides.txt)')
    parser.add_argument('--theme', type=str, choices=available_themes, 
                        default='default', help=f'Visual theme (options: {", ".join(available_themes)})')
    parser.add_argument('--logo', type=str, help='Path to logo image to add to slides')
    parser.add_argument('--output', type=str, default='output', help='Output directory for generated files')
    
    args = parser.parse_args()
    
    if not args.title:
        parser.error("--title is required.")
        # args.title = input("Enter carousel title: ") # Alternative: prompt if missing
        
    if not args.slides and not args.file:
         parser.error("Either --slides or --file must be provided.")
         # num_slides = int(input("How many slides do you want to create? ")) # Alternative
         # slides_content = get_interactive_slides(num_slides)
    elif args.slides and args.file:
        print("Warning: Both --slides and --file provided. Using --file.")
        # Prioritize file if both are given
        slides_content = parse_slide_data(args.file)
    elif args.file:
        slides_content = parse_slide_data(args.file)
    else: # Only args.slides provided
        slides_content = get_interactive_slides(args.slides)
        
    if not slides_content:
        print("Error: No slide content available. Exiting.")
        return

    # Validate logo path
    logo_path = args.logo
    if logo_path and not os.path.exists(logo_path):
        print(f"Warning: Logo file not found at {logo_path}. Continuing without logo.")
        logo_path = None
        
    # Initialize generator
    try:
        generator = CarouselGenerator(theme=args.theme, output_dir=args.output)
        print(f"Using theme: {args.theme}, Output directory: {args.output}")
    except Exception as e:
        print(f"Error initializing carousel generator: {e}")
        traceback.print_exc()
        return
        
    print(f"\nGenerating carousel '{args.title}' with {len(slides_content)} slides...")
    
    # Generate the carousel
    try:
        result = generator.generate_carousel(
            args.title, 
            slides_content,
            logo_path=logo_path
        )
        
        if result and result.get('pdf_path') and result.get('json_path'):
            print("\nCarousel generation completed successfully!")
            print(f"PDF saved to: {result['pdf_path']}")
            print(f"JSON data saved to: {result['json_path']}")
            print(f"Individual slides saved in: {generator.output_dir}/")
            
            # Provide preview command instruction relative to workspace root
            json_rel_path = os.path.relpath(result['json_path'], os.getcwd())
            print("\nTo preview your carousel, run:")
            # Use forward slashes for cross-platform compatibility in the command suggestion
            print(f"python preview_cli.py {json_rel_path.replace(os.sep, '/')}") 
        else:
            print("\nCarousel generation finished, but some output paths might be missing.")
            print(f"Result details: {result}")

    except Exception as e:
        print(f"\nError during carousel generation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

 