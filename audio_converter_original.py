import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
app = Flask(__name__)
CORS(app)  
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
recognizer = sr.Recognizer()
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
            sentence = recognizer.recognize_google(audio)
        words = word_tokenize(sentence.lower())
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        pos_tags = pos_tag(filtered_words)
        keywords = [word for word, tag in pos_tags if tag in ('NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS')]
        return jsonify({'keywords': keywords})
    
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
    app.run(host='0.0.0.0', port=5000)