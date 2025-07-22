
# from langchain_intro.chatbot import chat_model
from chatbot import chat_model
from langchain.schema.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content = '''You're an assistant knowledgeable about
                  healthcare. Only answer healthcare-related questions.
    '''),
    HumanMessage(content = '''
                 What is Medicaid managed care?
    ''')
]

response = chat_model.invoke(messages)
print("response : \n ", response.content)