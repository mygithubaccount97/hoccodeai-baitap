import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key='gsk_xxx',
)
while True:
    user_question = input("USER: ")
    complete = client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":"bạn là một trợ lý thông minh, hãy đưa ra câu trả lời ngắn gọn"
            },
            {
                "role":"user",
                "content":user_question,
            },
        ],
        model="gemma2-9b-it",
        temperature=0.6,
        max_tokens=500
    )
    print(complete.choices[0].message.content)
