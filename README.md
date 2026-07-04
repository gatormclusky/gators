# Document Restoration Tool

A comprehensive Python-based tool for restoring faded, degraded, and damaged documents with high accuracy for text extraction and archival purposes. **Full PDF support included.**

## Features

- **PDF & Image Support**: Process PDF documents and image files (JPG, PNG, TIFF, BMP)
- **Image Enhancement**: Multiple algorithms to improve faded document contrast and clarity
- **Noise Reduction**: Advanced denoising techniques (bilateral filtering, morphological operations)
- **Binarization**: Adaptive thresholding for text clarity
- **OCR Integration**: Extract text from restored documents using Tesseract
- **Batch Processing**: Process multiple documents automatically
- **Quality Metrics**: Assess restoration quality before/after
- **Output Formats**: Save restored documents in PDF, PNG, high-res TIFF
- **PDF Reconstruction**: Reassemble multi-page PDFs with all pages restored

## Installation

```bash
# Clone the repository
git clone https://github.com/gatormclusky/gators.git
cd gators

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (system dependency)
# On Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# On macOS:
brew install tesseract

# On Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Quick Start

### Restore a Single Document

```python
from document_restorer import DocumentRestorer

# Initialize restorer
restorer = DocumentRestorer()

# Restore an image
result = restorer.restore(
    input_path='faded_document.jpg',
    output_path='restored_document.png',
    techniques=['denoise', 'contrast', 'sharpen', 'binarize']
)

# Restore a PDF
pdf_result = restorer.restore_pdf(
    input_path='faded_document.pdf',
    output_path='restored_document.pdf'
)
```

### Extract Text from Restored Document

```python
# From restored image
text = restorer.extract_text('restored_document.png')
print(text)

# From restored PDF
pdf_text = restorer.extract_text_from_pdf('restored_document.pdf')
print(pdf_text)
```

### Batch Processing

```python
from document_restorer import BatchRestorer

batch = BatchRestorer(num_workers=4)

# Process all PDFs in a directory
batch.restore_directory(
    input_dir='./documents/',
    output_dir='./restored_documents/',
    file_types=['pdf', 'jpg', 'png'],
    preserve_structure=True
)
```

## Restoration Techniques

### 1. **Contrast Enhancement**
- Histogram equalization
- CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Levels adjustment
- Auto-brightness correction

### 2. **Noise Reduction**
- Bilateral filtering (edge-preserving)
- Non-local means denoising
- Morphological operations
- Despeckle algorithms

### 3. **Sharpening**
- Unsharp masking
- High-pass sharpening
- Deconvolution

### 4. **Binarization**
- Otsu's method
- Adaptive thresholding
- Niblack thresholding
- Sauvola thresholding

### 5. **Color Correction**
- Auto white balance
- Gamma correction
- Channel equalization
- Yellowing removal

### 6. **PDF-Specific Processing**
- Multi-page PDF handling
- Page-by-page restoration
- DPI optimization
- Text layer preservation

## Supported Document Types

- Black & white text documents
- Aged/yellowed documents
- Water-damaged documents
- Carbon copies
- Microfilm scans
- Faded photocopies
- Multi-page PDFs
- Redacted documents (with optional text recovery)
- Government/declassified documents

## Configuration

Edit `config.yaml` to customize:

```yaml
restoration:
  techniques:
    - denoise
    - contrast
    - sharpen
    - binarize
  
  parameters:
    denoise_strength: 10
    contrast_limit: 2.0
    sharpening_kernel: unsharp
    
ocr:
  engine: tesseract
  languages:
    - eng
  confidence_threshold: 0.6

pdf:
  dpi: 300
  quality: 95
  preserve_original: true

output:
  format: png
  compression: true
  quality: 95
```

## API Reference

See `docs/API.md` for complete documentation.

## Performance

- Single page image: ~2-5 seconds
- Single page PDF: ~3-7 seconds
- Batch processing: Parallel processing with configurable workers
- Memory efficient: Processes large PDFs without full loading

## Output Quality

The tool provides restoration with:
- Improved text legibility (suitable for OCR)
- Preserved document details and signatures
- Minimal artificial artifacts
- High-resolution output options (up to 600 DPI)
- Accurate color/grayscale preservation

## Examples

See `examples/` directory for detailed use cases:
- `restore_single_image.py` — Restore a single photo/scan
- `restore_single_pdf.py` — Restore a multi-page PDF
- `batch_restore.py` — Process directories of documents
- `extract_text.py` — OCR and text extraction
- `quality_assessment.py` — Compare before/after quality
- `declassified_documents.py` — Handle government documents with redactions

## License

MIT

## Contributing

Pull requests welcome! Please see CONTRIBUTING.md

## Support

For issues and questions, please open an issue on GitHub.
