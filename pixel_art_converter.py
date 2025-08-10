import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import os

class PixelArtConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Pixel Art Converter")
        self.root.geometry("1200x800")
        
        # Variables
        self.original_image = None
        self.display_image = None
        self.photo = None
        self.grid_size = None
        self.grid_offset_x = 0
        self.grid_offset_y = 0
        self.corner_points = []
        self.grid_overlay = None
        self.is_drawing_grid = False
        
        # Zoom variables
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.last_pan_x = 0
        self.last_pan_y = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel for image display
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Control buttons
        ttk.Button(left_panel, text="Open Image", command=self.open_image).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Select Pixel Corners", command=self.start_corner_selection).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Clear Selection", command=self.clear_selection).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Process Image", command=self.process_image).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Save Result", command=self.save_result).pack(fill=tk.X, pady=5)
        
        # Zoom controls
        zoom_frame = ttk.LabelFrame(left_panel, text="Zoom Controls")
        zoom_frame.pack(fill=tk.X, pady=10)
        
        zoom_buttons_frame = ttk.Frame(zoom_frame)
        zoom_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(zoom_buttons_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(zoom_buttons_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        ttk.Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom).pack(fill=tk.X, pady=2)
        ttk.Button(zoom_frame, text="Fit to Window", command=self.fit_to_window).pack(fill=tk.X, pady=2)
        
        # Status label
        self.status_label = ttk.Label(left_panel, text="No image loaded", wraplength=180)
        self.status_label.pack(fill=tk.X, pady=10)
        
        # Instructions
        instructions = """
Instructions:
1. Open an AI-generated image
2. Use zoom controls to get a close view
3. Click "Select Pixel Corners"
4. Click two corners of what looks like a pixel
5. Click "Process Image" to convert
6. Save the result

Zoom Controls:
• Zoom In/Out buttons or mouse wheel
• Right-click and drag to pan
• Middle-click to reset zoom
• "Fit to Window" to reset view
        """
        ttk.Label(left_panel, text=instructions, wraplength=180, justify=tk.LEFT).pack(fill=tk.X, pady=10)
        
        # Create a frame for the canvas and scrollbars
        canvas_frame = ttk.Frame(right_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image display area
        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="cross")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Button-3>", self.start_pan)  # Right click to start panning
        self.canvas.bind("<B3-Motion>", self.pan)  # Right click drag to pan
        self.canvas.bind("<ButtonRelease-3>", self.stop_pan)  # Release right click to stop panning
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Mouse wheel to zoom
        self.canvas.bind("<Button-2>", self.on_middle_click)  # Middle click to reset zoom
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                
                # Convert to RGBA if it has transparency, RGB otherwise
                if self.original_image.mode in ('RGBA', 'LA', 'P'):
                    # Handle images with transparency
                    if self.original_image.mode == 'P':
                        self.original_image = self.original_image.convert('RGBA')
                    elif self.original_image.mode == 'LA':
                        # Convert LA to RGBA
                        rgb_image = self.original_image.convert('RGB')
                        alpha = self.original_image.split()[-1]
                        self.original_image = Image.merge('RGBA', (*rgb_image.split(), alpha))
                else:
                    # Convert to RGB for images without transparency
                    self.original_image = self.original_image.convert('RGB')
                
                self.display_image = self.original_image.copy()
                self.update_display()
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
                self.clear_selection()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")
    
    def update_display(self):
        if self.display_image:
            # Calculate display size to fit in canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not yet sized, use default
                canvas_width, canvas_height = 800, 600
            
            # Calculate base scale to fit image in canvas
            img_width, img_height = self.display_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            base_scale = min(scale_x, scale_y, 1.0)  # Don't scale up
            
            # Apply zoom level
            scale = base_scale * self.zoom_level
            
            # Resize for display
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            
            # Handle transparent images properly for display (white background for viewing)
            if self.display_image.mode == 'RGBA':
                # Create a white background for transparent images (for display only)
                background = Image.new('RGB', (display_width, display_height), (255, 255, 255))
                
                # Use faster resampling for better performance
                resampling = Image.Resampling.NEAREST if self.zoom_level >= 2.0 else Image.Resampling.LANCZOS
                resized_image = self.display_image.resize((display_width, display_height), resampling)
                
                # Composite the transparent image onto white background
                background.paste(resized_image, (0, 0), resized_image)
                self.display_image_resized = background
            else:
                # Use faster resampling for better performance
                resampling = Image.Resampling.NEAREST if self.zoom_level >= 2.0 else Image.Resampling.LANCZOS
                self.display_image_resized = self.display_image.resize((display_width, display_height), resampling)
            
            self.photo = ImageTk.PhotoImage(self.display_image_resized)
            
            # Update canvas
            self.canvas.delete("all")
            
            # Apply pan offset
            x_offset = self.pan_x
            y_offset = self.pan_y
            
            self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)
            
            # Set proper scroll region to include the entire image area
            scroll_left = min(0, x_offset)
            scroll_top = min(0, y_offset)
            scroll_right = max(canvas_width, x_offset + display_width)
            scroll_bottom = max(canvas_height, y_offset + display_height)
            
            self.canvas.configure(scrollregion=(scroll_left, scroll_top, scroll_right, scroll_bottom))
            
            # Store scale for coordinate conversion
            self.scale_factor = scale
    
    def start_corner_selection(self):
        if not self.original_image:
            messagebox.showwarning("Warning", "Please open an image first")
            return
        
        self.is_drawing_grid = True
        self.corner_points = []
        self.status_label.config(text="Click two corners of a pixel")
        self.canvas.config(cursor="crosshair")
    
    def on_canvas_click(self, event):
        if not self.is_drawing_grid or not self.original_image:
            return
        
        # Convert canvas coordinates to image coordinates (accounting for pan and zoom)
        # First, convert from canvas coordinates to image coordinates
        canvas_x = event.x - self.pan_x
        canvas_y = event.y - self.pan_y
        
        # Then convert to actual image coordinates
        x = int(canvas_x / self.scale_factor)
        y = int(canvas_y / self.scale_factor)
        
        # Ensure coordinates are within image bounds
        img_width, img_height = self.original_image.size
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        
        self.corner_points.append((x, y))
        
        # Draw point on canvas at the actual click position
        self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, 
                              fill="red", outline="red", tags="selection")
        
        if len(self.corner_points) == 2:
            self.create_grid()
            self.is_drawing_grid = False
            self.canvas.config(cursor="")
            self.status_label.config(text="Grid created. Click 'Process Image' to convert.")
    
    def on_canvas_motion(self, event):
        if self.is_drawing_grid and len(self.corner_points) == 1:
            # Show preview line
            self.canvas.delete("preview")
            x1, y1 = self.corner_points[0]
            # Convert first point back to canvas coordinates
            canvas_x1 = int(x1 * self.scale_factor) + self.pan_x
            canvas_y1 = int(y1 * self.scale_factor) + self.pan_y
            # Draw line from first point to current mouse position
            self.canvas.create_line(canvas_x1, canvas_y1, event.x, event.y, 
                                  fill="red", dash=(5, 5), tags="preview")
    
    def create_grid(self):
        if len(self.corner_points) != 2:
            return
        
        # Calculate grid size and offset
        x1, y1 = self.corner_points[0]
        x2, y2 = self.corner_points[1]
        
        # Calculate the diagonal distance
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        self.grid_size = max(dx, dy)  # Use the larger dimension as grid size
        
        if self.grid_size < 2:
            messagebox.showwarning("Warning", "Grid size too small. Please select points further apart.")
            self.clear_selection()
            return
        
        # Calculate grid offset based on the first point
        # This ensures the grid aligns with the pixel boundaries you selected
        self.grid_offset_x = x1 % self.grid_size
        self.grid_offset_y = y1 % self.grid_size
        
        # Create grid overlay
        self.draw_grid_overlay()
    
    def draw_grid_overlay(self):
        if not self.original_image or not self.grid_size:
            return
        
        img_width, img_height = self.original_image.size
        
        # Create grid overlay image
        self.grid_overlay = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.grid_overlay)
        
        # Optimize grid drawing by limiting the number of lines for large images
        max_lines = 100  # Limit to prevent excessive drawing
        
        # Draw vertical grid lines with offset
        x_lines = 0
        for x in range(self.grid_offset_x, img_width, self.grid_size):
            if x_lines >= max_lines:
                break
            draw.line([(x, 0), (x, img_height)], fill=(255, 0, 0, 128), width=1)
            x_lines += 1
        
        # Draw horizontal grid lines with offset
        y_lines = 0
        for y in range(self.grid_offset_y, img_height, self.grid_size):
            if y_lines >= max_lines:
                break
            draw.line([(0, y), (img_width, y)], fill=(255, 0, 0, 128), width=1)
            y_lines += 1
        
        # Overlay grid on display image
        self.display_image = self.original_image.copy()
        self.display_image.paste(self.grid_overlay, (0, 0), self.grid_overlay)
        self.update_display()
    
    def clear_selection(self):
        self.corner_points = []
        self.grid_size = None
        self.grid_offset_x = 0
        self.grid_offset_y = 0
        self.grid_overlay = None
        self.is_drawing_grid = False
        self.canvas.delete("all")
        self.canvas.config(cursor="")
        
        if self.original_image:
            self.display_image = self.original_image.copy()
            self.update_display()
        
        self.status_label.config(text="Selection cleared")
    
    def process_image(self):
        if not self.original_image or not self.grid_size:
            messagebox.showwarning("Warning", "Please select pixel corners first")
            return
        
        try:
            # Show processing status
            self.status_label.config(text="Processing image...")
            self.root.update()
            
            # Convert to pixel art
            pixel_art = self.convert_to_pixel_art()
            
            # Display result
            self.display_image = pixel_art
            self.update_display()
            
            self.status_label.config(text="Image processed successfully!")
            messagebox.showinfo("Success", "Image converted to pixel art!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing image: {str(e)}")
            self.status_label.config(text="Processing failed")
    
    def convert_to_pixel_art(self):
        if not self.original_image or not self.grid_size:
            return None
        
        # Keep original image mode for transparency preservation
        original_mode = self.original_image.mode
        img_array = np.array(self.original_image)
        
        img_height, img_width = img_array.shape[:2]
        
        # Calculate effective image area after offset
        effective_width = img_width - self.grid_offset_x
        effective_height = img_height - self.grid_offset_y
        
        # Calculate number of grid cells
        grid_cols = effective_width // self.grid_size
        grid_rows = effective_height // self.grid_size
        
        # Optimize for large images by using vectorized operations
        if grid_rows * grid_cols > 10000:  # For very large grids, use numpy operations
            # Create coordinate arrays
            col_coords = np.arange(grid_cols) * self.grid_size + self.grid_offset_x + self.grid_size // 2
            row_coords = np.arange(grid_rows) * self.grid_size + self.grid_offset_y + self.grid_size // 2
            
            # Ensure coordinates are within bounds
            col_coords = np.clip(col_coords, 0, img_width - 1)
            row_coords = np.clip(row_coords, 0, img_height - 1)
            
            # Use advanced indexing for faster sampling
            output_array = img_array[row_coords[:, np.newaxis], col_coords]
        else:
            # For smaller grids, use the original loop method
            output_array = np.zeros((grid_rows, grid_cols, img_array.shape[2]), dtype=img_array.dtype)
            
            for row in range(grid_rows):
                for col in range(grid_cols):
                    # Calculate center point of grid cell with offset
                    center_x = self.grid_offset_x + col * self.grid_size + self.grid_size // 2
                    center_y = self.grid_offset_y + row * self.grid_size + self.grid_size // 2
                    
                    # Ensure we don't go out of bounds
                    center_x = min(center_x, img_width - 1)
                    center_y = min(center_y, img_height - 1)
                    
                    # Get color at center point
                    output_array[row, col] = img_array[center_y, center_x]
        
        # Convert back to PIL Image with original mode to preserve transparency
        pixel_art = Image.fromarray(output_array, mode=original_mode)
        
        # Scale up to original size for display
        display_width = grid_cols * self.grid_size
        display_height = grid_rows * self.grid_size
        pixel_art_display = pixel_art.resize((display_width, display_height), Image.Resampling.NEAREST)
        
        return pixel_art_display
    
    def save_result(self):
        if not self.display_image or self.display_image == self.original_image:
            messagebox.showwarning("Warning", "No processed image to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Pixel Art",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.display_image.save(file_path)
                messagebox.showinfo("Success", f"Pixel art saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
    
    # Zoom and pan methods
    def zoom_in(self):
        if self.original_image:
            self.zoom_level = min(self.zoom_level * 1.5, 10.0)  # Max 10x zoom
            self.update_display()
            self.status_label.config(text=f"Zoom: {self.zoom_level:.1f}x")
    
    def zoom_out(self):
        if self.original_image:
            self.zoom_level = max(self.zoom_level / 1.5, 0.1)  # Min 0.1x zoom
            self.update_display()
            self.status_label.config(text=f"Zoom: {self.zoom_level:.1f}x")
    
    def reset_zoom(self):
        if self.original_image:
            self.zoom_level = 1.0
            self.pan_x = 0
            self.pan_y = 0
            self.update_display()
            # Reset scroll position to top-left
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
            self.status_label.config(text="Zoom reset")
    
    def fit_to_window(self):
        if self.original_image:
            self.zoom_level = 1.0
            self.pan_x = 0
            self.pan_y = 0
            self.update_display()
            # Reset scroll position to top-left
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
            self.status_label.config(text="Fitted to window")
    
    def start_pan(self, event):
        if self.original_image:
            self.is_panning = True
            self.last_pan_x = event.x
            self.last_pan_y = event.y
            self.canvas.config(cursor="fleur")  # Cross cursor for panning
    
    def pan(self, event):
        if self.is_panning and self.original_image:
            dx = event.x - self.last_pan_x
            dy = event.y - self.last_pan_y
            self.pan_x += dx
            self.pan_y += dy
            self.last_pan_x = event.x
            self.last_pan_y = event.y
            
            # Ensure pan doesn't go too far in any direction
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if hasattr(self, 'photo'):
                img_width = self.photo.width()
                img_height = self.photo.height()
                
                # Limit pan to keep some part of the image visible
                max_pan_x = max(0, img_width - canvas_width // 4)
                max_pan_y = max(0, img_height - canvas_height // 4)
                min_pan_x = min(0, -(img_width - canvas_width * 3 // 4))
                min_pan_y = min(0, -(img_height - canvas_height * 3 // 4))
                
                self.pan_x = max(min_pan_x, min(max_pan_x, self.pan_x))
                self.pan_y = max(min_pan_y, min(max_pan_y, self.pan_y))
            
            # Update display immediately for responsive panning
            self.update_display()
    
    def stop_pan(self, event):
        if self.original_image:
            self.is_panning = False
            self.canvas.config(cursor="")
    
    def on_mousewheel(self, event):
        if self.original_image:
            # Zoom in/out with mouse wheel
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
    
    def on_middle_click(self, event):
        if self.original_image:
            # Middle click to reset zoom
            self.reset_zoom()

def main():
    root = tk.Tk()
    app = PixelArtConverter(root)
    
    # Handle window resize
    def on_resize(event):
        if hasattr(app, 'display_image') and app.display_image:
            app.update_display()
    
    root.bind("<Configure>", on_resize)
    
    root.mainloop()

if __name__ == "__main__":
    main()
