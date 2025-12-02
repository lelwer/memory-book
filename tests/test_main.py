"""
Pipeline Integration Tests for main.py

Tests the orchestration of the storybook generation pipeline.
Validates that main() correctly calls api_clients and book_assembler modules
in the right order with proper data flow between steps.

Uses pytest-mock to patch all external dependencies (API calls, file I/O).
"""

import pytest
import sys
from unittest.mock import patch, MagicMock, call
from src.main import main, get_user_input


class TestGetUserInput:
    """Tests for the get_user_input function."""
    
    def test_get_user_input_returns_dict_with_all_keys(self):
        """
        Test that get_user_input returns a dict with all required keys.
        This validates the input structure expected by main().
        """
        with patch('builtins.input', return_value=''):
            result = get_user_input()
        
        required_keys = {
            "memory", "protagonist", "character_desc", "tone", "details",
            "style", "complexity", "title", "end_message", "other_characters",
            "cover_theme", "theme_color"
        }
        assert isinstance(result, dict)
        assert required_keys.issubset(result.keys()), "Missing required keys in get_user_input output"
    
    def test_get_user_input_all_values_are_strings(self):
        """Test that all values returned are non-empty strings."""
        with patch('builtins.input', return_value=''):
            result = get_user_input()
        
        for key, value in result.items():
            assert isinstance(value, str), f"Key '{key}' should be a string but got {type(value)}"
            assert len(value) > 0, f"Key '{key}' should not be empty"
    
    def test_get_user_input_uses_defaults_on_empty_input(self):
        """Test that defaults are applied when user provides no input."""
        with patch('builtins.input', return_value=''):
            result = get_user_input()
        
        # Verify some expected defaults are present
        assert "Maya" in result["protagonist"]
        assert "Funny" in result["tone"]
        assert "Rhyming" in result["style"]
        assert "light blue" in result["theme_color"]
    
    def test_get_user_input_accepts_custom_values(self):
        """Test that get_user_input accepts and returns custom user input."""
        custom_inputs = [
            "My custom memory",  # memory (first input call)
            "Alice",  # protagonist
            "a 5-year-old",  # character_desc
            "Serious",  # tone
            "in the park",  # details
            "Narrative",  # style
            "Short",  # complexity
            "My Title",  # title
            "Best wishes",  # end_message
            "dad",  # other_characters
            "clouds",  # cover_theme
            "light pink",  # theme_color
        ]
        
        with patch('builtins.input', side_effect=custom_inputs):
            result = get_user_input()
        
        assert result["protagonist"] == "Alice"
        assert result["tone"] == "Serious"
        assert result["memory"] == "My custom memory"


class TestMainPipelineOrchestration:
    """
    Tests the main() pipeline orchestration.
    Verifies that main() correctly calls external modules in sequence
    and passes data correctly between steps.
    """
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_happy_path_all_steps_succeed(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test the happy path: all API calls succeed and PDF is created.
        
        This validates:
        - main() calls all modules in the correct order
        - All success messages are printed
        - No sys.exit() is called
        """
        # Setup mock user input
        mock_user_input.return_value = {
            "memory": "Test memory",
            "protagonist": "TestChild",
            "character_desc": "A test character",
            "tone": "Funny",
            "details": "Test details",
            "style": "Rhyming",
            "complexity": "Standard",
            "title": "Test Story",
            "end_message": "The End",
            "other_characters": "Test parents",
            "cover_theme": "test theme",
            "theme_color": "light blue"
        }
        
        # Setup API mock responses
        mock_gemini.return_value = "Page 1\n\nPage 2\n\nPage 3\n\nPage 4\n\nPage 5"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img1.png", "img2.png", "img3.png", "img4.png", "img5.png"]
        mock_pdf.return_value = True
        
        # Execute
        main()
        
        # Verify all modules were called
        assert mock_gemini.called, "get_story_from_gemini should be called"
        assert mock_cover.called, "get_cover_image should be called"
        assert mock_images.called, "get_images_from_api should be called"
        assert mock_pdf.called, "create_pdf should be called"
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_execution_order_is_correct(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that main() calls modules in the correct execution order.
        Order: get_user_input → get_story_from_gemini → get_cover_image → 
               get_images_from_api → create_pdf
        """
        call_order = []
        
        def track_gemini(*args, **kwargs):
            call_order.append('gemini')
            return "Story text"
        
        def track_cover(*args, **kwargs):
            call_order.append('cover')
            return "cover.png"
        
        def track_images(*args, **kwargs):
            call_order.append('images')
            return ["img1.png"]
        
        def track_pdf(*args, **kwargs):
            call_order.append('pdf')
            return True
        
        mock_user_input.return_value = {
            "memory": "Memory", "protagonist": "Child", "character_desc": "Desc",
            "tone": "Funny", "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title", "end_message": "End",
            "other_characters": "Parents", "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_gemini.side_effect = track_gemini
        mock_cover.side_effect = track_cover
        mock_images.side_effect = track_images
        mock_pdf.side_effect = track_pdf
        
        main()
        
        expected_order = ['gemini', 'cover', 'images', 'pdf']
        assert call_order == expected_order, \
            f"Expected execution order {expected_order}, but got {call_order}"
    
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_exits_on_gemini_api_failure(self, mock_user_input, mock_gemini):
        """
        Test that main() exits immediately if Gemini API fails.
        Pipeline should not proceed to cover or image generation.
        """
        mock_user_input.return_value = {
            "memory": "Memory", "protagonist": "Child", "character_desc": "Desc",
            "tone": "Funny", "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title", "end_message": "End",
            "other_characters": "Parents", "cover_theme": "theme", "theme_color": "light blue"
        }
        mock_gemini.side_effect = Exception("API connection failed")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1, "main() should exit with code 1 on API failure"
    
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_exits_on_cover_image_failure(
        self, mock_user_input, mock_gemini, mock_cover
    ):
        """
        Test that main() exits if cover image generation fails.
        Story generation should succeed, but pipeline halts at cover stage.
        """
        mock_user_input.return_value = {
            "memory": "Memory", "protagonist": "Child", "character_desc": "Desc",
            "tone": "Funny", "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title", "end_message": "End",
            "other_characters": "Parents", "cover_theme": "theme", "theme_color": "light blue"
        }
        mock_gemini.return_value = "Story text"
        mock_cover.side_effect = Exception("Cover generation failed")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


class TestDataFlowBetweenModules:
    """
    Tests that data flows correctly from one module to the next.
    Validates parameter passing and data transformations in the pipeline.
    """
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_story_prompt_includes_all_user_inputs(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that the prompt sent to Gemini includes all relevant user inputs.
        This validates that the "master prompt" is correctly constructed.
        """
        user_inputs = {
            "memory": "Armadillo question",
            "protagonist": "Maya",
            "character_desc": "3-year-old with curly hair",
            "tone": "Funny",
            "details": "Family home, hallway and bathroom",
            "style": "Rhyming",
            "complexity": "Standard",
            "title": "Silly Maya",
            "end_message": "Merry Christmas",
            "other_characters": "Mom with blonde hair",
            "cover_theme": "armadillos and flowers",
            "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        # Extract the prompt that was sent to Gemini
        prompt_arg = mock_gemini.call_args[0][0]
        
        # Verify critical elements are in the prompt
        assert "5-page story" in prompt_arg, "Prompt should specify 5 pages"
        assert "Armadillo question" in prompt_arg, "Prompt should include the memory"
        assert "Maya" in prompt_arg, "Prompt should include protagonist name"
        assert "Funny" in prompt_arg, "Prompt should include tone"
        assert "Rhyming" in prompt_arg, "Prompt should include style"
        assert "mom's point of view" in prompt_arg.lower(), "Prompt should specify mom's POV"
        assert "4 rhyming lines" in prompt_arg, "Prompt should specify line constraints"
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_images_api_receives_correct_parameters(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that get_images_from_api receives the correct parameters.
        
        Expected parameters:
        1. story_text (from Gemini)
        2. character_desc (from user input)
        3. other_characters (from user input)
        4. details (from user input)
        """
        story_text = "Page 1\n\nPage 2"
        
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "A brave child with blue eyes",
            "tone": "Funny", "details": "In the forest",
            "style": "Rhyming", "complexity": "Standard",
            "title": "Title", "end_message": "End",
            "other_characters": "Friendly owl", "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = story_text
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img1.png", "img2.png"]
        mock_pdf.return_value = True
        
        main()
        
        # Verify get_images_from_api was called with correct parameters
        mock_images.assert_called_once_with(
            story_text,
            "A brave child with blue eyes",
            "Friendly owl",
            "In the forest"
        )
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_pdf_creation_receives_all_components(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that create_pdf receives all components from the pipeline.
        
        Expected parameters:
        - title, story_text, image_list, end_message, cover_image_path, 
          theme_color, output_filename
        """
        story_text = "Story"
        cover_path = "cover.png"
        images = ["img1.png", "img2.png", "img3.png", "img4.png", "img5.png"]
        
        user_inputs = {
            "memory": "Memory", "protagonist": "Luna",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Luna's Adventure",
            "end_message": "The End, Love Mom", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light pink"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = story_text
        mock_cover.return_value = cover_path
        mock_images.return_value = images
        mock_pdf.return_value = True
        
        main()
        
        # Verify create_pdf was called with correct parameters
        mock_pdf.assert_called_once_with(
            title="Luna's Adventure",
            story_text=story_text,
            image_list=images,
            end_message="The End, Love Mom",
            cover_image_path=cover_path,
            theme_color="light pink",
            output_filename="luna_storybook.pdf"
        )
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_output_filename_sanitization(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that protagonist name is correctly sanitized for the output filename.
        Spaces should be replaced with underscores and converted to lowercase.
        """
        user_inputs = {
            "memory": "Memory", "protagonist": "Sarah Jane Smith",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        # Verify the filename was properly sanitized
        call_kwargs = mock_pdf.call_args[1]
        assert call_kwargs['output_filename'] == "sarah_jane_smith_storybook.pdf"
        assert " " not in call_kwargs['output_filename']
        assert call_kwargs['output_filename'].islower()


class TestEdgeCasesAndErrorHandling:
    """
    Tests edge cases and error handling in the pipeline.
    """
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_handles_none_cover_image(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that main() handles gracefully when cover image API returns None.
        Pipeline should continue and pass None to create_pdf.
        """
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = None  # Cover generation failed
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        # Verify create_pdf was still called with None for cover_image_path
        call_kwargs = mock_pdf.call_args[1]
        assert call_kwargs['cover_image_path'] is None
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_handles_empty_image_list(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that main() handles gracefully when image generation returns empty list.
        Pipeline should continue and pass empty list to create_pdf.
        """
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = []  # No images generated
        mock_pdf.return_value = True
        
        main()
        
        call_kwargs = mock_pdf.call_args[1]
        assert call_kwargs['image_list'] == []
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_handles_pdf_creation_failure(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """
        Test that main() handles gracefully when PDF creation fails.
        Should print error but not crash.
        """
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = False  # PDF creation failed
        
        # Should not raise exception
        main()
    
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_handles_connection_error(self, mock_user_input, mock_gemini):
        """
        Test that main() handles ConnectionError from API gracefully.
        Should exit with code 1.
        """
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.side_effect = ConnectionError("Network unreachable")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_main_handles_timeout_error(self, mock_user_input, mock_gemini):
        """
        Test that main() handles TimeoutError from API gracefully.
        Should exit with code 1.
        """
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.side_effect = TimeoutError("Request timed out")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


class TestPromptConstruction:
    """
    Tests the prompt construction logic for Gemini API.
    Ensures the master prompt contains all critical elements for story generation.
    """
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_prompt_specifies_five_pages(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """Test that the prompt specifies 5-page story requirement."""
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        prompt = mock_gemini.call_args[0][0]
        assert "5-page" in prompt or "5 page" in prompt.lower()
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_prompt_specifies_mom_point_of_view(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """Test that the prompt specifies mom's point of view."""
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        prompt = mock_gemini.call_args[0][0]
        assert "mom" in prompt.lower() and "point of view" in prompt.lower()
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_prompt_specifies_rhyme_constraints(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """Test that the prompt specifies rhyming constraints."""
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        prompt = mock_gemini.call_args[0][0]
        assert "rhyming" in prompt.lower() or "rhyme" in prompt.lower()
        assert "4 lines" in prompt or "4 rhyming" in prompt.lower()
    
    @patch('src.main.create_pdf')
    @patch('src.main.get_images_from_api')
    @patch('src.main.get_cover_image')
    @patch('src.main.get_story_from_gemini')
    @patch('src.main.get_user_input')
    def test_prompt_specifies_page_separation_format(
        self, mock_user_input, mock_gemini, mock_cover, mock_images, mock_pdf
    ):
        """Test that the prompt specifies double newline page separation."""
        user_inputs = {
            "memory": "Memory", "protagonist": "Child",
            "character_desc": "Desc", "tone": "Funny",
            "details": "Details", "style": "Rhyming",
            "complexity": "Standard", "title": "Title",
            "end_message": "End", "other_characters": "Other",
            "cover_theme": "theme", "theme_color": "light blue"
        }
        
        mock_user_input.return_value = user_inputs
        mock_gemini.return_value = "Story"
        mock_cover.return_value = "cover.png"
        mock_images.return_value = ["img.png"]
        mock_pdf.return_value = True
        
        main()
        
        prompt = mock_gemini.call_args[0][0]
        assert "double newline" in prompt.lower() or "\\n\\n" in prompt


