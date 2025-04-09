import argparse
import json
import os
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path
from urllib.parse import unquote

class CarouselPreviewHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        
        # Handle carousel data request
        if self.path.startswith("/carousel_data/"):
            file_path = unquote(self.path[len("/carousel_data/"):])
            self.send_carousel_data(file_path)
            return
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def send_carousel_data(self, json_path):
        try:
            with open(json_path, 'r') as f:
                carousel_data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(carousel_data).encode())
        except Exception as e:
            self.send_error(404, f"File not found: {json_path} ({str(e)})")

def generate_preview_html(json_file):
    """Generate HTML page for previewing the carousel"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        title = data.get('title', 'LinkedIn Carousel')
        slides = data.get('slides', [])
        
        # Create HTML directory if it doesn't exist
        html_dir = Path("preview_html")
        html_dir.mkdir(exist_ok=True)
        
        # Create HTML file
        html_path = html_dir / "index.html"
        with open(html_path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #0077B5;
            text-align: center;
        }}
        .carousel {{
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            gap: 20px;
            padding: 20px 0;
        }}
        .slide {{
            scroll-snap-align: start;
            flex: 0 0 auto;
            width: 500px;
            height: 500px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            position: relative;
        }}
        .slide img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 10px;
        }}
        .slide-number {{
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 14px;
        }}
        .controls {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
            gap: 10px;
        }}
        button {{
            background-color: #0077B5;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{
            background-color: #00669c;
        }}
        .fullscreen {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        .fullscreen img {{
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }}
        .close-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 30px;
            cursor: pointer;
        }}
        .slide-info {{
            margin-top: 20px;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .metadata {{
            margin-top: 40px;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        pre {{
            background-color: #f7f7f7;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="carousel" id="carousel">
""")
            
            # Add slides
            for slide in slides:
                slide_number = slide.get('number', 1)
                image_path = slide.get('image_path', '')
                image_path = image_path.replace('\\', '/')
                
                f.write(f"""
            <div class="slide">
                <img src="/{image_path}" alt="Slide {slide_number}">
                <div class="slide-number">Slide {slide_number}</div>
            </div>""")
            
            f.write(f"""
        </div>
        
        <div class="controls">
            <button id="prev-btn">Previous</button>
            <button id="next-btn">Next</button>
            <button id="download-btn">Download PDF</button>
        </div>
        
        <div class="slide-info" id="slide-info">
            <h2>Slide Information</h2>
            <div id="slide-content"></div>
        </div>
        
        <div class="metadata">
            <h2>Carousel Metadata</h2>
            <pre id="metadata-json"></pre>
        </div>
    </div>
    
    <div class="fullscreen" id="fullscreen">
        <span class="close-btn" id="close-btn">&times;</span>
        <img id="fullscreen-img" src="" alt="Fullscreen slide">
    </div>

    <script>
        const carousel = document.getElementById('carousel');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const downloadBtn = document.getElementById('download-btn');
        const slideInfo = document.getElementById('slide-content');
        const metadataJson = document.getElementById('metadata-json');
        const fullscreen = document.getElementById('fullscreen');
        const fullscreenImg = document.getElementById('fullscreen-img');
        const closeBtn = document.getElementById('close-btn');
        
        let currentSlide = 0;
        const slides = Array.from(document.querySelectorAll('.slide'));
        let carouselData = null;
        
        // Load carousel data
        fetch('/carousel_data/{json_file}')
            .then(response => response.json())
            .then(data => {{
                carouselData = data;
                metadataJson.textContent = JSON.stringify(data, null, 2);
                updateSlideInfo();
            }})
            .catch(error => console.error('Error loading carousel data:', error));
        
        function scrollToSlide(index) {{
            if (index < 0) index = 0;
            if (index >= slides.length) index = slides.length - 1;
            
            currentSlide = index;
            const slide = slides[index];
            
            slide.scrollIntoView({{
                behavior: 'smooth',
                block: 'nearest',
                inline: 'start'
            }});
            
            updateSlideInfo();
        }}
        
        function updateSlideInfo() {{
            if (!carouselData || !carouselData.slides) return;
            
            const slide = carouselData.slides[currentSlide];
            if (!slide) return;
            
            const heading = slide.heading || '';
            const content = (slide.content || '').replace(/\\n/g, '<br>');
            
            slideInfo.innerHTML = `
                <h3>${{heading}}</h3>
                <p>${{content}}</p>
            `;
        }}
        
        prevBtn.addEventListener('click', () => {{
            scrollToSlide(currentSlide - 1);
        }});
        
        nextBtn.addEventListener('click', () => {{
            scrollToSlide(currentSlide + 1);
        }});
        
        downloadBtn.addEventListener('click', () => {{
            if (!carouselData) return;
            
            const title = carouselData.title || 'carousel';
            const pdfPath = `/{title.replace(' ', '_')}_carousel.pdf`;
            
            // Open PDF in new tab
            window.open(pdfPath, '_blank');
        }});
        
        // Make slides clickable for fullscreen
        slides.forEach((slide, index) => {{
            slide.addEventListener('click', () => {{
                const img = slide.querySelector('img');
                fullscreenImg.src = img.src;
                fullscreen.style.display = 'flex';
            }});
        }});
        
        closeBtn.addEventListener('click', () => {{
            fullscreen.style.display = 'none';
        }});
        
        // Initialize with first slide
        scrollToSlide(0);
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') {{
                scrollToSlide(currentSlide - 1);
            }} else if (e.key === 'ArrowRight') {{
                scrollToSlide(currentSlide + 1);
            }} else if (e.key === 'Escape' && fullscreen.style.display === 'flex') {{
                fullscreen.style.display = 'none';
            }}
        }});
    </script>
</body>
</html>""")
        
        return html_path
    except Exception as e:
        print(f"Error generating preview HTML: {e}")
        return None

def start_preview_server(port=8000):
    """Start a local HTTP server to preview the carousel"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = CarouselPreviewHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    print(f"Server started at http://localhost:{port}/")
    print("Press Ctrl+C to stop the server")
    
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return httpd

def main():
    parser = argparse.ArgumentParser(description="Preview LinkedIn Carousel")
    parser.add_argument('json_file', type=str, help='Path to the carousel JSON file')
    parser.add_argument('--port', type=int, default=8000, help='Port for the preview server')
    
    args = parser.parse_args()
    
    # Check if JSON file exists
    if not os.path.exists(args.json_file):
        print(f"Error: JSON file not found: {args.json_file}")
        return
    
    # Generate preview HTML
    html_path = generate_preview_html(args.json_file)
    if not html_path:
        print("Failed to generate preview HTML")
        return
    
    # Start preview server
    httpd = start_preview_server(args.port)
    
    # Open browser
    webbrowser.open(f"http://localhost:{args.port}/")
    
    try:
        # Keep server running until interrupted
        while True:
            input("Press Enter to stop the server...\n")
            break
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        print("Server stopped")

if __name__ == "__main__":
    main() 