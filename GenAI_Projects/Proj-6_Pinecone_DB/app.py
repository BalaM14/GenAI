from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from main import (
    load_data, split_chunks, embed_vectors, format_vectors,
    insert_vectors, inferrence, llm_response, embed, pc
)
import os
import shutil

# Load env and initialize Flask
load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Data/'
app.config['PROCESSED_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded')

index_name = "test"
pc_index = pc.Index(index_name)

# List new PDFs (not yet embedded)
def list_pending_pdfs():
    return [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]

# List already embedded PDFs
def list_uploaded_pdfs():
    uploaded = []
    if os.path.exists(app.config['PROCESSED_FOLDER']):
        uploaded = [f for f in os.listdir(app.config['PROCESSED_FOLDER']) if f.endswith('.pdf')]
    return uploaded

# Move processed PDFs to /uploaded/
def move_processed_files():
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    for file in list_pending_pdfs():
        src = os.path.join(app.config['UPLOAD_FOLDER'], file)
        dst = os.path.join(app.config['PROCESSED_FOLDER'], file)
        shutil.move(src, dst)

@app.route('/', methods=['GET'])
def index():
    pdfs_pending = list_pending_pdfs()
    pdfs_uploaded = list_uploaded_pdfs()
    return render_template('index.html', pdfs=pdfs_pending, inserted=pdfs_uploaded)

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("pdfs")
    for file in uploaded_files:
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process_files():
    data = load_data(app.config['UPLOAD_FOLDER'])  # only picks from Data/, not /uploaded/
    if data:
        chunks, texts = split_chunks(data)
        vectors = embed_vectors(texts, chunks, embed)
        formatted = format_vectors(vectors)
        insert_vectors(pc_index, formatted)
        move_processed_files()  # move PDFs to /uploaded after embedding
    return redirect(url_for('ask'))

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    answer = ""
    if request.method == 'POST':
        query = request.form['query']
        search_result = inferrence(index_name, embed, query)
        final_response = "\n\n".join(
            [match['metadata']['text'] for match in search_result['matches']]
        )
        answer = llm_response(final_response, query)
    return render_template('ask.html', answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
