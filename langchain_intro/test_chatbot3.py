
from chatbot import hospital_agent_executor,review_chain

# hospital_agent_executor.invoke({"input":"what is the wait time at hospital C"})
# hospital_agent_executor.invoke({"input":"what patient said about teh comfort level at the hospital"})

input_msg = ["what is the wait time at hospital C", "what patient said about the comfort level at the hospital"]

for i in range(len(input_msg)):
    hospital_agent_executor.invoke({"input":input_msg[i]})