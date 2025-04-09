import json
import os
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f2f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #0077B5; text-align: center; }}
        .carousel {{ display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 20px; padding: 20px 0; }}
        .slide {{ scroll-snap-align: start; flex: 0 0 auto; width: 500px; height: 500px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); position: relative; cursor: pointer; }}
        .slide img {{ width: 100%; height: 100%; object-fit: contain; border-radius: 10px; }}
        .slide-number {{ position: absolute; top: 10px; left: 10px; background-color: rgba(0, 0, 0, 0.5); color: white; padding: 5px 10px; border-radius: 15px; font-size: 14px; }}
        .controls {{ display: flex; justify-content: center; margin-top: 20px; gap: 10px; }}
        button {{ background-color: #0077B5; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background-color: #00669c; }}
        .fullscreen {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.9); display: none; justify-content: center; align-items: center; z-index: 1000; }}
        .fullscreen img {{ max-width: 90%; max-height: 90%; object-fit: contain; }}
        .close-btn {{ position: absolute; top: 20px; right: 20px; color: white; font-size: 30px; cursor: pointer; }}
        .slide-info {{ margin-top: 20px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }}
        .metadata {{ margin-top: 40px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }}
        pre {{ background-color: #f7f7f7; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="carousel" id="carousel">
            {slides_html}
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
        const jsonFilePath = "{json_file_path_for_js}"; // Path for fetching data
        const workspaceRoot = "{workspace_root_for_js}"; // Workspace root for resolving paths

        // Function to resolve relative paths from the workspace root
        function resolvePath(relativePath) {
            // Normalize path separators for web
            const normalizedWorkspace = workspaceRoot.replace(/\\/g, '/');
            const normalizedRelative = relativePath.replace(/\\/g, '/');
            
            // Construct absolute path, then make it relative to the server root
            // Assumes the server runs from the workspace root
            let absolutePath = normalizedWorkspace + '/' + normalizedRelative;
            // Basic cleanup for potential double slashes, etc.
            absolutePath = absolutePath.replace(/\/\//g, '/'); 
            // Remove leading slash if server serves from root
            if (absolutePath.startsWith('/')) {
                absolutePath = absolutePath.substring(1);
            }
            return '/' + absolutePath; // Prepend slash for URL path
        }

        // Fetch carousel data using the relative path
        fetch(resolvePath(jsonFilePath))
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                carouselData = data;
                // Make image paths relative to server root
                carouselData.slides.forEach(slide => {
                    slide.image_path_web = resolvePath(slide.image_path); 
                });
                metadataJson.textContent = JSON.stringify(carouselData, null, 2);
                updateSlideInfo();
                // Update image sources after data is loaded
                slides.forEach((slideDiv, index) => {
                   const img = slideDiv.querySelector('img');
                   if(carouselData.slides[index]) {
                       img.src = carouselData.slides[index].image_path_web;
                       img.alt = `Slide ${carouselData.slides[index].number}`;
                   } else {
                       console.error("Mismatch between HTML slides and JSON data");
                   }
                });
            })
            .catch(error => {
                console.error('Error loading carousel data:', error);
                metadataJson.textContent = `Error loading carousel data from ${resolvePath(jsonFilePath)}: ${error}`;
            });
        
        function scrollToSlide(index) {
            if (!slides || slides.length === 0) return;
            if (index < 0) index = 0;
            if (index >= slides.length) index = slides.length - 1;
            
            currentSlide = index;
            slides[index].scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'start' }});
            updateSlideInfo();
        }
        
        function updateSlideInfo() {
            if (!carouselData || !carouselData.slides || !carouselData.slides[currentSlide]) return;
            const slide = carouselData.slides[currentSlide];
            const heading = slide.heading || '';
            const content = (slide.content || '').replace(/\n/g, '<br>');
            slideInfo.innerHTML = `<h3>Slide ${slide.number}: ${heading}</h3><p>${content}</p>`;
        }
        
        prevBtn.addEventListener('click', () => scrollToSlide(currentSlide - 1));
        nextBtn.addEventListener('click', () => scrollToSlide(currentSlide + 1));
        
        downloadBtn.addEventListener('click', () => {
            if (!carouselData || !carouselData.pdf_path) {
                 console.error("PDF path not found in carousel data");
                 return;
            }
            window.open(resolvePath(carouselData.pdf_path), '_blank');
        });
        
        slides.forEach((slide, index) => {
            slide.addEventListener('click', () => {
                if (!carouselData || !carouselData.slides[index]) return;
                fullscreenImg.src = resolvePath(carouselData.slides[index].image_path);
                fullscreen.style.display = 'flex';
            });
        });
        
        closeBtn.addEventListener('click', () => fullscreen.style.display = 'none');
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') scrollToSlide(currentSlide - 1);
            else if (e.key === 'ArrowRight') scrollToSlide(currentSlide + 1);
            else if (e.key === 'Escape' && fullscreen.style.display === 'flex') fullscreen.style.display = 'none';
        });
        
        // Initial setup
        if (slides.length > 0) {
             scrollToSlide(0);
        } else {
             console.warn("No slides found in the HTML.");
        }

    </script>
</body>
</html>
"""

def generate_preview_html(json_file, workspace_root):
    """Generate HTML page for previewing the carousel"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        title = data.get('title', 'LinkedIn Carousel')
        slides = data.get('slides', [])
        
        # Create HTML directory if it doesn't exist
        # This path is relative to where the script is run (workspace root)
        html_dir = Path("preview_html") 
        html_dir.mkdir(exist_ok=True)
        
        slides_html = ""
        for slide in slides:
            slide_number = slide.get('number', '?')
            # We'll set the actual src in the JS after loading data
            slides_html += f""" 
            <div class="slide">
                <img src="" alt="Loading slide {slide_number}...">
                <div class="slide-number">Slide {slide_number}</div>
            </div>"""

        # Prepare paths for JavaScript, relative to workspace root
        json_file_rel = os.path.relpath(json_file, workspace_root)
        workspace_root_js = workspace_root.replace('\\', '/') # Ensure forward slashes for JS
        json_file_path_for_js = json_file_rel.replace('\\', '/')

        # Create HTML file
        html_path = html_dir / "index.html"
        with open(html_path, 'w') as f:
            f.write(HTML_TEMPLATE.format(
                title=title, 
                slides_html=slides_html,
                json_file_path_for_js=json_file_path_for_js,
                workspace_root_for_js=workspace_root_js,
                # Add pdf_path_for_js if needed, ensuring it's relative to workspace
                pdf_path_for_js=os.path.relpath(data.get('pdf_path', ''), workspace_root).replace('\\', '/')
            ))
            
        print(f"Generated preview HTML at: {html_path}")
        return str(html_path) # Return the path relative to workspace root
    except Exception as e:
        print(f"Error generating preview HTML: {e}")
        return None 