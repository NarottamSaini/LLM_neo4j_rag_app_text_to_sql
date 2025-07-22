## For executing this file you need to be in folder: F:\learning\LLM_neo4j_rag_app\chatbot_api\src
import dotenv
dotenv.load_dotenv()

from agents.hospital_rag_agent import hospital_rag_agent_executor

response = hospital_rag_agent_executor.invoke(
{"input":"What is the wait time at Brown-Golden"}
)

response = hospital_rag_agent_executor.invoke(
{"input":"which hospital has highest waiting time"}
)

response = hospital_rag_agent_executor.invoke(
{"input":"what customer feedback has been recieved in overall comfort and overall quality of stay ."}
)

response = hospital_rag_agent_executor.invoke(
{"input":"Share all the details related to patient : Steven Bennett."}
)

response = hospital_rag_agent_executor.invoke(
{"input":"Which pysician has treated most patients covered by Cigna"}
)

response = hospital_rag_agent_executor.invoke(
{"input":"Query the graph database to get the review written by visit id: 7674"}
)

response = hospital_rag_agent_executor.invoke(
{"input":"show the review written by visit id: 7674"}
)

response = hospital_rag_agent_executor.invoke(
{"input":"Query the graph database to get the complete details regarding visit id: 7674 including the review shared by the patient."}
)

response = hospital_rag_agent_executor.invoke(
{"input":"Which physician treated the most patients covered by UnitedHealthcare"})

response.get("output")
