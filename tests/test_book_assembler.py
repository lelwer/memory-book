import pytest
import os
from unittest.mock import patch, MagicMock, mock_open, Mock
from book_assembler import create_pdf, PDF, COLOR_MAP, PDF_FONT, PAGE_SIZE_MM
from PIL import Image
import io


