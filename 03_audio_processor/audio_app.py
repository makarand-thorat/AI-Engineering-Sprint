import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def process_audio(audio_file_path):
    #1.Upload the file
    print(f"Uploading file: {audio_file_path}...")
    audio_file = client.files.upload(file=audio_file_path)

    #2.We wait for google to process the file
    while audio_file.state.name == "PROCESSING":
        print("Waiting for file to be processed...")
        time.sleep(5)
        audio_file = client.files.get(name=audio_file.name)
    print(f"File processed: {audio_file.name}")

    #3.Multimodal prompt
    prompt = """
    Transcribe this audio file accurately.
    -Identify different speakers and label them (eg., Speaker 1, Speaker2).
    -Provide a timestamp for each speaker's contribution in [MM:SS] format
    -If a speaker is speaking for long time provide time stamp after every 30 seconds
    """

    print("Analyzing content...")
    response=client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt,audio_file]
        )
    return response.text

if __name__ == "__main__":
    FILE_TO_PROCESS="podcast.mp3"

    if os.path.exists(FILE_TO_PROCESS):
        result = process_audio(FILE_TO_PROCESS)

        #SAVE THE TRANSCRIPT
        with open("podcast.txt","w") as f:
            f.write(result)
        
        print("\n---RESULT---\n")
        print(result)
    else:
        print(f"Could not find {FILE_TO_PROCESS} in this folder.")