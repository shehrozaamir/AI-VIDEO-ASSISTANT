from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence,RunnableParallel,RunnableLambda,RunnablePassthrough
import os
from dotenv import load_dotenv
load_dotenv()
model = init_chat_model("mistral-small-latest", model_provider="mistralai", temperature=1, max_tokens=2048, mistral_api_key=os.getenv("MISTRAL_API_KEY"))
def text_splitter(full_transcribe):
    text= RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    return text.split_text(full_transcribe)

def prompt_template(full_transcribe):
    llm=model
    prompt= ChatPromptTemplate.from_messages([
        ("system", "You are an ai  assistant which help to summarize the video's transcription in simple words"),
        ("user", "Please summarize the following text: {text}")
    ])
    
    
    chain=prompt | llm | StrOutputParser()
    split_text=text_splitter(full_transcribe)
    summaries=[chain.invoke({"text": chunk}) for chunk in split_text]
    combined=" ".join(summaries)
    combined_prompt=ChatPromptTemplate.from_messages([
        ("system", "You are expert meeting summarizer combine these partial summaries into a final professional summary in bullet points"),
        ("user",  "{summaries}")
    ])
    combined_chain=(
        #RunnablePassthrough: is mein humne combined ko pass kar diya 
        RunnablePassthrough() | RunnableLambda(lambda x: {"summaries": combined}) | combined_prompt | llm | StrOutputParser()
    )
    return combined_chain.invoke(combined)



def build_title(full_transcribe):
    llm=model
    title_chain=(
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": full_transcribe}) | ChatPromptTemplate.from_messages([
            ("system", "You are an ai assistant which help to generate a title for the given text"),
            ("user", "Please generate a title for the following text: {text}")
        ]) | llm | StrOutputParser()
    )
    return title_chain.invoke({"text": full_transcribe[:2000]})




