#!/usr/bin/env python3
"""
Example: Batch restore all documents in a directory.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_restorer import BatchRestorer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Initialize batch restorer with 4 parallel workers
    batch_restorer = BatchRestorer(num_workers=4)
    
    # Define directories
    input_directory = './documents/'
    output_directory = './restored_documents/'
    
    # File types to process
    file_types = ['pdf', 'jpg', 'jpeg', 'png', 'tiff']
    
    # Restoration techniques
    techniques = ['denoise', 'contrast', 'sharpen']
    
    print(f"\nBatch Restoring Documents")
    print(f"Input Directory: {input_directory}")
    print(f"Output Directory: {output_directory}")
    print(f"File Types: {', '.join(file_types)}")
    print(f"Techniques: {', '.join(techniques)}")
    print(f"Workers: 4")
    print("-" * 50)
    
    # Process all documents
    summary = batch_restorer.restore_directory(
        input_dir=input_directory,
        output_dir=output_directory,
        file_types=file_types,
        techniques=techniques,
        preserve_structure=True
    )
    
    # Print summary
    print(f"\nBatch Processing Summary:")
    print(f"Total Files: {summary['total']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    
    if summary['failed'] > 0:
        print(f"\nFailed Documents:")
        for detail in summary['details']:
            if detail['status'] == 'error':
                print(f"  - {detail['input']}: {detail['error']}")

if __name__ == '__main__':
    main()
