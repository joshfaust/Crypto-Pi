from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os, time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
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
        self.back_buffer = Image.new('RGB', (width, height), 'black')
        self.front_buffer = Image.new('RGB', (width, height), 'black')
        self.draw = ImageDraw.Draw(self.back_buffer)
        self.current_buffer = self.back_buffer
        
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

    def reset_display(self) -> None:
        """Completely reset both buffers and redraw from scratch."""
        self.back_buffer = Image.new('RGB', (self.width, self.height), 'black')
        self.front_buffer = Image.new('RGB', (self.width, self.height), 'black')
        self.draw = ImageDraw.Draw(self.back_buffer)
        self.current_buffer = self.back_buffer

    def swap_buffers(self) -> None:
        """Swap the front and back buffers with verification."""
        try:
            # Ensure all drawing operations are complete
            self.back_buffer.load()
            self.front_buffer.load()
            
            # Swap buffers
            self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
            self.draw = ImageDraw.Draw(self.back_buffer)
            self.current_buffer = self.back_buffer
            
        except Exception as e:
            print(f"Error during buffer swap: {e}")
            # Reset on error
            self.reset_display()

    def clear(self) -> None:
        """Clear the display by filling it with black."""
        self.draw.rectangle([0, 0, self.width, self.height], fill='black')

    def update_display(self) -> None:
        """Update the display with the current frame."""
        try:
            # Ensure back buffer is fully rendered
            self.back_buffer.load()
            
            # Swap buffers
            self.swap_buffers()
            
            # Convert the front buffer to RGB565
            rgb_image = self.front_buffer.convert('RGB')
            pixels = np.array(rgb_image)
            
            # Convert RGB888 to RGB565
            r = (pixels[..., 0] >> 3).astype(np.uint16) << 11
            g = (pixels[..., 1] >> 2).astype(np.uint16) << 5
            b = (pixels[..., 2] >> 3).astype(np.uint16)
            rgb565 = r | g | b
            
            # Prepare complete frame
            frame_data = rgb565.tobytes()
            
            # Write to framebuffer in a single operation
            with open(self.fb_device, 'wb') as fb:
                fb.write(frame_data)
                fb.flush()
                os.fsync(fb.fileno())
                
            # Small delay to ensure frame is written
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Error updating display: {e}")
            self.reset_display()

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

    def draw_all_tickers(self, tickers: List[Dict]) -> None:
        """Draw all tickers with improved error handling."""
        try:
            # Reset buffers before drawing new frame
            self.clear()
            
            # Draw header
            self.draw_header()
            
            # Draw each ticker
            for i, ticker in enumerate(tickers):
                self.draw_ticker(
                    position=(10, 45 + i * 55),
                    symbol=str(ticker["symbol"]),
                    price=float(ticker["price"]),
                    change=float(ticker["change"]),
                    volume=float(ticker["volume"])
                )
            
            # Ensure drawing is complete
            self.back_buffer.load()
            
            # Update display
            self.update_display()
            
        except Exception as e:
            print(f"Error in draw_all_tickers: {e}")
            self.reset_display()

    def draw_ticker(self, position: Tuple[int, int], symbol: str, price: float, 
                   change: float, volume: Optional[float] = None) -> None:
        """Draw a single ticker with all its information and icon."""
        x, y = position
        box_height = 50
        box_width = self.width - 20
        
        # Draw background box
        self.draw.rectangle([x, y, x + box_width, y + box_height], 
                          outline=self.GRAY, width=1)
        
        # Load and draw icon
        icon = self.icons.load_icon(symbol) or self.icons.draw_vector_icon(symbol)
        if icon:
            icon_y = y + (box_height - icon.height) // 2
            # Paste to the current buffer instead of self.image
            self.current_buffer.paste(icon, (x + 10, icon_y), icon)
            symbol_x = x + 50
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
