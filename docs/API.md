# Document Restoration Tool - API Reference

## Overview

The Document Restoration Tool provides a comprehensive API for restoring faded and degraded documents with support for both image files and PDF documents.

## Main Classes

### DocumentRestorer

Main interface for single document restoration.

#### Initialization

```python
from document_restorer import DocumentRestorer

restorer = DocumentRestorer(
    config=None,  # Optional configuration dict
    dpi=300       # DPI for PDF processing
)
```

#### Methods

##### restore(input_path, output_path, techniques=None, quality=95)

Restore a single image document.

**Parameters:**
- `input_path` (str): Path to input image
- `output_path` (str): Path to save restored image
- `techniques` (List[str]): Restoration techniques to apply. Options:
  - `'denoise'` - Remove noise and grain
  - `'contrast'` - Enhance contrast
  - `'sharpen'` - Sharpen text
  - `'binarize'` - Convert to black and white
- `quality` (int): Output quality (0-100)

**Returns:** Dictionary with restoration status and details

**Example:**
```python
result = restorer.restore(
    input_path='faded_document.jpg',
    output_path='restored_document.png',
    techniques=['denoise', 'contrast', 'sharpen', 'binarize'],
    quality=95
)
```

##### restore_pdf(input_path, output_path, techniques=None, quality=95)

Restore a multi-page PDF document.

**Parameters:**
- `input_path` (str): Path to input PDF
- `output_path` (str): Path to save restored PDF
- `techniques` (List[str]): Restoration techniques
- `quality` (int): Output quality (0-100)

**Returns:** Dictionary with PDF restoration status

**Example:**
```python
result = restorer.restore_pdf(
    input_path='faded_document.pdf',
    output_path='restored_document.pdf',
    techniques=['denoise', 'contrast', 'sharpen']
)
```

##### extract_text(image_path, language='eng')

Extract text from a restored image using OCR.

**Parameters:**
- `image_path` (str): Path to image file
- `language` (str): OCR language code (default: 'eng')

**Returns:** Extracted text as string

**Example:**
```python
text = restorer.extract_text(
    image_path='restored_document.png',
    language='eng'
)
print(text)
```

##### extract_text_from_pdf(pdf_path, language='eng')

Extract text from all pages of a restored PDF.

**Parameters:**
- `pdf_path` (str): Path to PDF file
- `language` (str): OCR language code

**Returns:** Extracted text from all pages

**Example:**
```python
text = restorer.extract_text_from_pdf(
    pdf_path='restored_document.pdf',
    language='eng'
)
```

### BatchRestorer

Batch process multiple documents in parallel.

#### Initialization

```python
from document_restorer import BatchRestorer

batch_restorer = BatchRestorer(
    num_workers=4,  # Number of parallel workers
    config=None     # Optional configuration dict
)
```

#### Methods

##### restore_directory(input_dir, output_dir, file_types=None, techniques=None, preserve_structure=True)

Restore all documents in a directory.

**Parameters:**
- `input_dir` (str): Input directory path
- `output_dir` (str): Output directory path
- `file_types` (List[str]): File types to process (default: ['pdf', 'jpg', 'jpeg', 'png', 'tiff'])
- `techniques` (List[str]): Restoration techniques
- `preserve_structure` (bool): Keep directory structure in output

**Returns:** Summary dictionary with total, successful, and failed counts

**Example:**
```python
summary = batch_restorer.restore_directory(
    input_dir='./documents/',
    output_dir='./restored_documents/',
    file_types=['pdf', 'jpg', 'png'],
    techniques=['denoise', 'contrast', 'sharpen'],
    preserve_structure=True
)

print(f"Success: {summary['successful']}/{summary['total']}")
```

### ImageRestorer

Low-level image processing engine.

#### Methods

##### load_image(image_path)

Load image from file.

**Returns:** Image as numpy array

##### save_image(image, output_path, quality=95)

Save image to file.

##### denoise(image, strength=None)

Apply bilateral denoising to image.

**Returns:** Denoised image

##### enhance_contrast(image, method='clahe')

Enhance image contrast.

**Methods:** 'clahe', 'histogram', 'levels'

**Returns:** Contrast-enhanced image

##### sharpen(image, method='unsharp')

Sharpen image.

**Methods:** 'unsharp', 'laplacian'

**Returns:** Sharpened image

##### binarize(image, method='adaptive')

Convert image to binary (black and white).

**Methods:** 'adaptive', 'otsu', 'niblack'

**Returns:** Binary image

##### restore(image, techniques)

Apply sequence of restoration techniques.

**Parameters:**
- `image` (numpy.ndarray): Input image
- `techniques` (List[str]): Techniques to apply in order

**Returns:** Restored image

### PDFHandler

PDF document handling utilities.

#### Methods

##### pdf_to_images(pdf_path)

Convert PDF pages to images.

**Returns:** List of images as numpy arrays

##### images_to_pdf(images, output_path, quality=95)

Convert images to PDF.

##### get_pdf_info(pdf_path)

Get PDF metadata and information.

**Returns:** Dictionary with PDF info

##### extract_text_from_pdf(pdf_path)

Extract text from PDF (if available in document).

**Returns:** Extracted text

## Restoration Techniques

### Denoising

Removes noise and grain from faded documents using bilateral filtering, which preserves edges while smoothing noise.

**Best for:**
- Scanned documents with grain
- Faded photocopies
- Low-quality camera photos

### Contrast Enhancement

Improves text visibility through histogram equalization or adaptive methods (CLAHE).

**Best for:**
- Very faded documents
- Low contrast images
- Documents with uneven lighting

### Sharpening

Enhances text clarity through unsharp masking or Laplacian sharpening.

**Best for:**
- Blurry scans
- Low-resolution documents
- After contrast enhancement

### Binarization

Converts grayscale to black and white, improving text clarity for OCR.

**Best for:**
- Text-heavy documents
- Before OCR extraction
- Improving file size

## Output Formats

- **PNG**: Lossless, best for archival
- **JPEG**: Lossy, smaller file size
- **TIFF**: High-resolution, suitable for printing
- **PDF**: Multi-page documents

## Return Values

### restore() / restore_pdf() Return Value

```python
{
    'status': 'success',  # or 'error'
    'input': 'path/to/input',
    'output': 'path/to/output',
    'techniques': ['denoise', 'contrast', ...],
    'pages_processed': 5,  # PDF only
    'error': 'error message'  # If status is 'error'
}
```

### restore_directory() Return Value

```python
{
    'total': 50,
    'successful': 48,
    'failed': 2,
    'details': [
        {'status': 'success', 'input': '...', 'output': '...'},
        {'status': 'error', 'input': '...', 'error': '...'},
        ...
    ]
}
```

## Error Handling

All methods include error handling and logging. Check the return status and error message:

```python
result = restorer.restore('input.jpg', 'output.png')

if result['status'] == 'error':
    print(f"Error: {result['error']}")
else:
    print(f"Restoration successful: {result['output']}")
```
