
import time
import requests

CHATBOT_URL = "http://localhost:8000/hospital-rag-agent"

questions = [
    "what is the current wait time at hospital Brown Inc",
    "what is the current wait time at hospital Burke, Griffin and Cooper",
    "At which hospital patients are complaining about the billing and insurance issues ?",
    "Which hospital has the shortest wait time",
    "What is average duration in days for emergency visits ?",
    # "What are patients saying about the nursing staff at Richardson-Powell",
    # "What was the total billing amount charged toeach payer for 2023",
    # "What is the average billing amount for Medicaid visits?",
    # "Total number of patient treated by Cory Campbell",
    # "What was the total billing amount for patient 1337",
    # "What was the total billing amount for patient 1340",
    # "which physician billed the most to insurer Cigna ?",
    # "which state had the largest percent increase in Medicaid visits from 2022 to 2023"

]


request_bodies = [{'text':q} for q in questions]

print("request_bodies : ", request_bodies)

start_time = time.perf_counter()

outputs = [requests.post(CHATBOT_URL, json=data) for data in request_bodies]

for i, output in enumerate(outputs):
    print(f"Question : {questions[i]}")
    print(f"Answer : {output.json()['output']}")
    print(f"Intermediate Steps : {output.json()['intermediate_steps']}")
    print("\n")

print("outputs : ", outputs)

end_time = time.perf_counter()

print(f"Run time : {end_time -start_time} seconds")

