import base64
import hashlib
import io
import logging
import os
from typing import Dict, Optional

import requests
from PIL import Image, UnidentifiedImageError

from ..config import settings

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Service for processing images using Gemini API"""

    def __init__(self):
        """Initialize the image processor with Gemini API key"""
        self.api_key = settings.google_api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert an image file to base64 string using direct file read"""
        try:
            logger.info(f"[ImageProcessor] Reading image file directly: {image_path}")
            
            # Get file stats before reading
            file_size = os.path.getsize(image_path)
            logger.info(f"[ImageProcessor] Original file size: {file_size} bytes")
            
            # Read file and calculate hash
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            file_hash = hashlib.md5(image_data).hexdigest()
            logger.info(f"[ImageProcessor] Original file MD5 hash: {file_hash}")
            
            # Encode to base64
            base64_data = base64.b64encode(image_data).decode("utf-8")
            
            # Log base64 metrics
            base64_length = len(base64_data)
            base64_hash = hashlib.md5(base64_data.encode("utf-8")).hexdigest()
            
            logger.info(f"[ImageProcessor] Base64 string length: {base64_length} characters")
            logger.info(f"[ImageProcessor] Base64 MD5 hash: {base64_hash}")
            logger.debug(f"Base64 start: {base64_data[:20]}...")
            logger.debug(f"Base64 end: ...{base64_data[-20:]}")
            
            return base64_data  # Just return the encoded data, no API calls here
        except Exception as e:
            logger.error(f"[ImageProcessor] Error encoding image: {str(e)}", exc_info=True)
            raise

    def validate_base64_image(self, base64_str: str) -> bool:
        """Validate that a base64 string can be decoded to a valid image"""
        try:
            decoded = base64.b64decode(base64_str)
            
            # Verify the decoded data starts with common image magic numbers
            if len(decoded) < 8:
                return False
                
            # Check for common image file signatures
            magic_numbers = {
                b'\xFF\xD8\xFF': 'JPEG',
                b'\x89PNG\r\n\x1a\n': 'PNG',
                b'GIF87a': 'GIF',
                b'GIF89a': 'GIF',
                b'BM': 'BMP',
                b'II*\x00': 'TIFF',
                b'MM\x00*': 'TIFF'
            }
            
            matches = [fmt for magic, fmt in magic_numbers.items() 
                      if decoded.startswith(magic)]
            
            if not matches:
                logger.warning("Decoded data doesn't match known image formats")
                return False
            
            # Try to open with PIL to verify it's a valid image
            try:
                Image.open(io.BytesIO(decoded)).verify()
                return True
            except Exception:
                return False
                
        except Exception:
            return False

    def _get_mime_type(self, image_path: str) -> str:
        """Determine the MIME type based on file extension and content"""
        try:
            # First check file extension
            ext = os.path.splitext(image_path)[1].lower()
            if ext == '.png':
                return 'image/png'
            elif ext in ['.jpg', '.jpeg']:
                return 'image/jpeg'
            
            # Fallback to checking file content
            with open(image_path, 'rb') as f:
                header = f.read(8)
                
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'image/png'
            elif header.startswith(b'\xFF\xD8'):
                return 'image/jpeg'
                
            logger.warning(f"Unrecognized image format for {image_path}, defaulting to jpeg")
            return 'image/jpeg'
        except Exception as e:
            logger.error(f"Error determining MIME type: {str(e)}")
            return 'image/jpeg'

    async def process_image(self, image_path: str, prompt: Optional[str] = None) -> Dict:
        """Process an image using Gemini API."""
        try:
            # Compare with test script behavior
            logger.info("=== Starting image processing ===")
            
            # Encode the image
            base64_image = self.encode_image_to_base64(image_path)
            
            # Get MIME type based on actual content
            mime_type = self._get_mime_type(image_path)
            #mime_type = "image/jpeg"
            logger.info(f"Determined MIME type: {mime_type}")
            
            # Prepare the request
            url = f"{self.api_url}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            if not prompt:
                prompt = "What's in this image? Please describe it in detail."
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": base64_image,
                                }
                            },
                        ]
                    }
                ]
            }
            
            # Log request details (without full base64)
            logger.info(f"Sending request to Gemini API")
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request headers: {headers}")
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error processing image with Gemini: {str(e)}")
            logger.error(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            raise
