"""
Document Restoration Tool

A comprehensive Python package for restoring faded, degraded, and damaged documents
with support for both images and PDF files.
"""

from .core import ImageRestorer
from .pdf_handler import PDFHandler
from .restorer import DocumentRestorer, BatchRestorer

__version__ = '1.0.0'
__author__ = 'Document Restoration Team'

__all__ = [
    'ImageRestorer',
    'PDFHandler',
    'DocumentRestorer',
    'BatchRestorer',
]
