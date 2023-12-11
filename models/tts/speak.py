import time
import os
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import logging

# Constants
OUTPUT_DIR = "output/tts/" # To do : create directory if doesn't exist

# Initialize the logger
logger = logging.getLogger(__name__)

# Define a function to save speech and log request details
def save_speech_and_log(text, speech):
    try:
        # Generate a timestamp for the file name
        timestamp = int(time.time())
        wav_filename = f"{OUTPUT_DIR}speech_{timestamp}.wav"
        log_filename = f"{OUTPUT_DIR}speech_{timestamp}.log"
        
        # Save the speech to a WAV file
        sf.write(wav_filename, speech.numpy(), samplerate=16000)
        
        # Save request details to a log file
        with open(log_filename, 'w') as log_file:
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(f"Text: {text}\n")
        
        return wav_filename
    except Exception as e:
        logger.exception("An error occurred during speech and log saving.")
        raise

# Define a function to load the TTS model
def load_model():
    processor = SpeechT5Processor.from_pretrained("models/tts/speecht5_tts/")
    model = SpeechT5ForTextToSpeech.from_pretrained("models/tts/speecht5_tts/")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

    model_dict = {
        'processor': processor,
        'model': model,
        'vocoder': vocoder,
        'speaker_embeddings': speaker_embeddings,
    }

    return model_dict

# Define a function to generate speech from text
def speak(text, model_dict):
    logger.info("TTS model received the following text:")
    logger.info(text)
    logger.info("Reading it...")
    inputs = model_dict["processor"](text=text, return_tensors="pt")
    speech = model_dict["model"].generate_speech(inputs["input_ids"], model_dict["speaker_embeddings"], vocoder=model_dict["vocoder"])
    logger.info("Finished")
    return speech
