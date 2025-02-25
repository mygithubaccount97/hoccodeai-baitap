import inspect
from pprint import pprint
import json
from openai import OpenAI
from pydantic import TypeAdapter
from dotenv import load_dotenv
import requests
# Implement 3 hàm

# Load biến môi trường từ .env
load_dotenv()
# BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
JINA_API_KEY = os.getenv('JINA_API_KEY')

def get_current_weather(location: str, unit: str):
    """
    Get current weather in a given location
    :param location: The city name
    :param unit: The unit temperature
    :return: the current temperature in a given location
    """
    # Hardcoded response for demo purposes
    return "Trời rét vãi nôi, 7 độ C"


def get_stock_price(symbol: str):
    # Không làm gì cả, để hàm trống
    """
    xem gia
    :param symbol:
    :return:
    """
    pass


# Bài 2: Implement hàm `view_website`, sử dụng `requests` và JinaAI để đọc markdown từ URL
def view_website(url: str):
    # Không làm gì cả, để hàm trống
    """
    View a website
    :param url: website address
    :return: content of the website
    """
    headers = {
        'Authorization': JINA_API_KEY
    }
    url_base = 'https://r.jina.ai/' + url
    response = requests.get(url_base, headers=headers)
    return response.text



# Bài 1: Thay vì tự viết object `tools`, hãy xem lại bài trước, sửa code và dùng `inspect` và `TypeAdapter` để define `tools`
get_weather_function = {
    "name": "get_weather",
    "description": inspect.getdoc(get_weather),
    "parameters": TypeAdapter(get_weather).json_schema(),
}
view_website_function = {
    "name": "view_website",
    "description": inspect.getdoc(view_website),
    "parameters": TypeAdapter(view_website).json_schema(),
}
get_stock_price_function = {
    "name": "get_stock_price",
    "description": inspect.getdoc(get_stock_price),
    "parameters": TypeAdapter(get_stock_price).json_schema(),
}
tools = [
    {
        "type": "function",
        "function": get_weather_function
    },
    {
        "type": "function",
        "function": view_website_function
    },
    {
        "type": "function",
        "function": get_stock_price()
    }
]

# https://platform.openai.com/api-keys

client = OpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=API_KEY,
)
COMPLETION_MODEL = "gpt-4o-mini"

messages = [{"role": "user", "content": "Thời tiết ở Hà Nội hôm nay thế nào?"}]

print("Bước 1: Gửi message lên cho LLM")
pprint(messages)

response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages,
    tools=tools
)

print("Bước 2: LLM đọc và phân tích ngữ cảnh LLM")
pprint(response)

print("Bước 3: Lấy kết quả từ LLM")
tool_call = response.choices[0].message.tool_calls[0]

pprint(tool_call)
arguments = json.loads(tool_call.function.arguments)

print("Bước 4: Chạy function get_current_weather ở máy mình")

if tool_call.function.name == 'get_current_weather':
    result = get_current_weather(
        arguments.get('location'), arguments.get('unit'))
    # Hoặc code này cũng tương tự
    # weather_result = get_current_weather(**arguments)
elif tool_call.function.name == 'view_website':
    result = view_website(arguments.get('url'))
print(f"Kết quả bước 4: {result}")
print("Bước 5: Gửi kết quả lên cho LLM")
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "content": result,
    "tool_call_id": tool_call.id
})

pprint(messages)

final_response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages
    # Ở đây không có tools cũng không sao, vì ta không cần gọi nữa
)
print(
    f"Kết quả cuối cùng từ LLM: {final_response.choices[0].message.content}.")


