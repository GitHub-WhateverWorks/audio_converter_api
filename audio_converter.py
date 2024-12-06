import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import jieba.posseg as pseg
import stopwordsiso as stopwords
from pydub import AudioSegment  # Import pydub for audio conversion
from googletrans import Translator  # For translation

app = Flask(__name__)
CORS(app)

recognizer = sr.Recognizer()

# Dynamically fetch Chinese stopwords
stop_words = stopwords.stopwords("zh")
desired_tags = {'n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a', 'ad', 'an'}

# Initialize translator
translator = Translator()

@app.route('/audio_converter_api', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['file']
    original_file_path = os.path.join('uploads', audio_file.filename)
    wav_file_path = os.path.splitext(original_file_path)[0] + '.wav'

    # Save the original audio file
    audio_file.save(original_file_path)

    try:
        # Convert audio file to WAV format
        audio = AudioSegment.from_file(original_file_path)
        audio.export(wav_file_path, format='wav')

        # Perform speech recognition on the WAV file
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
            try:
                # Attempt to recognize the speech in the audio
                sentence = recognizer.recognize_google(audio_data, language='zh-CN')
                print(f"Recognized sentence: {sentence}")  # Debugging: Print recognized sentence
            except sr.UnknownValueError:
                return jsonify({'error': 'Speech recognition could not understand audio'}), 400
            except sr.RequestError as e:
                return jsonify({'error': f'Request failed: {e}'}), 500

            # Check if the sentence is empty or None
            if not sentence:
                return jsonify({'error': 'No speech detected in the audio'}), 400

        # Tokenize and POS-tag words (Chinese sentence)
        words = pseg.cut(sentence)
        filtered_words = [word for word, tag in words if word not in stop_words and tag in desired_tags]

        print(f"Filtered words: {filtered_words}")  # Debugging: Print filtered words

        # Check if there are any keywords to translate
        if not filtered_words:
            return jsonify({'error': 'No meaningful keywords found'}), 400

        # Translate the filtered Chinese keywords into English
        translated_keywords = []
        for word in filtered_words:
            try:
                translation = translator.translate(word, src='zh-CN', dest='en').text
                print(f"Translated '{word}' to '{translation}'")  # Debugging: Print each translation
                if translation:
                    translated_keywords.append(translation)
            except Exception as e:
                print(f"Error during translation of word '{word}': {e}")  # Debugging: Log translation error
                continue  # Skip the word if translation fails

        # Check if the translation is successful and return the keywords
        if not translated_keywords:
            return jsonify({'error': 'No valid translated keywords found'}), 400

        return jsonify({'keywords': translated_keywords})

    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debugging: Log unexpected errors
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        # Clean up files
        if os.path.exists(original_file_path):
            os.remove(original_file_path)
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'API is running'}), 200

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=15000)