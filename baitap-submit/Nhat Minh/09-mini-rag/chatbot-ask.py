# 2. Thay vì hardcode `doc = wiki.page('Hayao_Miyazaki').text`, sử dụng function calling để:
#   - Lấy thông tin cần tìm từ câu hỏi
#   - Dùng `wiki.page` để lấy thông tin về
#   - Sử dụng RAG để có kết quả trả lời đúng.
import chromadb
from chromadb.utils import embedding_functions
from wikipediaapi import Wikipedia
from openai import OpenAI
import os
from dotenv import load_dotenv
import inspect
from pydantic import TypeAdapter
import json

# Load biến môi trường từ .env
load_dotenv()
# BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
client_ai = OpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=API_KEY
)

COLLECTION_NAME = "wiki_data"
client = chromadb.PersistentClient(path="./data")
client.heartbeat()
embedding_function = embedding_functions.DefaultEmbeddingFunction()
try:
    # Thử lấy collection nếu đã tồn tại
    collection = client.get_collection(COLLECTION_NAME)
except Exception as e:
    # Nếu collection không tồn tại, tạo mới
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_function)
# client = chromadb.PersistentClient(path="./data")
# client.heartbeat()
#
# embedding_function = embedding_functions.DefaultEmbeddingFunction()
# collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_function)
def get_wiki(page: str):
    """
    A function that retrieves content from a specified Wikipedia page. Given a page title, it returns the full text of
    the article in English. This tool helps extract information from Wikipedia for research, summarization,
    or knowledge retrieval tasks.
    :param page: trang thong tin tu wiki
    :return: noi dung duoc lay tu wiki
    """
    wiki = Wikipedia('HocCodeAI/0.0 (https://hoccodeai.com)', 'en')
    doc = wiki.page(page)
    if not doc.exists():
        return "This page dose not exit"
    return doc.text

# print(doc)
def add_vectorDB(doc: str):
    paragraphs = doc.split('\n\n')
    for index, paragraph in enumerate(paragraphs):
        collection.add(documents=[paragraph], ids=[str(index)])


get_wiki_function = {
    "name": "get_wiki",
    "description": inspect.getdoc(get_wiki),
    "parameters": TypeAdapter(get_wiki).json_schema()
}
tools = [
    {
        "type": "function",
        "function": get_wiki_function
    }
]

def get_completion(messages):
    response = client_ai.chat.completions.create(
        model='qwen-2.5-32b',
        messages=messages,
        tools=tools,
    )
    return response
messages = [{
    "role": "system",
    "content": "You are required to always use the provided Wikipedia tool to retrieve factual information for any questions "
               "that require it. "
               "Do not rely solely on internal knowledge; "
               "always invoke the tool to ensure the answer is up-to-date and accurate."
}]
while True:
    query = input("User: ")
    if query == "thoát":
        break

    messages.append({
        "role": "user",
        "content": query
    })

    response = client_ai.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=messages,

        tools=tools,
    )
    print(response.choices[0].message)

    if response.choices[0].message.content is not None:
        bot_message = response.choices[0].message.content
    else:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "get_wiki":
            arguments = json.loads(tool_call.function.arguments)
            data = get_wiki(arguments.get("page"))
        # print(data)
        add_vectorDB(data)
        q = collection.query(query_texts=[query], n_results=3)
        CONTEXT = q["documents"][0]
        prompt = f"""
        Use the following CONTEXT to answer the QUESTION at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use an unbiased and journalistic tone.
        CONTEXT: {CONTEXT}
        QUESTION: {query}
        """
        messages.append(response.choices[0].message)
        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        response = client_ai.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,

        )
        bot_message = response.choices[0].message.content
    print(f"BOT: {bot_message}")
    messages.append({
        "role": "assistant",
        "content": bot_message
    })
