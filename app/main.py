from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>AnanthaLibrary</title>
        </head>
        <body>
            <h1>Welcome to AnanthaLibrary 🚀</h1>
        </body>
    </html>
    """