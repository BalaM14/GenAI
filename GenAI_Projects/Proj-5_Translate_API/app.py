import openai
import os
from flask import Flask, request, render_template
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static"

@app.route('/translate', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        language = request.form["language"]
        file = request.files['audio_file']
        if file:
            audio_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(audio_path)
            
            with open(audio_path, "rb") as audio_file:
                transcript = openai.Audio.translate("whisper-1", audio_file)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a translator. Translate the following transcript to {language}."
                    },
                    {
                        "role": "user",
                        "content": transcript["text"]
                    }
                ],
                temperature=0,
                max_tokens=256
            )

            return render_template("index.html", translated_text=response.choices[0].message["content"])

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
