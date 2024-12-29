# tools.py

from langchain.agents import Tool
from langchain_community.tools.semanticscholar.tool import SemanticScholarAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY
from utils import chunkify

# Initialize Semantic Scholar API
semantic_scholar = SemanticScholarAPIWrapper()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GEMINI_API_KEY,
    temperature=0.1
)

# Reference creation function
def create_reference(publications: str) -> str:
    prompt_extract = (
        "You are an assistant tasked with extracting standard BibTeX styled references for citation from provided publications or publication references. "
        "Perform your task for following publications,\n\n"
        "Publications: {publications}"
    )

    prompt = PromptTemplate.from_template(prompt_extract)
    chain = prompt | llm
    processed_chunks = []
    chunks = chunkify(publications, 3000)
    for chunk in chunks:
        result = chain.invoke({"publications": chunk})
        processed_chunks.append(result.content)

    return "\n".join(processed_chunks)

# Tool setup
tools = [
    Tool(
        name="Semantic Scholar Search",
        func=semantic_scholar.run,
        description="Useful for retrieving academic references, citations for publications in BibTeX style.",
    ),
    Tool(
        name="Reference Extractor",
        description="Extract standard BibTeX styled reference from given publications or publication references.",
        func=create_reference
    )
]
