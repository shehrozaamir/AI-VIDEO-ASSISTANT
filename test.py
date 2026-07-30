# from audio_processor import process_input      # audio download/chunking wala function
# from transcriber import transcribe_all
# from summarizer import build_title, prompt_template
# from extractor import extract_questions, extract_decisions, extract_action_items
# from rag_engine import build_rag_pipeline, ask_question


# SOURCE = "https://www.youtube.com/watch?v=f84XbvASkk4"
# LANGUAGE = "english"   # ya "hinglish" agar Hinglish audio hai


# def section(title):
#     print("\n" + "=" * 50)
#     print(title)
#     print("=" * 50)

 
# # Step 1: Audio -> Chunks
# chunks = process_input(SOURCE)

# # Step 2: Transcription
# full_transcript = transcribe_all(chunks, language=LANGUAGE)
# section("FULL TRANSCRIPT")
# print(full_transcript)

# # Step 3: Title & Summary
# title = build_title(full_transcript)
# section("GENERATED TITLE")
# print(title)

# summary = prompt_template(full_transcript)
# section("GENERATED SUMMARY")
# print(summary)

# # Step 4: Extraction
# action_items = extract_action_items(full_transcript)
# section("EXTRACTED ACTION ITEMS")
# print(action_items)

# questions = extract_questions(full_transcript)
# section("EXTRACTED QUESTIONS")
# print(questions)

# decisions = extract_decisions(full_transcript)
# section("EXTRACTED DECISIONS")
# print(decisions)



# retriever, prompt, model = build_rag_pipeline(full_transcript)

# while True:
#     query = input("Enter query (0 to exit): ")
#     if query.strip() == "0":
#         break
#     print(ask_question(query, retriever, prompt, model))
    
    
    
#ADDING FRONTED USING AI
import streamlit as st

from audio_processor import process_input
from transcriber import transcribe_all
from summarizer import build_title, prompt_template
from qa_extractor import extract_questions, extract_decisions, extract_action_items
from rag_engine import build_rag_pipeline, ask_question
import os
from dotenv import load_dotenv
load_dotenv()


st.set_page_config(page_title="YouTube AI Summarizer", layout="wide")

st.title("🎥 YouTube Video Summarizer & Q&A")
st.caption("Paste a YouTube link → get transcript, summary, action items, and ask questions about it.")

# --- Session state to persist data across reruns ---
if "processed" not in st.session_state:
    st.session_state.processed = False

# --- Input section ---
col1, col2 = st.columns([3, 1])
with col1:
    source = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=f84XbvASkk4")
with col2:
    language = st.selectbox("Language", ["english", "hinglish"])

process_btn = st.button("Process Video", type="primary")

if process_btn and source:
    with st.spinner("Downloading & chunking audio..."):
        chunks = process_input(source)

    with st.spinner("Transcribing... (this can take a bit)"):
        full_transcript = transcribe_all(chunks, language=language)

    with st.spinner("Generating title & summary..."):
        title = build_title(full_transcript)
        summary = prompt_template(full_transcript)

    with st.spinner("Extracting action items, questions, decisions..."):
        action_items = extract_action_items(full_transcript)
        questions = extract_questions(full_transcript)
        decisions = extract_decisions(full_transcript)

    with st.spinner("Building RAG pipeline for Q&A..."):
        retriever, prompt, model = build_rag_pipeline(full_transcript)

    # Save everything to session state so it survives reruns (e.g. when asking questions)
    st.session_state.processed = True
    st.session_state.title = title
    st.session_state.full_transcript = full_transcript
    st.session_state.summary = summary
    st.session_state.action_items = action_items
    st.session_state.questions = questions
    st.session_state.decisions = decisions
    st.session_state.retriever = retriever
    st.session_state.prompt = prompt
    st.session_state.model = model

# --- Display results ---
if st.session_state.processed:
    st.header(st.session_state.title)

    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Action Items", "Questions", "Decisions"])

    with tab1:
        st.write(st.session_state.summary)

    with tab2:
        st.write(st.session_state.action_items)

    with tab3:
        st.write(st.session_state.questions)

    with tab4:
        st.write(st.session_state.decisions)

    with st.expander("Full Transcript"):
        st.write(st.session_state.full_transcript)

    st.divider()

    # --- Q&A section ---
    st.subheader("💬 Ask a question about this video")
    query = st.text_input("Your question", key="query_input")
    ask_btn = st.button("Get Answer")

    if ask_btn and query:
        with st.spinner("Thinking..."):
            answer = ask_question(
                query,
                st.session_state.retriever,
                st.session_state.prompt,
                st.session_state.model,
            )
        st.info(answer)

