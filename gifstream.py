import requests
from PIL import Image
import io
import time
import board
import displayio
import framebufferio
import rgbmatrix

GIF_URL = "https://media1.tenor.com/m/1u15ulrFh1EAAAAd/asc.gif"

def fetch_gif():
    """Fetch GIF from URL and return PIL Image object"""
    try:
        print(f"Fetching GIF from {GIF_URL}...")
        response = requests.get(GIF_URL, stream=True)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(f"Error fetching GIF: {e}")
        return None

def convert_frame(frame):
    """Convert a PIL Image frame to matrix format"""
    frame = frame.convert('RGB').resize((64, 32), Image.Resampling.LANCZOS)
    frame_data = []
    for y in range(32):
        row = []
        for x in range(64):
            r, g, b = frame.getpixel((x, y))[:3]
            color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            color = min(color, 65534)
            row.append(color)
        frame_data.append(row)
    return frame_data

def show_frame(frame_data, display):
    """Display a frame on the matrix"""
    bitmap = displayio.Bitmap(64, 32, 65535)
    palette = displayio.Palette(65535)
    
    for i in range(65535):
        r = ((i >> 11) & 0x1F) << 3
        g = ((i >> 5) & 0x3F) << 2
        b = (i & 0x1F) << 3
        palette[i] = (r << 16) | (g << 8) | b
    
    for y in range(32):
        for x in range(64):
            bitmap[x, y] = frame_data[y][x]
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group()
    group.append(tile_grid)
    display.root_group = group

def main():
    displayio.release_displays()
    matrix = rgbmatrix.RGBMatrix(
        width=64, height=32, bit_depth=6,
        rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
        addr_pins=[board.A5, board.A4, board.A3, board.A2],
        clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
    )
    display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
    
    while True:
        im = fetch_gif()
        if not im:
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue
            
        n_frames = getattr(im, "n_frames", 1)
        print(f"Streaming {n_frames} frames...")
        
        try:
            while True:
                for frame_idx in range(n_frames):
                    im.seek(frame_idx)
                    frame_data = convert_frame(im)
                    show_frame(frame_data, display)
                    duration = im.info.get('duration', 100)
                    time.sleep(duration / 1000.0)
                    
        except Exception as e:
            print(f"Error during streaming: {e}")
            print("Restarting stream in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main() 