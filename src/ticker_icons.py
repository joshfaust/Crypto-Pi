from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import time
import os
from pathlib import Path

class TickerIcons:
    """Class to handle cryptocurrency and stock icons.
    
    This class provides both bitmap loading and vector drawing capabilities
    for financial symbols.
    
    Attributes:
        icon_size (int): The size of icons in pixels.
        icon_cache (Dict): Cache of loaded bitmap icons.
    """
    
    def __init__(self, icon_size: int = 32):
        """Initialize the TickerIcons handler.
        
        Args:
            icon_size: Size in pixels for icons. Defaults to 32.
        """
        self.icon_size = icon_size
        self.icon_cache: Dict[str, Image.Image] = {}
        
    def load_icon(self, symbol: str, icons_dir: str = "icons") -> Optional[Image.Image]:
        """Load an icon from file if available.
        
        Args:
            symbol: The ticker symbol to load an icon for.
            icons_dir: Directory containing icon files.
            
        Returns:
            PIL Image if found, None otherwise.
        """
        if symbol in self.icon_cache:
            return self.icon_cache[symbol]
            
        # Check common image formats
        for ext in ['.png', '.jpg', '.jpeg']:
            icon_path = Path(icons_dir) / f"{symbol.lower()}{ext}"
            if icon_path.exists():
                try:
                    img = Image.open(icon_path)
                    # Convert to RGBA if not already
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    # Resize maintaining aspect ratio
                    img.thumbnail((self.icon_size, self.icon_size))
                    self.icon_cache[symbol] = img
                    return img
                except Exception as e:
                    print(f"Error loading icon for {symbol}: {e}")
                    return None
        return None
    
    def draw_vector_icon(self, symbol: str) -> Optional[Image.Image]:
        """Create a vector-style icon for symbols without bitmap icons.
        
        Args:
            symbol: The ticker symbol to create an icon for.
            
        Returns:
            PIL Image with the drawn icon.
        """
        img = Image.new('RGBA', (self.icon_size, self.icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simple circular background with text
        padding = 2
        draw.ellipse([padding, padding, self.icon_size-padding, self.icon_size-padding], 
                    fill=(41, 41, 41, 255))
        
        # Try to load font for symbol
        try:
            # Estimate font size to fit circle
            font_size = int(self.icon_size * 0.5)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Center text
        symbol_text = symbol[:3]  # Take first 3 chars only
        text_bbox = draw.textbbox((0, 0), symbol_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (self.icon_size - text_width) // 2
        y = (self.icon_size - text_height) // 2
        
        draw.text((x, y), symbol_text, fill=(255, 255, 255, 255), font=font)
        return img
