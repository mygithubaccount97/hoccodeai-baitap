import os
from openai import OpenAI


client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key='gsk_xxx',
)
prompt = input("ỨNG DỤNG AI VIẾT CODE PYTHON\nNhập yêu cầu của bạn:\n ")

messages = [
    {
        "role": "system",
        "content": "Bạn là một lập trình viên chuyên nghiêp. Hãy viết chương trình theo yêu cầu bằng ngôn ngữ PYTHON. chỉ đưa ra code hoàn chỉnh, không giải thích gì thêm."
    },
    {
        "role": "user",
        "content": prompt
    }
]
complete = client.chat.completions.create(
    messages=messages,
    model="gemma2-9b-it",
    temperature=0.3,
    max_tokens=1024,
)
print(complete.choices[0].message.content)



