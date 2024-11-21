# from openai import OpenAI
# import elevenlabs
import speech_recognition as sr
import time
import nltk
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')

recognizer = sr.Recognizer()
transcript_result = None

def handle_conversation():
    while True:
        start_time = time.time()
        words = ""
        keywords = []
        try:
            # Capture audio from the microphone
            with sr.Microphone() as source:
                print("Say something...")
                audio = recognizer.listen(source)
                sentence = recognizer.recognize_google(audio)
                # sentence = "Machine learning is transforming the technology landscape."
                words = word_tokenize(sentence.lower())
                            # Filter out stop words
                stop_words = set(stopwords.words('english'))
                filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
                
                # Tag parts of speech
                pos_tags = pos_tag(filtered_words)
                keywords = [word for word, tag in pos_tags if tag in ('NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS')]
                print(transcript_result)
                print("Keywords:", keywords)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            continue
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            continue

        end_time = time.time()
        print(f"Recognition Time: {end_time - start_time}")
        start_time = time.time()


handle_conversation()