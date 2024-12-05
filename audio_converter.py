import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import jieba
import jieba.posseg as pseg
from stop_words import get_stop_words

app = Flask(__name__)
CORS(app)  

recognizer = sr.Recognizer()

import jieba
import jieba.posseg as pseg
import stopwordsiso as stopwords

# Dynamically fetch Chinese stopwords
stop_words = stopwords.stopwords("zh")

desired_tags = {'n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a', 'ad', 'an'}

@app.route('/audio_converter_api', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['file']

    # Save the audio file
    file_path = os.path.join('uploads', audio_file.filename)
    audio_file.save(file_path)

    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            sentence = recognizer.recognize_google(audio, language='zh-CN')

        # Tokenize and POS-tag words
        words = pseg.cut(sentence)
        # Filter words based on stopwords and POS tags
        filtered_words = [word for word, tag in words if word not in stop_words and tag in desired_tags]
        return jsonify({'keywords': filtered_words})

    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Request failed: {e}'}), 500
    finally:
        os.remove(file_path)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'API is running'}), 200

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=15000)
