import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

audio_file = open("voice.mp3",'rb')
output = openai.Audio.translate("whisper-1",audio_file)
print(output)