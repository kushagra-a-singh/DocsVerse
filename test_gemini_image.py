import base64
import io
import hashlib
import requests
from PIL import Image


def encode_image_to_base64(image_path):
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        # Read the image file
        image_data = image_file.read()
        # Convert to base64
        base64_data = base64.b64encode(image_data).decode("utf-8")
        return base64_data


def send_image_to_gemini(image_path, api_key):
    """Send an image to Gemini API."""
    # Encode the image
    base64_image = encode_image_to_base64(image_path)

    print(f"\nTest Script Verification:")
    print(f"Base64 length: {len(base64_image)} chars")
    print(f"Base64 MD5: {hashlib.md5(base64_image.encode('utf-8')).hexdigest()}")
    print(f"First 20 chars: {base64_image[:20]}")
    print(f"Last 20 chars: {base64_image[-20:]}")
    # API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # Headers
    headers = {"Content-Type": "application/json"}

    # Request body
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "What's in this image?"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}},
                ]
            }
        ]
    }

    # Make the request
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "AIzaSyCQyM9hfqmLXgnjhxS8PzfrAzk0RjZR4H4"

    # Replace with your image path
    IMAGE_PATH = "D:/Kushagra/Programming/DocsVerse/backend/data/processed/d57f3ef2-3138-4b4d-98a6-a4c70f2ce212.png"

    try:
        result = send_image_to_gemini(IMAGE_PATH, API_KEY)
        print("Response:", result)
    except Exception as e:
        print("Error:", str(e))
