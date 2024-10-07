from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
# from openai.error import APIError
import os
from anthropic import Anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from openai import OpenAI
from .schemas import ChatGPTRequest, AnthropicRequest, InteractionResponse
from dotenv import load_dotenv
from datetime import datetime
from .models.interaction import InteractionModel
from anthropic import Client as AnthropicClient
from app.schemas import Interaction

load_dotenv()

app = FastAPI()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["chatgpt_interactions"]
interactions_collection = db["interactions"]

interaction_model = InteractionModel(interactions_collection)

openai_client = None
anthropic_client = None

@app.on_event("startup")
async def startup_event():
    global openai_client, anthropic_client
    
    try:
        openai_client = OpenAI()
        anthropic_client = Anthropic(
    # This is the default and can be omitted
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize clients: {str(e)}")

@app.post("/chatgpt/{model}")
async def chatgpt(request: ChatGPTRequest):
    try:
        response = openai_client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.question}],
            temperature = 0,
        )
        answer = response.choices[0].message.content
        
        interaction = Interaction(
            user_id=request.user_id,
            datetime=datetime.now().isoformat(),
            question=request.question,
            answer=answer.strip(),
            model=request.model
        )
        
        interaction_id = await interaction_model.save_interaction(interaction)
        
        return JSONResponse(content={"message": f"Interaction saved successfully", "interaction_id": interaction_id}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/anthropic/{model}")
async def anthropic(request: AnthropicRequest):
    try:
        message = await anthropic_client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": request.question,
                }
            ],
            model=request.model,
        )
        answer = message.content
        
        interaction = Interaction(
            user_id=request.user_id,
            datetime=datetime.now().isoformat(),
            question=request.question,
            answer=answer,
            model=request.model
        )
        
        interaction_id = await interaction_model.save_interaction(interaction)
        
        return JSONResponse(content={"message": f"Interaction saved successfully", "interaction_id": interaction_id}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/interactions/{user_id}")
async def get_interactions(user_id: str):
    try:
        interactions = await interaction_model.get_interactions_by_user_id(user_id)
        return JSONResponse(content={"interactions": interactions}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve interactions: {str(e)}")
    
@app.get("/interaction/{interaction_id}")
async def get_interaction(interaction_id: str):
    try:
        interaction = await interaction_model.get_interaction_by_id(interaction_id)
        if interaction:
            return JSONResponse(content={"interaction": interaction}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Interaction not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve interaction: {str(e)}") 