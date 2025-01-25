from PIL import Image
import sys
import os

def generate_matrix_code(gif_path, output_path, frame_limit=None):
    """Convert a GIF file to Python code for RGB matrix display."""
    
    try:
        im = Image.open(gif_path)
    except Exception as e:
        print(f"Error opening GIF file: {e}")
        return

    n_frames = getattr(im, "n_frames", 1)
    if frame_limit:
        n_frames = min(n_frames, frame_limit)
        
    frame_durations = []
    frames_data = []
    
    try:
        for frame_idx in range(n_frames):
            im.seek(frame_idx)
            frame = im.convert('RGB')
            
            frame = frame.resize((64, 32), Image.Resampling.LANCZOS)
            
            duration = im.info.get('duration', 100) 
            frame_durations.append(duration)
            
            frame_pixels = []
            for y in range(32):
                row = []
                for x in range(64):
                    r, g, b = frame.getpixel((x, y))[:3]
                    color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                    color = min(color, 65534)
                    row.append(color)
                frame_pixels.append(row)
            frames_data.append(frame_pixels)
            
    except Exception as e:
        print(f"Error processing frames: {e}")
        return

    with open(output_path, 'w') as f:
        f.write("""import time
import board
import displayio
import framebufferio
import rgbmatrix

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, 
    height=32, 
    bit_depth=6,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, 
    latch_pin=board.D0, 
    output_enable_pin=board.D1
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

FRAME_DATA = [
""")

        for frame in frames_data:
            f.write("    [\n")
            for row in frame:
                f.write("        [")
                f.write(", ".join(str(color) for color in row))
                f.write("],\n")
            f.write("    ],\n")
        
        f.write("]\n\n")
        
        f.write("FRAME_DURATIONS = [\n    ")
        f.write(", ".join(str(d) for d in frame_durations))
        f.write("\n]\n\n")

        f.write("""
def show_frame(frame_data):
    bitmap = displayio.Bitmap(64, 32, 65535)
    palette = displayio.Palette(65535)
    
    for i in range(65535):
        r = ((i >> 11) & 0x1F) << 3
        g = ((i >> 5) & 0x3F) << 2
        b = (i & 0x1F) << 3
        palette[i] = (r << 16) | (g << 8) | b
    
    for y in range(32):
        for x in range(64):
            color = frame_data[y][x]
            bitmap[x, y] = color
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group()
    group.append(tile_grid)
    display.root_group = group

def main():
    frame_idx = 0
    while True:
        show_frame(FRAME_DATA[frame_idx])
        time.sleep(FRAME_DURATIONS[frame_idx] / 1000.0)
        frame_idx = (frame_idx + 1) % len(FRAME_DATA)

if __name__ == "__main__":
    main()
""")

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python gifconv.py input.gif output.py [frame_limit]")
        return
    
    input_gif = sys.argv[1]
    output_py = sys.argv[2]
    frame_limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    if not os.path.exists(input_gif):
        print(f"Error: Input file '{input_gif}' not found")
        return
        
    print(f"Converting {input_gif} to Python code...")
    if frame_limit:
        print(f"Using first {frame_limit} frames only")
    generate_matrix_code(input_gif, output_py, frame_limit)
    print(f"Done! Output written to {output_py}")

if __name__ == "__main__":
    main()
