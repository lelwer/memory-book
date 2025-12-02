import pytest
import os
from unittest.mock import patch, MagicMock, mock_open

from src.api_clients import get_story_from_gemini, get_cover_image, get_images_from_api


@patch('src.api_clients.genai.GenerativeModel')
def test_get_story_from_gemini_returns_placeholder_when_no_api_key(mock_model_class):
	"""If GEMINI_API_KEY is not set, function should return a placeholder string."""
	with patch('src.api_clients.GEMINI_API_KEY', None):
		result = get_story_from_gemini("Any prompt")

	assert isinstance(result, str)
	assert "placeholder" in result.lower() or "gemini_api_key" in result.lower()


@patch('src.api_clients.genai.GenerativeModel')
def test_get_story_from_gemini_cleans_special_characters(mock_model_class):
	"""Ensure special punctuation from the API response is normalized."""
	mock_model = MagicMock()
	# Response contains typographic quotes, ellipsis and long dash
	mock_response = MagicMock()
	mock_response.text = 'Hello… it’s a “test” — end'
	mock_model.generate_content.return_value = mock_response
	mock_model_class.return_value = mock_model

	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		out = get_story_from_gemini('prompt')

	assert "..." in out
	assert "it's" in out or "it'" in out
	assert '"test"' in out
	assert "--" in out


@patch('src.api_clients.genai.GenerativeModel')
def test_get_story_from_gemini_handles_api_exception(mock_model_class):
	"""If the model raises an exception, return a fallback placeholder."""
	mock_model = MagicMock()
	mock_model.generate_content.side_effect = Exception("boom")
	mock_model_class.return_value = mock_model

	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		out = get_story_from_gemini('prompt')

	assert isinstance(out, str)
	assert "placeholder" in out.lower()


@patch('src.api_clients.genai.GenerativeModel')
@patch('builtins.open', new_callable=mock_open)
def test_get_cover_image_saves_file_for_png(mock_open_fn, mock_model_class):
	"""Cover generation should write a file and return its filename."""
	mock_model = MagicMock()
	mock_part = MagicMock()
	mock_part.inline_data = MagicMock()
	mock_part.inline_data.mime_type = "image/png"
	mock_part.inline_data.data = b"fakepng"

	mock_response = MagicMock()
	mock_response.parts = [mock_part]

	mock_model.generate_content.return_value = mock_response
	mock_model_class.return_value = mock_model

	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_cover_image('flowers')

	assert result == 'cover_pattern.png'
	mock_open_fn.assert_called_once_with('cover_pattern.png', 'wb')
	mock_open_fn().write.assert_called_once_with(b"fakepng")


@patch('src.api_clients.genai.GenerativeModel')
@patch('builtins.open', new_callable=mock_open)
def test_get_cover_image_handles_different_mime_types(mock_open_fn, mock_model_class):
	"""Cover generation should use correct file extension for jpeg."""
	mock_model = MagicMock()
	mock_part = MagicMock()
	mock_part.inline_data = MagicMock()
	mock_part.inline_data.mime_type = "image/jpeg"
	mock_part.inline_data.data = b"fakejpeg"

	mock_response = MagicMock()
	mock_response.parts = [mock_part]
	mock_model.generate_content.return_value = mock_response
	mock_model_class.return_value = mock_model

	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_cover_image('flowers')

	assert result == 'cover_pattern.jpeg'


@patch('src.api_clients.genai.GenerativeModel')
def test_get_cover_image_returns_none_when_no_parts(mock_model_class):
	mock_model = MagicMock()
	mock_response = MagicMock()
	mock_response.parts = []
	mock_model.generate_content.return_value = mock_response
	mock_model_class.return_value = mock_model

	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_cover_image('flowers')

	assert result is None


@patch('src.api_clients.genai.GenerativeModel')
@patch('builtins.open', side_effect=IOError("no write"))
def test_get_cover_image_handles_file_write_error(mock_open_fn, mock_model_class):
	mock_model = MagicMock()
	mock_part = MagicMock()
	mock_part.inline_data = MagicMock()
	mock_part.inline_data.mime_type = "image/png"
	mock_part.inline_data.data = b"fakepng"
	mock_response = MagicMock()
	mock_response.parts = [mock_part]
	mock_model.generate_content.return_value = mock_response
	mock_model_class.return_value = mock_model

	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_cover_image('flowers')

	assert result is None


@patch('src.api_clients.genai.GenerativeModel')
def test_get_cover_image_returns_none_without_api_key(mock_model_class):
	with patch('src.api_clients.GEMINI_API_KEY', None):
		result = get_cover_image('theme')

	assert result is None


@patch('src.api_clients.genai.GenerativeModel')
@patch('builtins.open', new_callable=mock_open)
def test_get_images_from_api_generates_files_for_each_page(mock_open_fn, mock_model_class):
	"""Verify images are generated and saved for each story page."""
	# Prepare chat and responses
	mock_model = MagicMock()
	mock_chat = MagicMock()

	def make_response(ext=b'pngdata', mime='image/png'):
		resp = MagicMock()
		part = MagicMock()
		part.inline_data = MagicMock()
		part.inline_data.mime_type = mime
		part.inline_data.data = ext
		resp.parts = [part]
		return resp

	# Two pages -> two responses
	mock_chat.send_message.side_effect = [make_response(b'one', 'image/png'), make_response(b'two', 'image/png')]
	mock_model.start_chat.return_value = mock_chat
	mock_model_class.return_value = mock_model

	story_text = "Page 1\n\nPage 2"
	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_images_from_api(story_text, "char desc", "others", "details")

	assert len(result) == 2
	assert result[0].endswith('temp_image_0.png')
	assert result[1].endswith('temp_image_1.png')
	assert mock_chat.send_message.call_count == 2


@patch('src.api_clients.genai.GenerativeModel')
@patch('builtins.open', new_callable=mock_open)
def test_get_images_from_api_handles_no_image_parts(mock_open_fn, mock_model_class):
	mock_model = MagicMock()
	mock_chat = MagicMock()
	mock_resp = MagicMock()
	mock_resp.parts = []
	mock_chat.send_message.return_value = mock_resp
	mock_model.start_chat.return_value = mock_chat
	mock_model_class.return_value = mock_model

	story_text = "Page without image"
	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_images_from_api(story_text, "char", "other", "details")

	assert result == []


@patch('src.api_clients.genai.GenerativeModel')
@patch('builtins.open', side_effect=IOError("no write"))
def test_get_images_from_api_file_write_error_returns_partial_or_empty(mock_open_fn, mock_model_class):
	mock_model = MagicMock()
	mock_chat = MagicMock()

	mock_resp = MagicMock()
	part = MagicMock()
	part.inline_data = MagicMock()
	part.inline_data.mime_type = 'image/png'
	part.inline_data.data = b'data'
	mock_resp.parts = [part]

	mock_chat.send_message.return_value = mock_resp
	mock_model.start_chat.return_value = mock_chat
	mock_model_class.return_value = mock_model

	story_text = "Page 1"
	with patch('src.api_clients.GEMINI_API_KEY', 'test_api_key'):
		result = get_images_from_api(story_text, "char", "other", "details")

	# If writing fails, function should not crash and should return whatever was collected (likely empty)
	assert isinstance(result, list)



