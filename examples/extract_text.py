#!/usr/bin/env python3
"""
Example: Extract text from restored documents using OCR.
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
    
    print(f"\nDocument Text Extraction Example")
    print("-" * 50)
    
    # Example 1: Extract text from an image
    print(f"\n1. Extracting text from restored image...")
    image_path = 'restored_document.png'
    
    text = restorer.extract_text(image_path, language='eng')
    print(f"\nExtracted Text:")
    print(text[:1000])  # Print first 1000 characters
    
    # Example 2: Extract text from a PDF
    print(f"\n2. Extracting text from restored PDF...")
    pdf_path = 'restored_document.pdf'
    
    pdf_text = restorer.extract_text_from_pdf(pdf_path, language='eng')
    print(f"\nExtracted Text:")
    print(pdf_text[:1000])  # Print first 1000 characters
    
    # Save extracted text
    with open('extracted_text.txt', 'w') as f:
        f.write(pdf_text)
    
    print(f"\nExtracted text saved to: extracted_text.txt")

if __name__ == '__main__':
    main()
