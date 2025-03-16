# Viết code để insert dữ liệu vào Weavite
import pandas as pd
import weaviate
from weaviate.embedded import EmbeddedOptions
from weaviate.classes.config import Configure, Property, DataType, Tokenization

vector_db_client = weaviate.connect_to_local()

vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

# Cấu hình tên collection
COLLECTION_NAME = "BookCollection"

def create_collection():
    # Tạo schema cho collection
    book_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        # Sử dụng model transformers để tạo vector
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        properties=[
            # Tiêu đề phim: text, được vector hóa và chuyển thành chữ thường
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

    # Chuyển đổi dữ liệu để import
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

vector_db_client.close()