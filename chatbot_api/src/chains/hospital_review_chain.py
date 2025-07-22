# import os
# from langchain.vectorstores.neo4j_vector import Neo4jVector
# from langchain.chains import RetrievalQA
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain.prompts import (
#     PromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     ChatPromptTemplate,
# )

import os
# from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

# HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")

# from dotenv import load_dotenv
# load_dotenv()

HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# HOSPITAL_QA_MODEL = load_dotenv("HOSPITAL_QA_MODEL")
print("HOSPITAL_QA_MODEL : {}\nNeo4j_URI : {}".format(HOSPITAL_QA_MODEL, NEO4J_URI))
print("OPENAI_API_KEY : {}".format(OPENAI_API_KEY))

# import httpx

# # Create a custom HTTP client with proxies
# http_client = httpx.Client(
#     proxies={
#         "http://": "http://localhost:8000",
#         "https://": "http://localhost:8000"
#     }
# )


import httpx

# # Create a transport with proxies
# transport = httpx.HTTPTransport(
#     proxy=httpx.Proxy(
#         url="http://your-proxy-url:port",
#         mode="TUNNEL_ONLY"  # or "FORWARD_ONLY" depending on your needs
#     )
# )

# # Initialize the client with the transport
# http_client = httpx.Client(transport=transport)

# os.environ["HTTP_PROXY"] = "http://34.124.169.171:7687"
# os.environ["HTTPS_PROXY"] = "http://34.124.169.171:7687"


neo4j_vector_index = Neo4jVector.from_existing_graph(
    url = NEO4J_URI, 
    username= NEO4J_USERNAME, 
    password = NEO4J_PASSWORD,
    index_name = "review", ## name given to vector_index
    node_label = "Review",  ## node to create embedding for
    text_node_properties= [  ## node properties to include in the embedding
        "physician_name",
        "patient_name",
        "text",
        "hospital_name",
    ],
    embedding=OpenAIEmbeddings(),  ##OPENAI_API_KEY=OPENAI_API_KEY, http_client=http_client
    embedding_node_property = "embedding",  ## embedding node property
    )

review_template = """
Your job is to use patient reviews to answer questions about their experience at a hospital. Use the following context to answer question. 
Be as detailed as possible, but don't make up any information that's not from the context. If you don't know teh answer, say you don't know

{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variable = ['context'], template = review_template)
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variable = ['question'], template = "{question}")
)

messages = [review_system_prompt, review_human_prompt]

review_prompt = ChatPromptTemplate(
    input_variable = ['context', 'question'],
    messages = messages,
)

reviews_vector_chain = RetrievalQA.from_chain_type(
    llm = ChatOpenAI(model = HOSPITAL_QA_MODEL, temperature = 0),
    chain_type = "stuff",   ## passing all retriever data to the LLM 
    retriever = neo4j_vector_index.as_retriever(k=12),
)

reviews_vector_chain.combine_documents_chain.llm_chain.prompt = review_prompt
