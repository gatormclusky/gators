#!/usr/bin/env python3
"""
Example: Restore a single faded image document.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_restorer import DocumentRestorer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Initialize restorer
    restorer = DocumentRestorer()
    
    # Define paths
    input_image = 'sample_faded_document.jpg'
    output_image = 'restored_document.png'
    
    # Define restoration techniques in order
    techniques = [
        'denoise',      # Remove noise
        'contrast',     # Enhance contrast
        'sharpen',      # Sharpen text
        'binarize'      # Convert to black and white
    ]
    
    print(f"\nRestoring document: {input_image}")
    print(f"Techniques: {', '.join(techniques)}")
    print("-" * 50)
    
    # Restore the image
    result = restorer.restore(
        input_path=input_image,
        output_path=output_image,
        techniques=techniques,
        quality=95
    )
    
    # Print result
    print(f"\nRestoration Result:")
    print(f"Status: {result['status']}")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print(f"Techniques Applied: {', '.join(result['techniques'])}")
    
    if result['status'] == 'success':
        # Extract text from restored document
        print(f"\nExtracting text from restored image...")
        text = restorer.extract_text(output_image)
        
        if text:
            print(f"\nExtracted Text:")
            print("-" * 50)
            print(text[:500])  # Print first 500 characters
            if len(text) > 500:
                print("...")
        else:
            print("No text could be extracted.")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == '__main__':
    main()
