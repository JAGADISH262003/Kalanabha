import unittest
from unittest.mock import patch, MagicMock

# Import functions/variables to be tested
from src.utils import language_mapping, is_valid_youtube_link # Import the moved function
from src.translation import translate_text
# We will mock googletrans.Translator

class TestProcessingLogic(unittest.TestCase):

    def test_language_mapping(self):
        """Test that a known language maps to the correct code."""
        self.assertEqual(language_mapping.get("en"), "english")
        self.assertEqual(language_mapping.get("es"), "spanish")
        self.assertIsNone(language_mapping.get("xx")) # Non-existent key

    def test_youtube_link_validation(self):
        """Test the YouTube link regex validation."""
        valid_links = [
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=60s" # With parameters
        ]
        invalid_links = [
            "http://youtube.com/watch?v=",
            "http://youtube.com/watch",
            "ftp://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://example.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PL_12345"
        ]

        for link in valid_links:
            self.assertTrue(is_valid_youtube_link(link), f"Expected '{link}' to be valid.")
        
        for link in invalid_links:
            self.assertFalse(is_valid_youtube_link(link), f"Expected '{link}' to be invalid.")

    @patch('src.translation.Translator')
    def test_translate_text_same_language(self, MockTranslator):
        """Test translate_text when source and target languages are the same."""
        # MockTranslator instance is not used as the function should return early
        src_text = "Hello world"
        translated = translate_text(src_text, "en", "en")
        self.assertEqual(translated, src_text)
        MockTranslator.assert_not_called() # Translator should not be initialized or used

    @patch('src.translation.Translator')
    def test_translate_text_different_language(self, MockTranslator):
        """Test translate_text when source and target languages are different."""
        mock_translator_instance = MockTranslator.return_value
        mock_translation_result = MagicMock()
        mock_translation_result.text = "Hola mundo"
        mock_translator_instance.translate.return_value = mock_translation_result

        src_text = "Hello world"
        src_lang = "en"
        target_lang = "es"
        
        translated = translate_text(src_text, src_lang, target_lang)
        
        self.assertEqual(translated, "Hola mundo")
        MockTranslator.assert_called_once() # Ensure Translator was initialized
        mock_translator_instance.translate.assert_called_once_with(src_text, src=src_lang, dest=target_lang)

    @patch('src.translation.Translator')
    def test_translate_text_empty_input(self, MockTranslator):
        """Test translate_text with empty input text."""
        with self.assertRaises(RuntimeError) as context: # Assuming it raises RuntimeError for empty text after changes
            translate_text("", "en", "es")
        self.assertIn("No text provided for translation", str(context.exception)) #Check if the error message is as expected
        MockTranslator.assert_not_called()

    @patch('src.translation.Translator')
    def test_translate_text_translation_failure(self, MockTranslator):
        """Test translate_text when the underlying translate call fails."""
        mock_translator_instance = MockTranslator.return_value
        mock_translator_instance.translate.side_effect = Exception("Simulated API error")

        src_text = "Hello world"
        with self.assertRaises(RuntimeError) as context:
            translate_text(src_text, "en", "es")
        
        self.assertIn("Error during translation", str(context.exception))
        self.assertIn("Simulated API error", str(context.exception))
        MockTranslator.assert_called_once()
        mock_translator_instance.translate.assert_called_once_with(src_text, src="en", dest="es")


if __name__ == '__main__':
    unittest.main()
