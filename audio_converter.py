import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import jieba
import jieba.posseg as pseg
import stopwordsiso as stopwords
from pydub import AudioSegment  # Import pydub for audio conversion
from googletrans import Translator

app = Flask(__name__)
CORS(app)

recognizer = sr.Recognizer()

# Dynamically fetch Chinese stopwords
stop_words = stopwords.stopwords("zh")
desired_tags = {'n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a', 'ad', 'an'}

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
            sentence = recognizer.recognize_google(audio_data, language='zh-CN')

        # Tokenize and POS-tag words
        words = pseg.cut(sentence)
        filtered_words = [word for word, tag in words if word not in stop_words and tag in desired_tags]

        translated_keywords = [translator.translate(word, src='zh-CN', dest='en').text for word in filtered_words]

        return jsonify({'keywords': translated_keywords})

    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Request failed: {e}'}), 500
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