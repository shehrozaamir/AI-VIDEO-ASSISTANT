#ACTIONALABLE ITEMS , DECISIONS, QUESTIONS

from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence,RunnableParallel,RunnableLambda,RunnablePassthrough
from dotenv import load_dotenv
import os
load_dotenv()

model = init_chat_model("mistral-small-latest", model_provider="mistralai", temperature=1, max_tokens=2048, mistral_api_key=os.getenv("MISTRAL_API_KEY"))
#system prompt yani har cheez ka alag prompt actionitems ka decisions ka questions ka
def build_chain(system_prompt:str) :
    return (RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | ChatPromptTemplate.from_messages([("system", system_prompt),("user", "Please respond to the following: {text}")]) | model | StrOutputParser())

def extract_action_items(full_transcribe):
    system_prompt="""You are an expert meeting analyst. Read the provided meeting transcript (full_transcribe) carefully and extract all actionable items from it.

For each actionable item, include:
- Task description
- Owner (person responsible, if mentioned; else write "Unassigned")
- Deadline (if mentioned; else write "Not specified")

Format the output as a numbered list, like this:
1. Task: <task description> | Owner: <owner> | Deadline: <deadline>
2. Task: <task description> | Owner: <owner> | Deadline: <deadline>

Rules:
- Only extract tasks that are explicitly stated or clearly implied in the transcript. Do not make up information.
- If no actionable items are found in the transcript, respond with exactly: "No action items found."
- Do not add any extra commentary, headers, or explanation — output only the numbered list (or the no-items message).
"""
    chain=build_chain(system_prompt)
    return chain.invoke(full_transcribe)


def extract_decisions(full_transcribe):
    system_prompt2="""


You are an expert meeting analyst. Read the provided meeting transcript (full_transcribe) carefully and extract all key decisions made during the meeting.

For each decision, include:
- Decision description
- Context/reason (if mentioned; else write "Not specified")

Format the output as a numbered list, like this:
1. Decision: <decision description> | Context: <context/reason>
2. Decision: <decision description> | Context: <context/reason>

Rules:
- Only extract decisions that are explicitly stated or clearly implied in the transcript. Do not make up information.
- If no decisions are found in the transcript, respond with exactly: "No decisions found."
- Do not add any extra commentary, headers, or explanation — output only the numbered list (or the no-decisions message).
"""
    chain=build_chain(system_prompt2)
    return chain.invoke(full_transcribe)

def extract_questions(full_transcribe):
    system_prompt3="""You are an expert meeting analyst. Read the provided meeting transcript (full_transcribe) carefully and extract all open questions or unresolved issues raised during the meeting.

For each question, include:
- Question description
- Raised by (if mentioned; else write "Unspecified")

Format the output as a numbered list, like this:
1. Question: <question description> | Raised by: <person>
2. Question: <question description> | Raised by: <person>

Rules:
- Only extract questions that are explicitly stated or clearly implied in the transcript. Do not make up information.
- If no open questions are found in the transcript, respond with exactly: "No questions found."
- Do not add any extra commentary, headers, or explanation — output only the numbered list (or the no-questions message)."""
    chain=build_chain(system_prompt3)
    return chain.invoke(full_transcribe)
