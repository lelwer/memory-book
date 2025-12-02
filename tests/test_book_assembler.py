
import pytest
import os
from unittest.mock import patch, MagicMock
from src.book_assembler import create_pdf, PDF, COLOR_MAP, PDF_FONT, PAGE_SIZE_MM
from PIL import Image
import io


class TestColorMap:
	def test_color_map_contains_all_expected_colors(self):
		expected_colors = [
			"light blue", "light pink", "light green",
			"light yellow", "light gray", "white"
		]

		for c in expected_colors:
			assert c in COLOR_MAP


class TestPDFClass:
	def test_pdf_footer_on_story_pages(self):
		pdf = PDF(orientation='P', unit='mm', format=(210, 210))
		pdf._page_count = 5
		pdf.add_page()
		pdf.add_page()

		# Mock the methods that footer calls
		with patch.object(pdf, 'set_y'):
			with patch.object(pdf, 'set_font'):
				with patch.object(pdf, 'set_text_color'):
					with patch.object(pdf, 'cell') as mock_cell:
						pdf.footer()

						# Verify cell was called with page number
						assert mock_cell.called

	def test_pdf_no_footer_on_first_page(self):
		pdf = PDF(orientation='P', unit='mm', format=(210, 210))
		pdf._page_count = 5
		pdf.add_page()

		with patch.object(pdf, 'cell') as mock_cell:
			pdf.footer()

			# Should not render footer on page 1
			assert not mock_cell.called

	def test_pdf_no_footer_on_last_page(self):
		pdf = PDF(orientation='P', unit='mm', format=(210, 210))
		pdf._page_count = 3
		pdf.add_page()
		pdf.add_page()
		pdf.add_page()

		# Simulate being on the last page
		with patch.object(pdf, 'page_no', return_value=3):
			with patch.object(pdf, 'cell') as mock_cell:
				pdf.footer()

				# Should not render footer on last page
				assert not mock_cell.called

	def test_pdf_page_count_property(self):
		pdf = PDF(orientation='P', unit='mm', format=(210, 210))

		# Before setting
		assert pdf.page_count == 0

		# After setting
		pdf._page_count = 5
		assert pdf.page_count == 5


class TestCreatePDFBasicFunctionality:
	@patch('src.book_assembler.os.path.exists')
	def test_successful_pdf_creation(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			with patch('src.book_assembler.Image.open') as mock_image_open:
				mock_exists.return_value = True
				mock_pdf = MagicMock()
				mock_pdf.page_no.return_value = 8
				mock_pdf_class.return_value = mock_pdf

				# Mock PIL Image context manager and size
				mock_img = MagicMock()
				mock_img.size = (800, 600)
				mock_image_open.return_value.__enter__.return_value = mock_img

				result = create_pdf(
					title="Test Story",
					story_text="Page 1\n\nPage 2",
					image_list=["img1.png", "img2.png"],
					end_message="The End",
					cover_image_path="cover.png",
					theme_color="light blue",
					output_filename="test.pdf"
				)

				assert result is True
				mock_pdf.output.assert_called_once_with("test.pdf")

	@patch('src.book_assembler.os.path.exists')
	def test_pdf_creation_with_nonexistent_cover(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 3
			mock_pdf_class.return_value = mock_pdf

			result = create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message="End",
				cover_image_path="nonexistent.png",
				theme_color="light blue",
				output_filename="test.pdf"
			)

			assert result is True

	@patch('src.book_assembler.os.path.exists')
	def test_pdf_creation_with_exception(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_pdf_class.side_effect = Exception("PDF creation failed")

			result = create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message="End",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			assert result is False

	@patch('src.book_assembler.os.path.exists')
	def test_pdf_creation_without_end_message(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 3
			mock_pdf_class.return_value = mock_pdf

			result = create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message="",  # Empty end message
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			assert result is True

	@patch('src.book_assembler.os.path.exists')
	def test_pdf_creation_with_none_end_message(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 3
			mock_pdf_class.return_value = mock_pdf

			result = create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message=None,
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			assert result is True

	@patch('src.book_assembler.os.path.exists')
	def test_valid_theme_color(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=[],
				end_message="",
				cover_image_path=None,
				theme_color="light pink",
				output_filename="test.pdf"
			)

			# Verify set_fill_color was called with light pink RGB
			calls = mock_pdf.set_fill_color.call_args_list
			assert any(call[0] == (255, 204, 229) for call in calls)

	@patch('src.book_assembler.os.path.exists')
	def test_invalid_theme_color_defaults_to_white(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=[],
				end_message="",
				cover_image_path=None,
				theme_color="invalid_color",
				output_filename="test.pdf"
			)

			# Should default to white (255, 255, 255)
			calls = mock_pdf.set_fill_color.call_args_list
			assert any(call[0] == (255, 255, 255) for call in calls)

	@patch('src.book_assembler.os.path.exists')
	def test_case_insensitive_color_matching(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=[],
				end_message="",
				cover_image_path=None,
				theme_color="LIGHT BLUE",  # Uppercase
				output_filename="test.pdf"
			)

			# Should still match light blue
			calls = mock_pdf.set_fill_color.call_args_list
			assert any(call[0] == (204, 229, 255) for call in calls)

	@patch('src.book_assembler.Image.open')
	@patch('src.book_assembler.os.path.exists')
	def test_story_page_with_existing_image(self, mock_exists, mock_image_open):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = True
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			# Mock PIL Image
			mock_img = MagicMock()
			mock_img.size = (800, 600)  # Width x Height
			mock_image_open.return_value.__enter__.return_value = mock_img

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message="",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			# Verify image was added to PDF
			assert mock_pdf.image.called

	@patch('src.book_assembler.os.path.exists')
	def test_story_page_with_missing_image(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["nonexistent.png"],
				end_message="",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			# Should create placeholder rectangle instead
			assert mock_pdf.rect.called

	@patch('src.book_assembler.os.path.exists')
	def test_more_pages_than_images(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 4
			mock_pdf_class.return_value = mock_pdf

			result = create_pdf(
				title="Test",
				story_text="Page 1\n\nPage 2\n\nPage 3",
				image_list=["img1.png"],  # Only one image for 3 pages
				end_message="",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			# Should handle gracefully without crashing
			assert result is True

	@patch('src.book_assembler.Image.open')
	@patch('src.book_assembler.os.path.exists')
	def test_image_aspect_ratio_preservation_landscape(self, mock_exists, mock_image_open):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = True
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			# Mock landscape image (wider than tall)
			mock_img = MagicMock()
			mock_img.size = (1600, 900)  # 16:9 aspect ratio
			mock_image_open.return_value.__enter__.return_value = mock_img

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["landscape.png"],
				end_message="",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			# Verify image was added (aspect ratio preserved internally)
			assert mock_pdf.image.called

	@patch('src.book_assembler.Image.open')
	@patch('src.book_assembler.os.path.exists')
	def test_image_aspect_ratio_preservation_portrait(self, mock_exists, mock_image_open):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = True
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			# Mock portrait image (taller than wide)
			mock_img = MagicMock()
			mock_img.size = (600, 800)  # Portrait aspect ratio
			mock_image_open.return_value.__enter__.return_value = mock_img

			create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["portrait.png"],
				end_message="",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			assert mock_pdf.image.called

	@patch('src.book_assembler.Image.open')
	@patch('src.book_assembler.os.path.exists')
	def test_image_open_exception_handling(self, mock_exists, mock_image_open):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = True
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			# Simulate error opening image
			mock_image_open.side_effect = IOError("Cannot open image")

			result = create_pdf(
				title="Test",
				story_text="Page 1",
				image_list=["corrupt.png"],
				end_message="",
				cover_image_path=None,
				theme_color="white",
				output_filename="test.pdf"
			)

			# Should catch exception and return False
			assert result is False

	@patch('src.book_assembler.os.path.exists')
	def test_title_page_with_cover_image(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = True
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			create_pdf(
				title="My Story",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message="",
				cover_image_path="cover.png",
				theme_color="light blue",
				output_filename="test.pdf"
			)

			# Verify cover image was added
			image_calls = [call for call in mock_pdf.image.call_args_list 
						  if 'cover.png' in str(call)]
			assert len(image_calls) > 0

	@patch('src.book_assembler.os.path.exists')
	def test_title_page_without_cover_image(self, mock_exists):
		with patch('src.book_assembler.PDF') as mock_pdf_class:
			mock_exists.return_value = False
			mock_pdf = MagicMock()
			mock_pdf.page_no.return_value = 2
			mock_pdf_class.return_value = mock_pdf

			create_pdf(
				title="My Story",
				story_text="Page 1",
				image_list=["img1.png"],
				end_message="",
				cover_image_path=None,
				theme_color="light pink",
				output_filename="test.pdf"
			)

			# Should use colored rectangle instead
			assert mock_pdf.rect.called


