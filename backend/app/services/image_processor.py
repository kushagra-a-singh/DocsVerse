import base64
import hashlib
import io
import logging
import os
import re  # Import re for parsing
from typing import (  # Import List and Any for type hints
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

import requests
from PIL import Image, UnidentifiedImageError

from ..config import settings
from ..models.query import Citation 

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

            file_size = os.path.getsize(image_path)
            logger.info(f"[ImageProcessor] Original file size: {file_size} bytes")

            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            file_hash = hashlib.md5(image_data).hexdigest()
            logger.info(f"[ImageProcessor] Original file MD5 hash: {file_hash}")

            base64_data = base64.b64encode(image_data).decode("utf-8")

            base64_length = len(base64_data)
            base64_hash = hashlib.md5(base64_data.encode("utf-8")).hexdigest()

            logger.info(
                f"[ImageProcessor] Base64 string length: {base64_length} characters"
            )
            logger.info(f"[ImageProcessor] Base64 MD5 hash: {base64_hash}")
            logger.debug(f"Base64 start: {base64_data[:20]}...")
            logger.debug(f"Base64 end: ...{base64_data[-20:]}\n")

            return base64_data 
        except Exception as e:
            logger.error(
                f"[ImageProcessor] Error encoding image: {str(e)}", exc_info=True
            )
            raise

    def validate_base64_image(self, base64_str: str) -> bool:
        """Validate that a base64 string can be decoded to a valid image"""
        try:
            decoded = base64.b64decode(base64_str)

            if len(decoded) < 8:
                return False

            magic_numbers = {
                b"\xff\xd8\xff": "JPEG",
                b"\x89PNG\r\n\x1a\n": "PNG",
                b"GIF87a": "GIF",
                b"GIF89a": "GIF",
                b"BM": "BMP",
                b"II*\x00": "TIFF",
                b"MM\x00*": "TIFF",
            }

            matches = [
                fmt for magic, fmt in magic_numbers.items() if decoded.startswith(magic)
            ]

            if not matches:
                logger.warning("Decoded data doesn't match known image formats")
                return False

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
            ext = os.path.splitext(image_path)[1].lower()
            if ext == ".png":
                return "image/png"
            elif ext in [".jpg", ".jpeg"]:
                return "image/jpeg"

            with open(image_path, "rb") as f:
                header = f.read(8)

            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                return "image/png"
            elif header.startswith(b"\xff\xd8"):
                return "image/jpeg"

            logger.warning(
                f"Unrecognized image format for {image_path}, defaulting to jpeg"
            )
            return "image/jpeg"
        except Exception as e:
            logger.error(f"Error determining MIME type: {str(e)}")
            return "image/jpeg"

    async def process_image(
        self, image_path: str, query: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Process an image using Gemini API and return structured answer and citations."""
        try:
            logger.info("=== Starting image processing ===")

            base64_image = self.encode_image_to_base64(image_path)

            mime_type = self._get_mime_type(image_path)
            logger.info(f"Determined MIME type: {mime_type}")

            url = f"{self.api_url}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}

            image_prompt = f"""
Human:
        You are an AI assistant that analyzes images and provides accurate information based on their content.

        Analyze the image and answer the following query: {query}

        Provide a comprehensive answer based ONLY on the information in the image.
        If the answer cannot be determined from the image, say "I don't have enough information to answer this question based on the image content."

        Format your response in the following structure:

        # Answer
        [Your detailed answer here with proper markdown formatting]

        # Citations
        For key pieces of information in your answer that can be directly attributed to the image, provide a citation in this format:
        - [Image Title or Identifier]: "[relevant description or quote from the image content]"

        Guidelines:
        1. Use proper markdown formatting:
           - Use **bold** for emphasis
           - Use bullet points for lists
           - Use proper headings with # for sections
           - Use code blocks with ``` for any code or technical content
           - Use blockquotes with > for important quotes

        2. Citation Rules:
           - Each major point in your answer should ideally have a citation if it directly comes from the image.
           - Include a relevant description or quote from the image content in the citation.
           - Format citations as a bulleted list.
           - If you know the document name or identifier, use it in the citation.

        Example format:
        # Answer
        [Your detailed answer with proper markdown formatting]

        # Citations
        - [Image: Chart 1]: "[description of a key data point from the chart]"
        - [Image: Diagram A]: "[explanation of a component from the diagram]"

Assistant:
"""
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": image_prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": base64_image,
                                }
                            },
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": settings.llm.temperature,
                    "maxOutputTokens": 1000,
                },
            }

            logger.info("Sending request to Gemini API")
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request headers: {headers}")

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            response_json = response.json()
            logger.info("Received response from Gemini API")
            logger.debug(f"Raw Gemini response: {response_json}")

            generated_text = ""
            if (
                response_json
                and response_json.get("candidates")
                and response_json["candidates"][0].get("content")
                and response_json["candidates"][0]["content"].get("parts")
            ):
                generated_text = "".join(
                    [
                        part.get("text", "")
                        for part in response_json["candidates"][0]["content"]["parts"]
                    ]
                ).strip()
                logger.debug(
                    f"Extracted text from Gemini response: {generated_text[:200]}..."
                )
            else:
                logger.warning("Gemini response did not contain expected text.")
                return "Error: Could not extract text from image analysis.", []

            synthesized_answer, synthesized_citations_dict = (
                self._parse_structured_response(generated_text, image_path)
            )

            return synthesized_answer, synthesized_citations_dict

        except Exception as e:
            logger.error(f"Error processing image with Gemini: {str(e)}", exc_info=True)
            raise

    def _parse_structured_response(
        self, response_text: str, image_path: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Parses the structured markdown response from the LLM."""
        answer = ""
        citations = []
        answer_section = ""
        citations_section = ""

        parts = response_text.split("# Answer")
        if len(parts) > 1:
            answer_section = parts[1].strip()
            citations_parts = answer_section.split("# Citations")
            answer = citations_parts[0].strip()
            if len(citations_parts) > 1:
                citations_section = citations_parts[1].strip()
        else:
            answer = response_text.strip()

        if citations_section:
            citation_lines = citations_section.split("\\n")
            image_identifier = os.path.basename(
                image_path
            )  

            for line in citation_lines:
                line = line.strip()
                if not line or not line.startswith("-"):
                    continue

                match = re.match(r'-\s*\[(.*?)\]:\s*"(.*)"', line)
                if match:
                    doc_name_match = match.group(1).strip()
                    quote = match.group(2).strip()

                    citation_doc_name = (
                        doc_name_match if doc_name_match else image_identifier
                    )

                    citations.append(
                        {
                            "document_id": image_identifier,  
                            "document_name": citation_doc_name,
                            "text": quote,
                            "page": None, 
                            "chunk": None, 
                        }
                    )
                elif (
                    citations
                    and "text" in citations[-1]
                    and not citations[-1]["text"].endswith('"')
                ):
                    citations[-1]["text"] += "\\n" + line

        return answer, citations
