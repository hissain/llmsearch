import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import os
from dotenv import load_dotenv

load_dotenv()

# Ensure this is set globally
os.environ["UVLOOP_DISABLE"] = "1"

# Configuration for external APIs
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

import streamlit as st
import time

# Import necessary modules from LangChain and related libraries
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools.semanticscholar.tool import SemanticScholarAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Configuration ---
# Replace with your actual API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# --- Utility Functions ---
def chunkify(text: str, chunk_size: int):
    """Splits text into chunks of a maximum specified length."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

# --- Initialize Components ---
# Semantic Scholar API wrapper
semantic_scholar = SemanticScholarAPIWrapper()

# LLM instance
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GEMINI_API_KEY,
    temperature=0.1
)

def create_reference(publications: str) -> str:
    """
    Extract standard BibTeX styled references from the provided publications.
    It chunks the publications if necessary and processes each chunk.
    """
    prompt_extract = (
        "You are an assistant tasked with extracting standard BibTeX styled references for citation from provided publications or publication references. "
        "Perform your task for following publications,\n\n"
        "Publications: {publications}"
    )
    prompt = PromptTemplate.from_template(prompt_extract)
    # Create a chain from the prompt and llm using the pipeline operator
    chain = prompt | llm
    processed_chunks = []
    for chunk in chunkify(publications, 3000):
        result = chain.invoke({"publications": chunk})
        processed_chunks.append(result.content)
    return "\n".join(processed_chunks)

# Setup tools for the agent
tools = [
    Tool(
        name="Semantic Scholar Search",
        func=semantic_scholar.run,
        description="Useful for retrieving academic references, citations for publications in BibTeX style.",
    ),
    Tool(
        name="Reference Extractor",
        description="Extract standard BibTeX styled reference from given publications or publication references.",
        func=create_reference,
    )
]

# Initialize the agent with the defined tools and LLM
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    max_iterations=3,
    handle_parsing_errors=True,
    verbose=True,
)

# --- Streamlit App ---
def main():
    st.title("Research References Chatbot")
    st.write("Enter a research topic to get academic references.")

    # Input form for research title
    with st.form(key="research_form"):
        title = st.text_input("Research Title", "")
        submit_button = st.form_submit_button("Get References")

    # Container for logging steps
    log_placeholder = st.empty()
    logs = []

    def update_logs(message: str):
        logs.append(message)
        # Update the log display (using markdown for line breaks)
        log_placeholder.markdown("\n".join(logs))

    if submit_button and title:
        update_logs("**Starting agentic search for references...**")
        query = f"Find related publications for: {title}. Then create references from the publications found."
        update_logs(f"**Query:** {query}")
        
        with st.spinner("Fetching references..."):
            try:
                # Run the agent; no prior chat history is maintained here.
                response_text = agent.run(input=query, chat_history=[])
                update_logs("**Agent returned the following references:**")
                update_logs(response_text)
            except Exception as e:
                update_logs(f"**An error occurred:** {e}")
                response_text = ""

        st.subheader("References Output")
        st.text_area("References", value=response_text, height=300)

if __name__ == "__main__":
    main()
