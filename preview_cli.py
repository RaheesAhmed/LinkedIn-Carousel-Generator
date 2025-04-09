import argparse
import os
import sys
import webbrowser
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preview.html_generator import generate_preview_html
from src.preview.server import start_preview_server

def main():
    parser = argparse.ArgumentParser(description="Preview LinkedIn Carousel")
    parser.add_argument('json_file', type=str, help='Path to the carousel JSON data file (e.g., output/my_carousel_data.json)')
    parser.add_argument('--port', type=int, default=8000, help='Port for the preview server')
    
    args = parser.parse_args()
    
    # Get absolute path to JSON file
    json_abs_path = os.path.abspath(args.json_file)
    
    # Check if JSON file exists
    if not os.path.exists(json_abs_path):
        print(f"Error: JSON file not found at: {json_abs_path}")
        return

    # Workspace root is the current working directory when the script is run
    workspace_root = os.getcwd()
    print(f"Workspace root detected as: {workspace_root}")

    # Generate preview HTML (will be created in preview_html/index.html relative to workspace)
    try:
        html_path_rel = generate_preview_html(json_abs_path, workspace_root)
        if not html_path_rel:
            print("Failed to generate preview HTML.")
            return
    except Exception as e:
        print(f"Error during HTML generation: {e}")
        traceback.print_exc()
        return

    # Start preview server (serves from workspace_root)
    try:
        httpd = start_preview_server(args.port)
        if not httpd:
             # Server failed to start (e.g., port in use)
             return 
    except Exception as e:
        print(f"Error starting preview server: {e}")
        traceback.print_exc()
        return
        
    # Construct the URL to open
    # The server serves from workspace root, HTML is in preview_html/index.html
    preview_url = f"http://localhost:{args.port}/{html_path_rel.replace(os.sep, '/')}"
    print(f"Opening preview in browser: {preview_url}")
    
    # Open browser
    webbrowser.open(preview_url)
    
    try:
        # Keep the script running so the server thread continues
        input("Preview server is running. Press Enter to stop...\n")
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        if httpd:
            print("Shutting down server...")
            httpd.shutdown()
            print("Server stopped.")
        else:
            print("Server was not started properly.")

if __name__ == "__main__":
    main() 