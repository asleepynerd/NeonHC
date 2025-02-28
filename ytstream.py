import time
import board
import displayio
import framebufferio
import rgbmatrix
import urllib.request
import json
import io
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

VIDEO_ID = "dQw4w9WgXcQ" 

COBALT_API = "http://35.204.199.3:9000/"
GIF_API = "http://35.204.199.3:3000/convert/video/to/gif"

def get_gif():
    """Get video and convert to GIF"""
    try:
        print("Fetching video info...")
        
        data = json.dumps({
            "url": f"https://youtube.com/watch?v={VIDEO_ID}",
            "videoQuality": "144",
            "youtubeVideoCodec": "h264"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            COBALT_API,
            data=data,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            
        if result.get('status') not in ['stream', 'tunnel']:
            print("Error: Unexpected response from Cobalt API: ", result)
            return None
            
        print("Downloading video...")
        video_url = result['url']
        with urllib.request.urlopen(video_url) as response:
            video_data = response.read()
            
        print("Converting to GIF...")
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        
        form_data = bytearray()
        
        form_data.extend(f'--{boundary}\r\n'.encode('utf-8'))
        form_data.extend(b'Content-Disposition: form-data; name="file"; filename="video.mp4"\r\n')
        form_data.extend(b'Content-Type: video/mp4\r\n\r\n')
        form_data.extend(video_data)
        form_data.extend(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
        
        req = urllib.request.Request(
            GIF_API,
            data=form_data,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            gif_data = response.read()
            
        return gif_data
                
    except Exception as e:
        print(f"Error getting GIF: {e}")
        return None

def read_frames(gif_data):
    """Read frames from GIF data"""
    try:
        gif = Image.open(io.BytesIO(gif_data))
        n_frames = getattr(gif, 'n_frames', 1)
        print(f"Found {n_frames} frames")
        
        while True:
            for frame_idx in range(n_frames):
                gif.seek(frame_idx)
                frame = gif.convert('RGB')
                frame = frame.resize((64, 32), Image.Resampling.LANCZOS)
                
                duration = gif.info.get('duration', 100)
                
                frame_data = []
                for y in range(32):
                    row = []
                    for x in range(64):
                        r, g, b = frame.getpixel((x, y))
                        color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                        color = min(color, 65534)
                        row.append(color)
                    frame_data.append(row)
                yield frame_data, duration / 1000.0
                
    except Exception as e:
        print(f"Error reading frames: {e}")

def show_frame(frame_data, display):
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
        try:
            gif_data = get_gif()
            if not gif_data:
                raise Exception("Failed to get GIF")
                
            print("Playing video...")
            for frame, duration in read_frames(gif_data):
                start_time = time.monotonic()
                show_frame(frame, display)
                elapsed = time.monotonic() - start_time
                
                remaining = duration - elapsed
                if remaining > 0:
                    time.sleep(remaining)
                
        except Exception as e:
            print(f"Error: {e}")
            
        print("Restarting video in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    main() 
