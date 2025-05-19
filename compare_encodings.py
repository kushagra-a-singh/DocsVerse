import base64
import hashlib
import os
from backend.app.services.image_processor import ImageProcessor

def compare_encodings(image_path):
    """Compare the test script encoding with backend encoding"""
    print(f"\n=== Comparing encodings for {image_path} ===")
    
    # 1. Get file stats
    file_size = os.path.getsize(image_path)
    with open(image_path, 'rb') as f:
        file_data = f.read()
    file_hash = hashlib.md5(file_data).hexdigest()
    
    print(f"Original file size: {file_size} bytes")
    print(f"Original file MD5: {file_hash}")
    
    # 2. Test script method
    def test_script_method():
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    test_b64 = test_script_method()
    print("\nTest Script Method:")
    print(f"Base64 length: {len(test_b64)} chars")
    print(f"Base64 MD5: {hashlib.md5(test_b64.encode('utf-8')).hexdigest()}")
    print(f"Start: {test_b64[:20]}...")
    print(f"End: ...{test_b64[-20:]}")
    
    # 3. Backend method
    processor = ImageProcessor()
    backend_b64 = processor.encode_image_to_base64(image_path)
    
    print("\nBackend Method:")
    print(f"Base64 length: {len(backend_b64)} chars")
    print(f"Base64 MD5: {hashlib.md5(backend_b64.encode('utf-8')).hexdigest()}")
    print(f"Start: {backend_b64[:20]}...")
    print(f"End: ...{backend_b64[-20:]}")
    
    # 4. Comparison
    print("\nComparison:")
    print(f"Same length: {len(test_b64) == len(backend_b64)}")
    print(f"Same content: {test_b64 == backend_b64}")
    
    if test_b64 != backend_b64:
        print("\nDifferences found!")
        # Find where they start to differ
        for i, (a, b) in enumerate(zip(test_b64, backend_b64)):
            if a != b:
                print(f"First difference at position {i}:")
                print(f"Test: ...{test_b64[i-20:i+20]}...")
                print(f"Backend: ...{backend_b64[i-20:i+20]}...")
                break

if __name__ == "__main__":
    image_path = "D:/Kushagra/Programming/DocsVerse/backend/data/processed/d57f3ef2-3138-4b4d-98a6-a4c70f2ce212.png"
    compare_encodings(image_path)