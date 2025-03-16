# Viết code để tìm kiếm sách/query từ Weavite
# Import các thư viện cần thiết

import weaviate
import gradio as gr



# Khởi tạo Weaviate và kết nối
vector_db_client = weaviate.connect_to_local()

vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))



COLLECTION_NAME = "BookCollection"


def search_book(query):
    book_collection = vector_db_client.collections.get(COLLECTION_NAME)
    # TÌM KIẾM THEO NGỮ NGHĨA + TỪ KHÓA
    response = book_collection.query.hybrid(
        query=query, alpha=0.5, limit=5
    )
    results = []
    for book in response.objects:
        title = book.properties['title'].upper()
        author = book.properties['author']
        genre = book.properties['genre']
        description = book.properties['description']

        text = f"**{title}**\n- Thể loại: {genre}\n- Tác giả: {author}\n- Mô tả: {description}"
        results.append(text)
    return "\n\n".join(results) if results else "Không tìm thấy kết quả phù hợp"

# TẠO GIAO DIỆN VỚI GRADIO
with gr.Blocks(title="TÌM KIẾM SÁCH") as interface:
    query = gr.Textbox(label="Tìm kiếm sách", placeholder="Tên, tác giả, mô tả, thể loại...")
    search = gr.Button(value="Search")
    result = gr.Markdown(label="KẾT QUẢ")
    search.click(fn=search_book, inputs=query, outputs=result)
interface.queue().launch()

# Đóng kết nối
vector_db_client.close()