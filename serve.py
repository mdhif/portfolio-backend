import uvicorn
from fastapi import FastAPI, HTTPException, Response

from models.tts.speak import load_model, speak, save_speech_and_log
from pydantic import BaseModel
import logging
import soundfile as sf
import time
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define CORS settings
origins = [
    "*",  # Add your frontend's origin(s) here
]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # You can specify specific headers if needed
)

# Define the TextRequest model using Pydantic
class TextRequest(BaseModel):
    text: str

# Initialize the FastAPI app
app = FastAPI()

# Initialize the logger
logger = logging.getLogger(__name__)


# Define an OPTIONS endpoint to handle preflight requests
@app.options("/tts")
async def options_tts():
    return {"allow": "POST"}  # Respond with the allowed methods for the /tts endpoint

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/tts")
def speak_text(request_data: TextRequest):
    text = request_data.text
    logger.info(f"Received text: {text}")
    
    if not text:
        logger.error("No text to process.")
        raise HTTPException(status_code=400, detail="No text provided")

    try:
        # Time the execution of the loop
        start_time = time.time()
        # Apply text to speech model
        speech = speak(text, tts_model)
        # Log model output
        logger.info(f"Generated speech: {speech}")
        # Save to file and get the file path
        wav_filename = save_speech_and_log(text, speech)
        # Compute execution time
        end_time = time.time() - start_time
        logger.info(f"Generated speech in {end_time:.2f} seconds: {speech}")
        
        # Check if the file exists
        if not os.path.exists(wav_filename):
            raise HTTPException(status_code=500, detail="Speech file not generated correctly")
        
        # Read the WAV file
        with open(wav_filename, "rb") as wav_file:
            wav_data = wav_file.read()
        
        # Return the WAV file as a response with appropriate headers
        response = Response(content=wav_data, media_type="audio/wav")
        response.headers["Content-Disposition"] = f"attachment; filename=speech.wav"
        
        return response
    except Exception as e:
        logger.exception("An error occurred during text-to-speech processing.")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Load text to speech models
    logger.info("Loading TextToSpeech model")
    tts_model = load_model()

    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8080)
