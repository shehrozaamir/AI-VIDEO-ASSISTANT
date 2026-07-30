from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import  TokenTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
import os
import shutil
from dotenv import load_dotenv
load_dotenv()

    
    
# rag.py
def build_rag_pipeline(full_transcript):
    documents = [Document(page_content=full_transcript)]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    texts = text_splitter.split_documents(documents)

    if os.path.exists("chroma-db"):
        shutil.rmtree("chroma-db")

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
    model = init_chat_model("mistral-small-latest", model_provider="mistralai", temperature=1, max_tokens=2048, mistral_api_key=os.getenv("MISTRAL_API_KEY"))

    vectorstore = Chroma.from_documents(documents=texts, embedding=embedding_model, persist_directory="chroma-db")
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(search_type="mmr"), llm=model
    )

    prompt = ChatPromptTemplate.from_messages([(
                "system",
                """You are an expert meeting assistant. Answer the user's question based ONLY on the meeting transcript context provided below.
    
    If the answer is not found in the context, say:
    "I could not find this information in the meeting transcript."
    
    Always be concise and precise. If quoting someone, mention it clearly.
    
    Context from meeting transcript:
    {context}""",
            ),
            ("human", "{question}")])  # same as before

    return multi_query_retriever, prompt, model


def ask_question(query, multi_query_retriever, prompt, model):
    docs = multi_query_retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    final_prompt = prompt.invoke({"context": context, "question": query})
    response = model.invoke(final_prompt)
    return response.content


