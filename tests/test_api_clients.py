import pytest
from unittest.mock import patch, MagicMock
from src.api_clients import get_story_from_gemini, get_cover_image, get_images_from_api

# ==========================================
# 1. Tests for get_story_from_gemini
# ==========================================

@patch('src.api_clients.genai.GenerativeModel')
def test_get_story_from_gemini_success(mock_model_class):
    """Test that valid text is returned when API call succeeds."""
    # Setup the mock
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Once upon a time..."
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model

    # Run function with a fake API key set
    with patch('src.api_clients.GEMINI_API_KEY', 'fake_key'):
        result = get_story_from_gemini("Tell me a story")
    
    assert result == "Once upon a time..."

def test_get_story_from_gemini_raises_error_when_no_api_key():
    """If GEMINI_API_KEY is missing, function should raise ValueError."""
    with patch('src.api_clients.GEMINI_API_KEY', None):
        with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
            get_story_from_gemini("Any prompt")

@patch('src.api_clients.genai.GenerativeModel')
def test_get_story_from_gemini_reraises_exception(mock_model_class):
    """If the API fails, the function should re-raise the exception."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Connection Failed")
    mock_model_class.return_value = mock_model

    with patch('src.api_clients.GEMINI_API_KEY', 'fake_key'):
        with pytest.raises(Exception, match="API Connection Failed"):
            get_story_from_gemini("prompt")

# ==========================================
# 2. Tests for get_cover_image
# ==========================================

@patch('src.api_clients.genai.GenerativeModel')
def test_get_cover_image_success(mock_model_class):
    """Test that it saves a file and returns path on success."""
    # Mock the API response structure
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    mock_part = MagicMock()
    mock_part.inline_data.mime_type = "image/png"
    mock_part.inline_data.data = b"fake_image_bytes"
    
    mock_response.parts = [mock_part]
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model

    # Mock 'open' so we don't actually write to disk
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        with patch('src.api_clients.GEMINI_API_KEY', 'fake_key'):
            result = get_cover_image("theme")
            
    assert result == "cover_pattern.png"

def test_get_cover_image_returns_none_no_key():
    """Should return None and print error if key is missing."""
    with patch('src.api_clients.GEMINI_API_KEY', None):
        result = get_cover_image("theme")
    assert result is None

# ==========================================
# 3. Tests for get_images_from_api
# ==========================================

@patch('src.api_clients.genai.GenerativeModel')
def test_get_images_from_api_success(mock_model_class):
    """Test generating images for story pages."""
    # Mock chat session
    mock_chat = MagicMock()
    mock_model = MagicMock()
    mock_model.start_chat.return_value = mock_chat
    mock_model_class.return_value = mock_model
    
    # Mock response for one image
    mock_response = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data.mime_type = "image/jpeg"
    mock_part.inline_data.data = b"fake_bytes"
    mock_response.parts = [mock_part]
    
    mock_chat.send_message.return_value = mock_response

    story_text = "Page 1 text.\n\nPage 2 text."
    
    with patch("builtins.open", new_callable=MagicMock):
        with patch('src.api_clients.GEMINI_API_KEY', 'fake_key'):
            results = get_images_from_api(story_text, "desc", "chars", "details")
            
    # Should get 2 images (one for each page)
    assert len(results) == 2
    assert "temp_image_0.jpeg" in results
    assert "temp_image_1.jpeg" in results

def test_get_images_returns_empty_no_key():
    with patch('src.api_clients.GEMINI_API_KEY', None):
        result = get_images_from_api("text", "desc", "chars", "details")
    assert result == []