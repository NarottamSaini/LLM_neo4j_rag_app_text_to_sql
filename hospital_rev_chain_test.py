import dotenv
dotenv.load_dotenv()
from chatbot_api.src.chains.hospital_review_chain import review_vector_chain

query = """
What have patient said about hospital efficiency?
Mention details from the specific reviews.
"""

response = review_vector_chain.invoke(query)
print("response.get('result') : ",response.get('result'))