from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from pinecone import Pinecone
from langchain.prompts import PromptTemplate
import os
import openai
from dotenv import load_dotenv
import glob
import shutil

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['PINECONE_API_KEY'] = os.getenv("PINECONE_API_KEY")

embed = OpenAIEmbeddings()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")


def load_data(dir_path):
    loader = PyPDFDirectoryLoader(dir_path)
    data = loader.load()
    return data


def split_chunks(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(data)
    texts = [doc.page_content for doc in chunks]
    return chunks, texts


def embed_vectors(texts,chunks,embed):   
    embeddings = embed.embed_documents(texts)
    vectors = [
            {
                "id": f"id-{i}",
                "values": vector,
                "metadata": {
                    "source": chunks[i].metadata.get("source", ""),
                    "text": chunks[i].page_content,  # ✅ this is what you're missing
                    #"vector": vector
                }
            }
            for i, vector in enumerate(embeddings)
            ]
    return vectors


def format_vectors(embedded_vectors):
    pc_vectors = [
                            {
                                'id': vector['id'],
                                'values': vector['values'],
                                'metadata': {
                                    key: str(value) if isinstance(value, (list, dict)) else value
                                    for key, value in vector['metadata'].items()
                                }
                            }
                            for vector in embedded_vectors
                        ]
    return pc_vectors


def insert_vectors(pc_index, pc_vectors):
    pc_index.upsert(pc_vectors)
    return True


def move_uploaded_pdfs(source_dir="Data", target_dir="Data/uploaded"):
    os.makedirs(target_dir, exist_ok=True)
    for file in os.listdir(source_dir):
        if file.endswith(".pdf"):
            shutil.move(os.path.join(source_dir, file), os.path.join(target_dir, file))


def inferrence(index_name,embed,user_query):
    inference_index = pc.Index(index_name)
    query_vector = embed.embed_query(user_query)

    response = inference_index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True
    )
    return response


def llm_response(final_response,user_query):
    prompt = f"""
                You are a helpful assistant that only answers questions using the provided context.
                Context:
                {final_response}
                Question:
                {user_query}
                Answer the question in detail using only the information found in the context. If only headings or hints are available, expand on them based on what is implied. Avoid adding any external knowledge.
            """

    llm_response_msg = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300,
            )
    return llm_response_msg.choices[0].message.content


if __name__ == "__main__":
    data = load_data("Data/")
    print("Data loaded successfully")
    chunks, texts = split_chunks(data)
    print("Chunks completed successfully")
    embedded_vectors = embed_vectors(texts,chunks,embed)
    print("Embedding completed successfully")
    pc_vectors = format_vectors(embedded_vectors)
    print("Formmated vectors to Pinecone DB format")
    print(f"Dimension of vector: {len(embedded_vectors[0]['values'])}")
    index_name = "test"
    pc_index = pc.Index(index_name)
    vectors_inserted = insert_vectors(pc_index, pc_vectors)
    print("Inserted the vectors to Pinecone DB")
    move_uploaded_pdfs()
    user_query = input("Enter the query?")
    response = inferrence(index_name,embed,user_query)
    print(user_query)
    print(f"No. of matching records: {len(response['matches'])}")
    final_response = ""
    for i in response['matches']:
        text_content = i['metadata']['text']
        print(f"\n\nDB_Response: \n{text_content}")
        final_response += "\n\n" + text_content

    answer = llm_response(final_response,user_query)
    print(f"\n\nLLM Response: \n{answer}")