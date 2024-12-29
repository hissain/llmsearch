from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
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
                .loader {
                    border: 8px solid #f3f3f3;
                    border-top: 8px solid #3498db;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 2s linear infinite;
                    margin: 20px 0;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Research References Chatbot</h1>
                <form id="researchForm">
                    <input type="text" name="title" id="title" placeholder="Enter Research Title" required>
                    <button type="submit">Get References</button>
                </form>
                <div id="loader" class="loader" style="display: none;"></div>
                <div id="output" style="display: none;"></div>
            </div>
            <script>
                // Function to show the loader
                function showLoader() {
                    document.getElementById('loader').style.display = 'block'; // Show the loader
                    document.getElementById('output').style.display = 'none';  // Hide the output
                }

                // Function to hide the loader and display the output
                function hideLoader(result) {
                    document.getElementById('loader').style.display = 'none'; // Hide the loader
                    const output = document.getElementById('output');
                    output.style.display = 'block'; // Show the output
                    output.innerHTML = result; // Display the result
                }

                document.getElementById('researchForm').addEventListener('submit', async function(event) {
                    event.preventDefault();
                    const title = document.getElementById('title').value;
                    console.log('Form submitted with title:', title);

                    showLoader();

                    const response = await fetch(`/get_references/?title=${title}`);
                    const result = await response.text();

                    hideLoader(result);
                });
            </script>
        </body>
    </html>
    """
