# sudo apt-get install portaudio19-dev
# gcloud auth application-default login
# gcloud auth application-default set-quota-project tidy-tine-423303-s1

# Import dependencies
import os, io, sys, asyncio, argparse
from google.cloud import speech, texttospeech
import sounddevice as sd
import wavio
from pydub import AudioSegment
from openai import OpenAI
from pynput import keyboard

OPENAI_API_KEY=""
client = OpenAI(api_key=OPENAI_API_KEY)

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

def ask_openai(text):

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": text}
    ]
    )

    print(completion.choices[0].message)

    return completion.choices[0].message

def convert_to_mono(input_file, output_file):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)
    
    # Convert to mono
    mono_audio = audio.set_channels(1)
    
    # Export the mono audio
    mono_audio.export(output_file, format="wav")

def main():
    # Record and save audio
    record_and_save(duration=3, filename="output.wav")
    
    # Convert to mono
    convert_to_mono("output.wav", "output_mono.wav")
    
    # Transcribe speech to text
    transcribed_text = speech_to_text("output_mono.wav")

    # Get response from openai 
    #response_text = ask_openai(transcribed_text)
    
    # Convert text back to speech
    #text_to_speech(response_text)
    text_to_speech(transcribed_text)

def on_press(key):
    try:
        if key.char == 'r':
            main()
        elif key.char == 'x':
            print("Exiting the program.")
            sys.exit()
    except AttributeError:
        pass

def start_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    # print("="*40)
    # print("      Welcome to Raspberry Pi Home!      ")
    # print("="*40)
    # print("Press 'r' to ask a question")
    # print("Press 'x' to exit the program")
    # print("="*40)
    # start_listener()
    main()
    



