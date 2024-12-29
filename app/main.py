from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
from langchain.agents import Tool
from langchain_community.tools.semanticscholar.tool import SemanticScholarAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType

load_dotenv()
os.environ["UVLOOP_DISABLE"] = "1"

# Initialize Semantic Scholar API
semantic_scholar = SemanticScholarAPIWrapper()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv('GEMINI_API_KEY'),
    temperature=0.1
)

# Define chunking function
def chunkify(text: str, max_length: int) -> list[str]:
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence) + 2
        if current_length + sentence_length > max_length:
            chunks.append(". ".join(current_chunk) + ".")
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")

    return chunks

# Define the reference creation function
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

# Initialize tools
tools = []
tools.append(
    Tool(
        name="Semantic Scholar Search",
        func=semantic_scholar.run,
        description="Useful for retrieving academic references, citations, and publications.",
    )
)
reference_tool = Tool(
    name="Reference Creator",
    description="Create IEEE conventional reference for citation from a list of academic publications.",
    func=create_reference
)
tools.append(reference_tool)

# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    max_iterations=3,
    handle_parsing_errors=True,
    verbose=True,
)

# FastAPI instance
app = FastAPI()

# Route to serve the homepage (HTML page with a form to input title)
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Research References Chatbot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    background-color: #ffffff;
                    padding: 40px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    width: 60%;
                    max-width: 600px;
                }
                h1 {
                    color: #333;
                    font-size: 32px;
                    margin-bottom: 20px;
                }
                input[type="text"] {
                    width: 70%;
                    padding: 12px;
                    margin-bottom: 20px;
                    border: 2px solid #ccc;
                    border-radius: 4px;
                    font-size: 18px;
                    box-sizing: border-box;
                }
                button {
                    padding: 12px 24px;
                    background-color: #0066cc;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    border-radius: 4px;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #0057a0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Research References Chatbot</h1>
                <form action="/get_references/" method="get">
                    <input type="text" name="title" placeholder="Enter Research Title" required>
                    <button type="submit">Get References</button>
                </form>
            </div>
        </body>
    </html>
    """

# Route to get references based on the title
@app.get("/get_references/", response_class=HTMLResponse)
async def get_references(title: str, request: Request):
    # Initialize chat history
    chat_history = []
    
    # Query the agent
    user_input = f"Find related publications for: {title}. Then create references from the publications found."
    response = agent.run(input=user_input, chat_history=chat_history)
    chat_history.append(("User: " + user_input, "Agent: " + response))
    
    # Return the chat response (styled as a chat interface)
    return f"""
    <html>
        <head>
            <title>Research References Chatbot</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    background-color: #ffffff;
                    padding: 40px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    width: 60%;
                    max-width: 600px;
                }}
                h1 {{
                    color: #333;
                    font-size: 32px;
                    margin-bottom: 20px;
                }}
                .chat-box {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    margin: 20px 0;
                    width: 100%;
                    height: 400px;
                    overflow-y: scroll;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                }}
                .msg-container {{
                    margin-bottom: 10px;
                }}
                .user-msg {{
                    color: #333;
                    font-weight: bold;
                }}
                .agent-msg {{
                    color: #0066cc;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    font-size: 18px;
                    text-decoration: none;
                    color: #0066cc;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Research References Chatbot</h1>
                <div class="chat-box">
                    <div class="msg-container">
                        <p class="user-msg">User: {user_input}</p>
                        <p class="agent-msg">Agent: {response}</p>
                    </div>
                </div>
                <a href="/">Back to Home</a>
            </div>
        </body>
    </html>
    """
