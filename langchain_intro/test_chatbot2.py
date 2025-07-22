
from chatbot import review_chain

question = """ 
            Has anyone complained about the communication with the hospital staff"""

response = review_chain.invoke(question)

print("response : \n", response)