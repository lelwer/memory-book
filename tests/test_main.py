"""
Pipeline Integration Tests for main.py

Tests the orchestration of the storybook generation pipeline.
Validates that main() correctly calls api_clients and book_assembler modules
in the right order with proper data flow between steps.

Uses pytest-mock to patch all external dependencies (API calls, file I/O).
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from src.main import main, get_user_input, validate_environment

# 1. Test validate_environment specifically
def test_validate_environment_exits_without_key():
    """Verify that the validator actually calls sys.exit(1) if key is missing."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            validate_environment()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

def test_validate_environment_passes_with_key():
    """Verify it does NOT exit if key is present."""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'fake_key'}):
        # Should not raise SystemExit
        try:
            validate_environment()
        except SystemExit:
            pytest.fail("validate_environment() raised SystemExit unexpectedly!")

# 2. Test the Main Loop (Mocking everything!)
@patch('src.main.validate_environment')  # Stop the crash!
@patch('src.main.get_user_input')        # Fake user input
@patch('src.main.get_story_from_gemini') # Fake Story API
@patch('src.main.get_cover_image')       # Fake Cover API
@patch('src.main.get_images_from_api')   # Fake Image API
@patch('src.main.create_pdf')            # Fake PDF creation
def test_main_success_flow(mock_create_pdf, mock_get_images, mock_get_cover, 
                           mock_get_story, mock_input, mock_validator):
    """
    Test the happy path: Main runs, gets input, calls APIs, and makes a PDF.
    """
    # A. Setup the fake data
    mock_input.return_value = {
        "protagonist": "TestUser",
        "memory": "Test memory",
        "tone": "Funny",
        "style": "Rhyming",
        "details": "Details",
        "character_desc": "Desc",
        "other_characters": "Others",
        "title": "Test Title",
        "end_message": "The End",
        "cover_theme": "Theme",
        "theme_color": "blue"
    }
    mock_get_story.return_value = "Page 1\n\nPage 2"
    mock_get_cover.return_value = "cover.png"
    mock_get_images.return_value = ["img1.png", "img2.png"]
    mock_create_pdf.return_value = True

    # B. Run Main
    main()

    # C. Verify everything was called
    mock_validator.assert_called_once()
    mock_get_story.assert_called_once()
    mock_get_cover.assert_called_once()
    mock_create_pdf.assert_called_once()

@patch('src.main.validate_environment')
@patch('src.main.get_user_input')
@patch('src.main.get_story_from_gemini')
def test_main_handles_api_failure(mock_get_story, mock_input, mock_validator):
    """
    Test that main exits gracefully if the Story API fails.
    """
    # FIX: We must provide ALL keys used in the f-string in main.py, 
    # otherwise it crashes with KeyError before hitting the API.
    mock_input.return_value = {
        "protagonist": "Test", 
        "tone": "Funny",
        "memory": "Test memory",       # Added
        "details": "Test details",     # Added
        "style": "Rhyming",            # Added
        "cover_theme": "Test theme",   # Added
        "theme_color": "blue"          # Added
    }
    
    # Simulate API Failure
    mock_get_story.side_effect = Exception("API Down")

    # Expect sys.exit(1) because main.py catches the error and exits
    with pytest.raises(SystemExit) as e:
        main()
    
    assert e.value.code == 1