
from langchain.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from chatbot import review_chain
import dotenv

dotenv.load_dotenv()

context = "I had a great stay!"
question = "Did anyone have a positive experience?"

# review_chain.invoke({"context": context, "question": question})
print(review_chain.invoke({"context": context, "question": question}))
