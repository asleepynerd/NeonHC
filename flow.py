import time
import board
import displayio
import framebufferio
import rgbmatrix
import math
import random

# Release any previously initialized displays
displayio.release_displays()

# Initialize RGB matrix
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

def hsv_to_rgb(h, s, v):
    h = (h % 360) / 360
    i = math.floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    if i % 6 == 0: r, g, b = v, t, p
    elif i % 6 == 1: r, g, b = q, v, p
    elif i % 6 == 2: r, g, b = p, v, t
    elif i % 6 == 3: r, g, b = p, q, v
    elif i % 6 == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    
    return int(r * 255), int(g * 255), int(b * 255)

def plasma_effect(frame, bitmap, palette):
    for y in range(32):
        for x in range(64):
            v = math.sin(x * 0.1 + frame * 0.1)
            v += math.sin(y * 0.1 + frame * 0.11)
            v += math.sin((x + y) * 0.1 + frame * 0.13)
            v += math.sin(math.sqrt((x*x + y*y) * 0.1) + frame * 0.07)
            color_index = int((v + 4) * 2) % 16
            bitmap[x, y] = color_index

def spiral_effect(frame, bitmap, palette):
    center_x, center_y = 32, 16
    for y in range(32):
        for x in range(64):
            dx = x - center_x
            dy = y - center_y
            angle = math.atan2(dy, dx)
            dist = math.sqrt(dx*dx + dy*dy)
            v = math.sin(dist * 0.3 - frame * 0.1 + angle * 3)
            color_index = int((v + 1) * 8) % 16
            bitmap[x, y] = color_index

def ripple_effect(frame, bitmap, palette):
    for y in range(32):
        for x in range(64):
            dx = x - 32
            dy = y - 16
            dist = math.sqrt(dx*dx + dy*dy)
            v = math.sin(dist * 0.5 - frame * 0.1)
            v += math.sin(dist * 0.33 - frame * 0.15)
            color_index = int((v + 2) * 4) % 16
            bitmap[x, y] = color_index

def update_display(frame):
    bitmap = displayio.Bitmap(64, 32, 16)
    palette = displayio.Palette(16)
    
    # Create a dynamic color palette
    hue_shift = math.sin(frame * 0.02) * 30  # Slowly shift base hue
    for i in range(16):
        r, g, b = hsv_to_rgb((frame + i * 22.5 + hue_shift) % 360, 1.0, 1.0)
        palette[i] = (r << 16) | (g << 8) | b
    
    # Blend between effects based on time
    effect_time = (frame % 720) / 720.0  # 24 seconds per cycle
    
    if effect_time < 0.33:  # First third: plasma
        plasma_effect(frame, bitmap, palette)
    elif effect_time < 0.66:  # Second third: spiral
        if effect_time < 0.4:  # Blend from plasma to spiral
            plasma_effect(frame, bitmap, palette)
            temp_bitmap = displayio.Bitmap(64, 32, 16)
            spiral_effect(frame, temp_bitmap, palette)
            blend = (effect_time - 0.33) * 7.5
            for y in range(32):
                for x in range(64):
                    if random.random() < blend:
                        bitmap[x, y] = temp_bitmap[x, y]
        else:
            spiral_effect(frame, bitmap, palette)
    else:  # Final third: ripple
        if effect_time < 0.73:  # Blend from spiral to ripple
            spiral_effect(frame, bitmap, palette)
            temp_bitmap = displayio.Bitmap(64, 32, 16)
            ripple_effect(frame, temp_bitmap, palette)
            blend = (effect_time - 0.66) * 7.5
            for y in range(32):
                for x in range(64):
                    if random.random() < blend:
                        bitmap[x, y] = temp_bitmap[x, y]
        else:
            ripple_effect(frame, bitmap, palette)
    
    # Create and display the tile grid
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group()
    group.append(tile_grid)
    display.root_group = group

def main():
    frame = 0
    while True:
        update_display(frame)
        frame = (frame + 1) % 720
        time.sleep(0.03)  # ~30 FPS

if __name__ == "__main__":
    main()