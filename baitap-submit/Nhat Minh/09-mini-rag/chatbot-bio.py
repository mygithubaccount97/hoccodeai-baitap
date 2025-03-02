# 1. Dùng chunking để làm bot trả lời tiểu sử người nổi tiếng, anime v...v
#   - <https://en.wikipedia.org/wiki/S%C6%A1n_T%C3%B9ng_M-TP>
#   - <https://en.wikipedia.org/wiki/Jujutsu_Kaisen>
import chromadb
from chromadb.utils import embedding_functions
from wikipediaapi import Wikipedia
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()
# BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
client_ai = OpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=API_KEY
)

COLLECTION_NAME = "Sep_Son_Tung_MTP"
client = chromadb.PersistentClient(path="./data")
client.heartbeat()

embedding_function = embedding_functions.DefaultEmbeddingFunction()
collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_function)

wiki = Wikipedia('HocCodeAI/0.0 (https://hoccodeai.com)', 'en')
doc = wiki.page('Sơn_Tùng_M-TP').text

# print(doc)

paragraphs = doc.split('\n\n')
for index, paragraph in enumerate(paragraphs):
    collection.add(documents=[paragraph], ids=[str(index)])

# print(collection.peek())
messages = [{
    "role": "system",
    "content": "You are required to always use the provided Wikipedia tool to retrieve factual information for any questions that require it. Do not rely solely on internal knowledge; always invoke the tool to ensure the answer is up-to-date and accurate."
}]
while True:
    query = input("Có hỏi gì về Sếp không: ")
    if query == "thoát":
        break

    q = collection.query(query_texts=[query], n_results=3)
    CONTEXT = q["documents"][0]
    prompt = f"""
    Use the following CONTEXT to answer the QUESTION at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use an unbiased and journalistic tone.
    
    CONTEXT: {CONTEXT}
    QUESTION: {query}
    """


    response = client_ai.chat.completions.create(
        model='qwen-2.5-32b',
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    print(f"BOT: {response.choices[0].message.content}")

