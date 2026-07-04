#!/usr/bin/env python3
"""
Example: Restore a multi-page PDF document.
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
    restorer = DocumentRestorer(dpi=300)  # High DPI for better quality
    
    # Define paths
    input_pdf = 'faded_document.pdf'
    output_pdf = 'restored_document.pdf'
    
    # Define restoration techniques
    techniques = [
        'denoise',      # Remove noise and grain
        'contrast',     # Enhance contrast
        'sharpen'       # Sharpen text (skip binarize for PDFs to keep color info)
    ]
    
    print(f"\nRestoring PDF document: {input_pdf}")
    print(f"Techniques: {', '.join(techniques)}")
    print(f"DPI: 300")
    print("-" * 50)
    
    # Restore the PDF
    result = restorer.restore_pdf(
        input_path=input_pdf,
        output_path=output_pdf,
        techniques=techniques,
        quality=95
    )
    
    # Print result
    print(f"\nRestoration Result:")
    print(f"Status: {result['status']}")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    
    if result['status'] == 'success':
        print(f"Pages Processed: {result['pages_processed']}")
        print(f"Techniques Applied: {', '.join(result['techniques'])}")
        
        # Extract text from restored PDF
        print(f"\nExtracting text from restored PDF...")
        text = restorer.extract_text_from_pdf(output_pdf)
        
        if text:
            print(f"\nExtracted Text (first 500 characters):")
            print("-" * 50)
            print(text[:500])
            if len(text) > 500:
                print("...")
        else:
            print("No text could be extracted.")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == '__main__':
    main()
