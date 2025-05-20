from googletrans import Translator, LANGUAGES
from src.utils import language_mapping # Assuming utils.py is in the same directory

def translate_text(text, src_lang_code, target_lang_code):
    """
    Translates text from a source language to a target language.

    Args:
        text (str): The text to translate.
        src_lang_code (str): The language code of the source text (e.g., 'en' for English).
                               This should be a code recognized by Whisper.
        target_lang_code (str): The language code for the target language (e.g., 'es' for Spanish).
                                This should be a key from `language_mapping`.

    Returns:
        str: The translated text, or None if translation fails.
    """
    if not text:
        print("Error: No text provided for translation.")
        return None

    # Ensure the source language code from Whisper is compatible with Google Translate
    # Whisper might return 'zh-cn', Google Translate expects 'zh-CN' or just 'zh'
    # Usually, the short codes (e.g., 'en', 'es') work fine.
    # We'll use the source language code as is, assuming it's generally compatible.
    # If issues arise, mapping might be needed.
    # Example: Whisper gives 'zh-cn', Google Translate needs 'zh-cn' or 'zh-hans'

    # Get the full language name for Google Translate from our mapping
    # googletrans uses language codes directly, but our mapping might be useful for other purposes
    # or if we need to display the full language name.
    # For the Translator, we use the target_lang_code directly.

    if target_lang_code not in language_mapping and target_lang_code not in LANGUAGES:
         # Check if the target_lang_code is a direct key in googletrans.LANGUAGES (e.g. 'zh-cn')
        print(f"Warning: Target language code '{target_lang_code}' not in predefined language_mapping or googletrans.LANGUAGES.")
        # Attempt to use it directly if it's a valid code for googletrans
        # No specific validation here, googletrans will raise an error if it's invalid.

    print(f"Initializing Google Translator...")
    translator = Translator()
    
    print(f"Attempting to translate from '{src_lang_code}' to '{target_lang_code}'...")
    try:
        # Perform the translation
        translation_result = translator.translate(text, src=src_lang_code, dest=target_lang_code)
        translated_text = translation_result.text
        
        # print(f"Original text ({src_lang_code}): {text}") # Can be long
        # print(f"Translated text ({target_lang_code}): {translated_text}") # Can be long
        print(f"Translation successful from '{src_lang_code}' to '{target_lang_code}'.")
        return translated_text
    except Exception as e:
        error_message = f"Error during translation from '{src_lang_code}' to '{target_lang_code}': {str(e)}. "
        if "invalid source language" in str(e).lower():
            error_message += f"The source language code '{src_lang_code}' might be invalid or unsupported. "
        if "invalid destination language" in str(e).lower():
             error_message += f"The target language code '{target_lang_code}' might be invalid or unsupported. Check `googletrans.LANGUAGES`. "
        # Add a note about potential network issues for common errors like 'AttributeError: 'NoneType' object has no attribute 'group''
        if "'NoneType' object has no attribute 'group'" in str(e) or "HTTPError 503" in str(e): # Common with googletrans if service is unavailable or rate limited
            error_message += "This might be due to network issues or the translation service being temporarily unavailable. Please try again later."

        print(error_message)
        raise RuntimeError(error_message)

if __name__ == '__main__':
    # Example Usage
    sample_text_en = "Hello, how are you today?"
    detected_lang_en = "en" # Simulate Whisper's output

    sample_text_hi = "नमस्ते आप कैसे हैं?" # Hindi
    detected_lang_hi = "hi"


    # Test 1: English to Spanish
    target_es = "es"
    print(f"\n--- Translating from English to Spanish ---")
    translated_spanish = translate_text(sample_text_en, detected_lang_en, target_es)
    if translated_spanish:
        print(f"English to Spanish: {translated_spanish}")

    # Test 2: English to French
    target_fr = "fr"
    print(f"\n--- Translating from English to French ---")
    translated_french = translate_text(sample_text_en, detected_lang_en, target_fr)
    if translated_french:
        print(f"English to French: {translated_french}")

    # Test 3: Hindi to English
    target_en = "en"
    print(f"\n--- Translating from Hindi to English ---")
    translated_english_from_hindi = translate_text(sample_text_hi, detected_lang_hi, target_en)
    if translated_english_from_hindi:
        print(f"Hindi to English: {translated_english_from_hindi}")


    # Test 4: Invalid target language
    target_invalid = "xx"
    print(f"\n--- Translating from English to Invalid Language ('{target_invalid}') ---")
    translated_invalid = translate_text(sample_text_en, detected_lang_en, target_invalid)
    if not translated_invalid:
        print(f"Translation to '{target_invalid}' failed as expected.")

    # Test 5: Using a language code like 'zh-cn' (Whisper might output this)
    sample_text_zh = "你好，世界"
    detected_lang_zh = "zh-cn" # Whisper might output this for Chinese (Simplified)
    target_lang_en_from_zh = "en"
    print(f"\n--- Translating from Chinese ('{detected_lang_zh}') to English ---")
    translated_en_from_zh = translate_text(sample_text_zh, detected_lang_zh, target_lang_en_from_zh)
    if translated_en_from_zh:
        print(f"Chinese to English: {translated_en_from_zh}")

    # Test with a language_mapping key
    target_german_key = "de" # 'de' is a key in language_mapping
    print(f"\n--- Translating from English to German (using key '{target_german_key}') ---")
    translated_german = translate_text(sample_text_en, detected_lang_en, target_german_key)
    if translated_german:
        print(f"English to German: {translated_german}")
