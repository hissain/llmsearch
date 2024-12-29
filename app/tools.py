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
        "You are an assistant tasked with creating IEEE styled references for citation from provided publications. "
        "Now, please generate IEEE bibliography styled references for the following publications.\n\n"
        "Publications: {publications}"
    )

    prompt = PromptTemplate.from_template(prompt_extract)
    chain = prompt | llm
    processed_chunks = []
    chunks = chunkify(publications, 2000)
    for chunk in chunks:
        result = chain.invoke({"publications": chunk})
        processed_chunks.append(result.content)

    return "\n".join(processed_chunks)

# Tool setup
tools = [
    Tool(
        name="Semantic Scholar Search",
        func=semantic_scholar.run,
        description="Useful for retrieving academic references, citations, and publications.",
    ),
    Tool(
        name="Reference Creator",
        description="Create IEEE conventional reference for citation from a list of academic publications.",
        func=create_reference
    )
]
