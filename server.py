#uvicorn server:app --reload    

from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")


app = FastAPI()

@app.get("/")
async def root():
    return "HHTP Endpoint for AgentRAG DGT"

@app.get("/completion")
async def complete_text(prompt: str):
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)