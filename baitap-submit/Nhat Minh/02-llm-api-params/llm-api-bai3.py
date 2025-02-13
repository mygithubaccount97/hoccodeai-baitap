import os
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

#lấy thông tin từ web

url = input("NHẬP ĐƯỜNG LINK VÀO ĐÂY: ")
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    main_detail = soup.find("div", id="main-detail")
    if main_detail:
        text_content = main_detail.get_text(strip=True)
    else:
        print("Không tìm thấy nội dung")
else:
    print("Lỗi:", response.status_code)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key='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',
)
chat_history = [
    {
        "role": "system",
        "content": "bạn là một AI tóm tắt nội dung từ trang WEB. Hãy trả lời chỉ dựa trên nội dung trang WEB."

    },

    {
        "role": "user",
        "content": text_content,
    },
    {
        "role": "user",
        "content": "hãy tóm tắt nội dung phía trên. "
                   "Trình bày với định dạng như sau: tiều đề viết hoa; nội dung chính (viết thành từng đoạn văn);ghi rõ nguồn cung cấp thông tin và đường link đẫn với bài viết.",
    },
]

answer = client.chat.completions.create(
    messages=chat_history,
    model="gemma2-9b-it",
    temperature=0.5,
    max_tokens=500
)
chat_history.append({
    "role": "assistant",
    "content": answer.choices[0].message.content
})
print("Assistant: ", answer.choices[0].message.content)

