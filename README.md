# AI Pixel Art Converter

A Python application that converts AI-generated images to pixel art by allowing you to define the pixel grid size and processing the image accordingly.

## Features

- Open AI-generated images that are supposed to be pixel art but aren't actually pixelated
- **Zoom and pan functionality** for precise pixel corner selection
- Select two corners of what looks like a pixel to define the grid size
- Automatically create a grid overlay based on your selection
- Process the image to create a pixel-perfect version
- Save the resulting pixel art

## Installation

1. Make sure you have Python 3.7+ installed on your system
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python pixel_art_converter.py
```

2. **Open Image**: Click "Open Image" to select an AI-generated image that should be pixel art

3. **Select Pixel Corners**: 
   - Use zoom controls to get a close view of the image for precise selection
   - Click "Select Pixel Corners" to start the selection process
   - Click on two corners of what appears to be a single pixel in the image
   - The application will calculate the grid size based on the diagonal distance between these points
   - A red grid overlay will appear showing how the image will be divided

4. **Process Image**: Click "Process Image" to convert the image to pixel art
   - The application reads the color from the center of each grid cell
   - Creates a new image where each grid cell becomes a single pixel
   - Scales the result back to the original size

5. **Save Result**: Click "Save Result" to save the pixel art image

## How It Works

1. **Grid Definition**: You select two points that represent the corners of what should be a single pixel
2. **Grid Creation**: The application creates a grid where each cell is the size of your selection
3. **Color Sampling**: For each grid cell, the color at the center point is sampled
4. **Pixel Art Generation**: A new image is created where each grid cell becomes a single pixel with the sampled color
5. **Scaling**: The result is scaled back to the original image size for display

## Tips for Best Results

- **Use zoom controls** to get a precise view when selecting pixel corners
- Choose points that clearly represent the intended pixel size in the AI-generated image
- Make sure your selection points are far enough apart to create a meaningful grid
- The larger the grid size, the more pixelated the result will be
- For best results, use images that were intended to be pixel art but have anti-aliasing or blurring

## Requirements

- Python 3.7+
- Pillow (PIL)
- NumPy
- tkinter (usually comes with Python)

## Troubleshooting

- If the grid appears too small, try selecting points that are further apart
- If the image doesn't load, make sure it's in a supported format (PNG, JPG, JPEG, BMP, GIF, TIFF)
- If you get an error about missing modules, make sure you've installed the requirements

## Example Workflow

1. Open an AI-generated "pixel art" image that has smooth edges
2. **Zoom in** to get a close view of the pixels for precise selection
3. Select two corners of what should be a single pixel (e.g., from one corner to the opposite corner of a colored square)
4. Review the red grid overlay to ensure it matches your expectations
5. Process the image to create true pixel art
6. Save the result

## Zoom Controls

- **Zoom In/Out buttons**: Click to zoom in or out
- **Mouse wheel**: Scroll to zoom in/out
- **Right-click and drag**: Pan around when zoomed in
- **Middle-click**: Reset zoom to fit window
- **Reset Zoom button**: Reset zoom and pan to default
- **Fit to Window button**: Reset view to fit the entire image

The application will create a true pixel art version where each grid cell becomes a single, solid-colored pixel.
