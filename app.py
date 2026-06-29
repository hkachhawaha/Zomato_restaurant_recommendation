import uvicorn
from zomato_ai.phase2.api import app as fastapi_app

# Direct assignment ensures AST parsers / builders recognize the FastAPI instance
app = fastapi_app

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
