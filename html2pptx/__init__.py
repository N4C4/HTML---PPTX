# -*- coding: utf-8 -*-
"""html2pptx: convierte wireframes HTML (o imágenes PNG/JPG) en PPTX editable."""
from .convert import convert, BrowserNotFound, DumpError, UnsupportedFile

__version__ = "0.1.0"
__all__ = ["convert", "BrowserNotFound", "DumpError", "UnsupportedFile", "__version__"]
