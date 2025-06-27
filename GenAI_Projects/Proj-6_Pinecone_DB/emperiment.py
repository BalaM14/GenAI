# Databricks notebook source
!pip install langchain pypdf openai tiktoken langchain_community pinecone

# COMMAND ----------

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from pinecone import Pinecone
from langchain.prompts import PromptTemplate
import os

# COMMAND ----------

loader = PyPDFDirectoryLoader("Data/")
data = loader.load()

# COMMAND ----------

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(data)
texts = [doc.page_content for doc in chunks]

# COMMAND ----------

import os
from dotenv import load_dotenv

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['PINECONE_API_KEY'] = os.getenv("PINECONE_API_KEY")


# COMMAND ----------

embed = OpenAIEmbeddings()
embeddings = embed.embed_documents(texts)

# COMMAND ----------

vectors = [
    {
        "id": f"id-{i}",
        "values": vector,
        "metadata": {
            "source": chunks[i].metadata.get("source", ""),
            "text": chunks[i].page_content,  # ✅ this is what you're missing
            "vector": vector
        }
    }
    for i, vector in enumerate(embeddings)
]

# Ensure that the vectors are in the correct format
corrected_vectors = [
    {
        'id': vector['id'],
        'values': vector['values'],
        'metadata': {
            key: str(value) if isinstance(value, (list, dict)) else value
            for key, value in vector['metadata'].items()
        }
    }
    for vector in vectors
]


# COMMAND ----------

from pinecone import Pinecone

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("drug")

# COMMAND ----------

index

# COMMAND ----------

index.delete(delete_all=True)

# COMMAND ----------

index.upsert(corrected_vectors)

# COMMAND ----------


inference_index = pc.Index("drug")

# COMMAND ----------

query = "What kind of Drug using here?"
query_vector = embed.embed_query(query)

response = inference_index.query(
    vector=query_vector,
    top_k=3,
    include_metadata=True
)

for i in response['matches']:
    print(f"Response: \n\n {i['metadata']['text']}")

# COMMAND ----------

retrieved_chunks = "\n\n".join([match['metadata']['text'] for match in response['matches']])
retrieved_chunks

# COMMAND ----------

import openai, os
openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = f"""
You are a helpful assistant that answers questions based on provided context.

Context:
{retrieved_chunks}

Question:
{query}

Answer:
"""

response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    max_tokens=300,
)

print("💬 Final Answer:\n", response.choices[0].message.content)


# COMMAND ----------

