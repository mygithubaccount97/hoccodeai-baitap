import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key='gsk_xxx',
)
chat_history = []
while True:
    user_question = input("USER: ")
    chat_history.append({
        "role": "user",
        "content": user_question
    })
    answer = client.chat.completions.create(
        messages=chat_history,
        model="gemma2-9b-it",
        temperature=1,
        max_tokens=500
    )
    chat_history.append({
        "role": "assistant",
        "content": answer.choices[0].message.content
    })
    print(answer.choices[0].message.content)
