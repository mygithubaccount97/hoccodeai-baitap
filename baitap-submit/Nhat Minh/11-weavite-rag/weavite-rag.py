import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization
import pandas as pd
import gradio as gr

# Tải API key từ file .env
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Kết nối tới Weaviate
vector_db_client = weaviate.connect_to_local()
print("DB is ready: {}".format(vector_db_client.is_ready()))

COLLECTION_NAME = "BookCollectionRAG"

# Hàm tạo collection
def create_collection():
    book_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        generative_config=Configure.Generative.ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="llama3.2",
        ),
        properties=[
            Property(name="title", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="author", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="description", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="grade", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="genre", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="excerpt", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="data", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="intro", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="lexile", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="path", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="is_prose", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="license", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="notes", data_type=DataType.TEXT, skip_vectorization=True),
        ]
    )
    # Đọc dữ liệu từ file CSV
    data = pd.read_csv('commonlit_texts.csv')
    sent_to_vector_db = data.astype(str).to_dict(orient='records')
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB. Total records: {total_records}")

    # Import dữ liệu vào DB theo batch
    with book_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)
    print("Data saved to Vector DB")

# Kiểm tra và tạo collection nếu chưa tồn tại
if vector_db_client.collections.exists(COLLECTION_NAME):
    print("Collection {} already exists".format(COLLECTION_NAME))
else:
    create_collection()

# Hàm tìm kiếm sách
def search_book(query):
    books = vector_db_client.collections.get(COLLECTION_NAME)
    response = books.generate.near_text(
        query=query,
        single_prompt="Viết một bài giới thiệu ngắn gọn bằng tiếng Việt về sách: {title}, tác giả: {author}, thể loại: {genre}, trích đoạn: {excerpt}",
        limit=3
    )
    
    # Định dạng kết quả bằng Markdown
    result = ""
    for book in response.objects:
        title = book.properties['title']
        author = book.properties['author']
        genre = book.properties['genre']
        generated_intro = book.generated
        result += f"### {title}\n"
        result += f"- **Tác giả**: {author}\n"
        result += f"- **Thể loại**: {genre}\n"
        result += f"- **Giới thiệu**: {generated_intro}\n\n"
    
    # Xử lý trường hợp không tìm thấy sách
    if not result:
        result = "Không tìm thấy sách phù hợp với truy vấn của bạn."
    
    return result

# Giao diện Gradio
with gr.Blocks() as interface:
    # Tiêu đề và mô tả
    gr.Markdown("# TÌM KIẾM SÁCH")
    gr.Markdown("Nhập tên, tác giả, mô tả hoặc thể loại để tìm kiếm sách và nhận gợi ý.")
    
    # Sắp xếp trường nhập và nút tìm kiếm
    with gr.Row():
        query = gr.Textbox(label="Tìm kiếm sách", placeholder="Ví dụ: tình yêu, phiêu lưu, tác giả cụ thể...")
        search = gr.Button("Tìm kiếm")
    
    # Khu vực hiển thị kết quả
    result = gr.Markdown(label="Kết quả tìm kiếm")
    
    # Kết nối hàm search_book với giao diện
    search.click(fn=search_book, inputs=query, outputs=result)

# Khởi chạy giao diện
interface.launch()

# Đóng kết nối Weaviate
vector_db_client.close()