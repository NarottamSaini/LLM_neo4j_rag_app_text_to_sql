import dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings

REVIEW_CSV_PATH = "data/reviews.csv"
REVIEW_CHROMA_PATH = "chroma_data"

dotenv.load_dotenv()

loader = CSVLoader(file_path=REVIEW_CSV_PATH, source_column="review")
reviews = loader.load()

reviews_vector_db = Chroma.from_documents(reviews, OpenAIEmbeddings(), persist_directory = REVIEW_CHROMA_PATH)

questions = """ Has anyone complained about the 
                communication with the hospital staff"""

relevant_docs = reviews_vector_db.similarity_search(questions, k=3)
print("relevant_docs : \n", relevant_docs)

print("relevant_docs : \n", relevant_docs[0].page_content)
print("relevant_docs : \n", relevant_docs[1].page_content)
print("relevant_docs : \n", relevant_docs[2].page_content)
