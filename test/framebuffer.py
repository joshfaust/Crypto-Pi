import numpy as np
import struct

def create_test_pattern(width=480, height=320, line_length=960):
    """Create a test pattern matching the exact framebuffer parameters."""
    with open('data.out', 'wb') as f:
        for y in range(height):
            line_data = bytearray(line_length)
            for x in range(width):
                # Calculate color components
                hue = (x + y) / (width + height)
                if y < height // 2:
                    if x < width // 2:
                        # Top-left: Red to Yellow
                        r = 31
                        g = int((x / (width/2)) * 63)
                        b = 0
                    else:
                        # Top-right: Yellow to Green
                        r = int((1 - (x - width/2)/(width/2)) * 31)
                        g = 63
                        b = 0
                else:
                    if x < width // 2:
                        # Bottom-left: Red to Purple
                        r = 31
                        g = 0
                        b = int((y - height/2)/(height/2) * 31)
                    else:
                        # Bottom-right: Full rainbow
                        r = int(((1 + np.sin(hue * 2 * np.pi)) / 2) * 31)
                        g = int(((1 + np.sin(hue * 2 * np.pi + 2*np.pi/3)) / 2) * 63)
                        b = int(((1 + np.sin(hue * 2 * np.pi + 4*np.pi/3)) / 2) * 31)
                
                # Pack into RGB565
                pixel = (r << 11) | (g << 5) | b
                
                # Write to line buffer
                pos = x * 2  # 2 bytes per pixel
                struct.pack_into('<H', line_data, pos, pixel)
            
            # Write complete line
            f.write(line_data)
            f.flush()

if __name__ == "__main__":
    create_test_pattern()
    print("Test pattern created. Display with:")
    print("cat data.out > /dev/fb1")