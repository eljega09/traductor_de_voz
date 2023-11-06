from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import speech_recognition as sr
from gtts import gTTS
from libretranslatepy import LibreTranslateAPI
import subprocess
import os
import uuid
import http.client
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import urllib.parse

app = Flask(__name__, static_url_path='/static')
CORS(app)

# Iniciar el objeto reconocedor de voz
recognizer = sr.Recognizer()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400

    audio_file = request.files['audio_file']
    unique_filename = str(uuid.uuid4())
    original_path = f"temp/{unique_filename}.webm"
    converted_path = f"temp/{unique_filename}.wav"
    audio_file.save(original_path)

    # Intenta convertir el archivo de audio a formato WAV
    try:
        subprocess.check_call(['ffmpeg', '-i', original_path, '-ar', '16000', '-ac', '1', converted_path])
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode('utf-8') if e.output else "No output"
        os.remove(original_path)  # Limpiar el archivo original
        return jsonify({'error': 'Failed to convert audio file', 'ffmpeg_error': error_output}), 500
    except Exception as e:
        os.remove(original_path)  # Limpiar el archivo original
        return jsonify({'error': 'An unexpected error occurred', 'detail': str(e)}), 500

    # Intenta procesar el archivo de audio convertido
    try:
        with sr.AudioFile(converted_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='es-ES')
    except sr.UnknownValueError:
        text = "Speech recognition could not understand audio"
    except sr.RequestError as e:
        text = f"Could not request results from speech recognition service; {e}"
    finally:
        # Limpiar archivos después del procesamiento
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(converted_path):
            os.remove(converted_path)

    
    if 'error' in text:
        return jsonify({'error': text}), 400

   
    return jsonify({'text': text})


@app.route('/translate', methods=['POST'])
def translate_text():
   
    data = request.json
    text_to_translate = data.get('text')
    if not text_to_translate:
        return jsonify({'error': 'No text provided'}), 400

    conn = http.client.HTTPSConnection("google-translate1.p.rapidapi.com")

    
    payload = urllib.parse.urlencode({'q': text_to_translate, 'target': 'en'})  # solo traduce en ingles
    """
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'Accept-Encoding': "application/gzip",
        'X-RapidAPI-Key': "209c0a67aamsh03178906980785bp12106cjsnd81bba3eef39",
        'X-RapidAPI-Host': "google-translate1.p.rapidapi.com"
    }

    """
    headers = {
    'content-type': "application/x-www-form-urlencoded",
    'Accept-Encoding': "application/gzip",
    #'X-RapidAPI-Key': os.environ.get("X_RapidAPI_Key"),
    'X-RapidAPI-Host': "google-translate1.p.rapidapi.com"
}

    try:
        
        conn.request("POST", "/language/translate/v2", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        translation_data = json.loads(data.decode("utf-8"))

        
        translated_text = translation_data["data"]["translations"][0]["translatedText"]
        
    except Exception as e:
        return jsonify({'error': 'Failed to translate text', 'detail': str(e)}), 502

    return jsonify({'translated_text': translated_text})



@app.route('/synthesize_speech', methods=['POST'])
def synthesize_speech():
    
    data = request.json
    text = data.get('text') 
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    # Convertir texto a audio
    tts = gTTS(text=text, lang='en')
    tts.save("static/translated_speech.mp3")  
    return jsonify({'speech_url': '/static/translated_speech.mp3'})


if __name__ == "__main__":
    if not os.path.exists('temp'):
        os.makedirs('temp')
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
