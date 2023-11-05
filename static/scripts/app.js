
let mediaRecorder;
let audioChunks = [];

function startRecording() {
    
    audioChunks = [];
    
    document.getElementById("stop-record-btn").disabled = false;
    document.getElementById("start-record-btn").disabled = true;

    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks);
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();


            sendAudioToServer(audioBlob);
        });
    });
}

function stopRecording() {
    
    document.getElementById("start-record-btn").disabled = false;
    document.getElementById("stop-record-btn").disabled = true;
    if (mediaRecorder) {
        mediaRecorder.stop(); 
    }
}

function sendAudioToServer(blob) {
   
    let formData = new FormData();
    formData.append("audio_file", blob);

    fetch("/transcribe", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        
        console.log(data);
        document.getElementById("transcription").innerText = "Transcripción: " + data.text;
        
        translateText(data.text);
    })
    .catch(error => {
        console.error(error);
    });
}


function bindStopButton() {
    const stopButton = document.getElementById("stop-record-btn");
    if (stopButton) {
        stopButton.addEventListener("click", stopRecording);
    }
}


document.addEventListener("DOMContentLoaded", bindStopButton);

function translateText(textToTranslate) {
    fetch('/translate', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: textToTranslate })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    
    .then(data => {
        if ('translated_text' in data) {
            document.getElementById("translation").innerText = "Traducción: " + data.translated_text;
            synthesizeSpeech(data.translated_text);
        } else if ('error' in data) {
           
            document.getElementById("translation").innerText = "Error: " + data.error;
        }
    })
    
    .catch(error => {
        console.error(error);
    });
}


function synthesizeSpeech(textToSpeak) {
    fetch('/synthesize_speech', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: textToSpeak })
    })
    .then(response => response.json())
    .then(data => {
        
        const audioElement = document.getElementById("audio-playback");
        audioElement.src = data.speech_url;
        audioElement.play();
    })
    .catch(error => {
        console.error(error);
    });
}
