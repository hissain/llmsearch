# routes/references.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from tools import tools, llm
from langchain.agents import initialize_agent, AgentType

router = APIRouter()

# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    max_iterations=3,
    handle_parsing_errors=True,
    verbose=True,
)

@router.get("/get_references/", response_class=HTMLResponse)
async def get_references(title: str):
    # Initialize chat history
    chat_history = []
    
    # Show progress while waiting for results
    loading_page = """
    <html>
        <head>
            <title>Research References Chatbot</title>
            <a href="/">Back to Home</a>
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
                    width: 80%;
                    max-width: 700px;
                }}
                h1 {{
                    color: #333;
                    font-size: 32px;
                    margin-bottom: 20px;
                }}
                .loader {{
                    border: 8px solid #f3f3f3;
                    border-top: 8px solid #3498db;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 2s linear infinite;
                    margin: 20px 0;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Research References Chatbot</h1>
                <div class="loader"></div>
                <p>Please wait while we fetch the results...</p>
            </div>
        </body>
    </html>
    """

    # Return loading page first
    response = HTMLResponse(content=loading_page)

    # Query the agent after displaying the loading page
    user_input = f"Find related publications for: {title}. Then create references from the publications found."
    response_text = agent.run(input=user_input, chat_history=chat_history)
    chat_history.append(("User: " + user_input, "Agent: " + response_text))

    # Markdown rendering using basic HTML tags
    markdown_output = f"""
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
                    height: 90vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    background-color: #ffffff;
                    padding: 40px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    width: 80%;
                    max-width: 700px;
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
                    text-align: left;
                }}
                .msg-container {{
                    margin-bottom: 10px;
                }}
                .user-msg {{
                    color: #333;
                    font-weight: bold;
                    text-align: left;
                }}
                .agent-msg {{
                    color: #0066cc;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Research References Chatbot</h1>
                <div class="chat-box">
                    <div class="msg-container">
                        <p class="user-msg">Topic: {title}</p>
                        <pre class="agent-msg">{response_text}</pre>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    return HTMLResponse(content=markdown_output)
