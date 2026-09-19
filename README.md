# AI Video Assistant

A Streamlit app that takes a YouTube link and turns it into a transcript, a summary, action items, key decisions, and open questions — then lets you ask follow-up questions about the video like a chatbot.

Built this mainly for meeting/lecture recordings where you don't want to sit through the whole video again just to find one thing that was said.

## How it works

1. **Audio processing** – downloads the audio from the YouTube link (`yt-dlp`), converts it to mono 16kHz WAV, and splits it into 10-minute chunks so it's manageable to transcribe.
2. **Transcription** – each chunk is transcribed with either:
   - **Whisper** (runs locally) for English audio
   - **Sarvam AI's** speech-to-text-translate API for Hinglish audio (it translates while transcribing, and the API only accepts clips under 30s, so chunks get sliced further before sending)
3. **Summary & title** – the full transcript is split into pieces, each piece gets summarized, and then those partial summaries get combined into one final bullet-point summary. A title is generated separately.
4. **Extraction** – three separate LLM calls pull out action items, decisions, and open questions from the transcript, each with owner/context/deadline where mentioned.
5. **Q&A (RAG)** – the transcript is chunked, embedded, and stored in a Chroma vector store. Questions you ask get run through a multi-query retriever so you get relevant context back before the model answers.

All of this is wired into a Streamlit UI (`test.py`) — paste a link, pick the language, hit process, and everything shows up in tabs.

## Tech used

- [Streamlit](https://streamlit.io/) for the UI
- `yt-dlp` + `pydub` for downloading and processing audio
- [OpenAI Whisper](https://github.com/openai/whisper) for English transcription
- [Sarvam AI](https://sarvam.ai/) for Hinglish transcription/translation
- [LangChain](https://www.langchain.com/) for all the LLM chains (summary, extraction, RAG)
- Mistral's `mistral-small-latest` model for the LLM calls
- `sentence-transformers` (all-MiniLM-L6-v2) + Chroma for embeddings and vector storage

## Setup

1. Install dependencies:
   ```bash
   pip install streamlit yt-dlp pydub openai-whisper requests langchain langchain-community langchain-huggingface langchain-classic langchain-text-splitters sentence-transformers scikit-learn chromadb python-dotenv
   ```
2. Make sure `ffmpeg` is installed on your system (needed by both `yt-dlp` and `pydub`).
3. Create a `.env` file in the project root:
   ```
   MISTRAL_API_KEY=your_key_here
   ```
4. If you plan to use Hinglish transcription, open `transcriber.py` and paste your Sarvam API key where it says `SARVAM_API_KEY = "YOUR_SARVAM_API_KEY_HERE"`.

## Usage

Run the app with:
```bash
streamlit run test.py
```
Paste a YouTube URL, pick English or Hinglish, and click "Process Video." Once it's done, you'll see the summary, action items, questions, and decisions in separate tabs, plus a chat box at the bottom to ask anything else about the video.

## Notes

- This was built as a final year project to explore combining speech-to-text, LLM chains, and RAG in one pipeline.
- The Sarvam API key is currently hardcoded in `transcriber.py` instead of using `.env` — worth moving that over at some point.
- Processing time depends heavily on video length since Whisper runs locally.

## Author

Built by Shehroz — BSCS student, learning GenAI and agentic AI by building small projects like this one.
