# sudo apt-get install portaudio19-dev

# Import dependencies
import os, io, sys, asyncio, argparse
from google.cloud import speech, texttospeech
import sounddevice as sd
import wavio
from pydub import AudioSegment

OPENAI_API_KEY=""

def record_and_save(duration=3, filename= "output.wav"):
    print("Recording in progress...")

    # Recording audio
    fs = 44100  # Sample rate
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()

    print("Recording done.")

    # Saving as .wav file
    wavio.write(filename, recording, fs, sampwidth=2)

    print(f"Audio recorded and saved as {filename}")

def speech_to_text(audio_file_path):
    """
    Transcribes speech from an audio file to text using Google Cloud Speech-to-Text API.

    Args:
        audio_file_path (str): Path to the audio file to transcribe.

    Returns:
        ret: Transcribed text from the speech.
    """
    # Instantiate a client
    client = speech.SpeechClient()

    # Loads the audio file
    with io.open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()

    # Configure the speech recognition
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    ret = ""
    for result in response.results:
        ret += result.alternatives[0].transcript

    print("Speech translated to text!")
    print("Text:" + ret)

    return ret 

def text_to_speech(text):
    """
    Convert text to speech using Google Cloud Text-to-Speech API.

    Args:
        text (str): The text to be converted to speech.

    Returns:
        None
    """
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech request on the text input with the selected voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("result.wav", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)

    print("Text translated to audio!")

    return 

def convert_to_mono(input_file, output_file):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)
    
    # Convert to mono
    mono_audio = audio.set_channels(1)
    
    # Export the mono audio
    mono_audio.export(output_file, format="wav")

if __name__ == "__main__":
    record_and_save(duration=3, filename= "output.wav")
    convert_to_mono("output.wav", "output.wav")
    text = speech_to_text("output.wav")
    text_to_speech(text)


