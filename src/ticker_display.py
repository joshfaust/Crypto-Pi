from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
from src.ticker_icons import TickerIcons

class TickerDisplay:
    """A class to handle the display of financial ticker information on a framebuffer device."""

    def __init__(self, width: int = 480, height: int = 320, fb_device: str = '/dev/fb1', icons_dir="./icons") -> None:
        """Initialize the TickerDisplay."""
        self.width = width
        self.height = height
        self.fb_device = fb_device
        self.icons_dir = icons_dir
        self.image = Image.new('RGB', (width, height), 'black')
        self.draw = ImageDraw.Draw(self.image)
        self.icons = TickerIcons(32)  # 32px icons
        
        # Load fonts
        try:
            self.large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            self.large_font = ImageFont.load_default()
            self.medium_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
        
        # Colors
        self.GREEN = '#00FF00'
        self.RED = '#FF0000'
        self.WHITE = '#FFFFFF'
        self.GRAY = '#808080'

    def clear(self) -> None:
        """Clear the display by filling it with black."""
        self.draw.rectangle([0, 0, self.width, self.height], fill='black')

    def update_display(self) -> None:
        """Convert the current image to RGB565 format and write to the framebuffer device."""
        try:
            # Convert to RGB565
            rgb_image = self.image.convert('RGB')
            pixels = np.array(rgb_image)
            
            # Convert RGB888 to RGB565
            r = (pixels[..., 0] >> 3).astype(np.uint16) << 11
            g = (pixels[..., 1] >> 2).astype(np.uint16) << 5
            b = (pixels[..., 2] >> 3).astype(np.uint16)
            rgb565 = r | g | b
            
            # Get frame data
            frame_data = rgb565.tobytes()
            
            # Write in chunks matching hardware buffer (4KB)
            buffer_size = 4096
            with open(self.fb_device, 'wb') as fb:
                for i in range(0, len(frame_data), buffer_size):
                    chunk = frame_data[i:i + buffer_size]
                    fb.write(chunk)
                    fb.flush()
                    # Small delay between chunks to match hardware timing
                    time.sleep(0.0005)  # 0.5ms delay
                
                # Final flush to ensure all data is written
                fb.flush()
                
        except Exception as e:
            print(f"Error updating display: {e}")

    @staticmethod
    def format_price(price: float) -> str:
        """Format a price value with appropriate decimal places.
        
        Args:
            price: The price value to format.
            
        Returns:
            A formatted price string with appropriate decimal places and dollar sign.
        """
        if price >= 1000:
            return f"${price:,.0f}"
        elif price >= 1:
            return f"${price:,.2f}"
        else:
            return f"${price:.4f}"

    @staticmethod
    def format_change(change: float) -> str:
        """Format a percentage change value.
        
        Args:
            change: The percentage change value to format.
            
        Returns:
            A formatted percentage change string with sign and two decimal places.
        """
        return f"{change:+.2f}%"

    def draw_header(self) -> None:
        """Draw the header section with title and current time."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.draw.text((10, 5), "Crypto Tracker", 
                      font=self.medium_font, fill=self.WHITE)
        self.draw.text((self.width - 210, 5), f"Updated: {current_time}", 
                      font=self.medium_font, fill=self.WHITE)
        self.draw.line((10, 35, self.width - 10, 35), fill=self.GRAY)

    def draw_ticker(self, position: Tuple[int, int], symbol: str, price: float, 
                   change: float, volume: Optional[float] = None) -> None:
        """Draw a single ticker with all its information and icon."""
        x, y = position
        box_height = 50
        box_width = self.width - 20
        
        # Draw background box
        self.draw.rectangle([x, y, x + box_width, y + box_height], 
                          outline=self.GRAY, width=1)
        
        # Try to load icon
        icon = self.icons.load_icon(symbol, icons_dir=self.icons_dir) or self.icons.draw_vector_icon(symbol)
        if icon:
            # Calculate icon position (centered vertically in box)
            icon_y = y + (box_height - icon.height) // 2
            # Paste icon with alpha channel
            self.image.paste(icon, (x + 10, icon_y), icon)
            symbol_x = x + 50  # Move symbol text after icon
        else:
            symbol_x = x + 10
        
        # Draw symbol
        self.draw.text((symbol_x, y + 5), symbol, 
                      font=self.large_font, fill=self.WHITE)
        
        # Draw current price
        price_text = self.format_price(price)
        self.draw.text((x + 150, y + 5), price_text, 
                      font=self.large_font, fill=self.WHITE)
        
        # Draw price change
        change_color = self.GREEN if change >= 0 else self.RED
        change_text = self.format_change(change)
        self.draw.text((x + 300, y + 5), change_text, 
                      font=self.large_font, fill=change_color)
        
        # Draw 24h price if provided
        if volume is not None:
            volume_text = f"24h Vol: {self.format_price(volume)}"
            self.draw.text((x + 150, y + 30), volume_text, 
                          font=self.small_font, fill=self.GRAY)