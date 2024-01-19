import os
from gtts import gTTS


def generate_audio(text: str, lang: str, file_path: str, slow: bool = False) -> os.path:
    """ Generate audio file from text
    
    Args:
        text (str): Text to convert to audio
        lang (str): Language to use
        file_path (str): Name of file to save audio to
        
    Returns:
        os.path: Path to audio file
    """
    
    # Save a default message if no text is found
    empty_message = {
        "es": "No se ha encontrado texto",
        "en": "No text found"
    }
    if not text:
        text = empty_message[lang]
    
    # Clean text
    text = text.strip()
    clean_chars = [
        "\n"
    ]
    for char in clean_chars:
        text = text.replace(char, " ")
    
    # Create file dirs
    file_dir = os.path.dirname(file_path)
    os.makedirs(file_dir, exist_ok=True)
    
    # Generate audio
    gtts_audio = gTTS(text=text, lang=lang, slow=slow)
    gtts_audio.save(file_path)
    
    return file_path


if __name__ == "__main__":
    text = "this is a sample text"
    lang = "en"
    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder)
    audio_file = os.path.join(parent_folder, 'sample.mp3')
    generate_audio(text, lang, audio_file)