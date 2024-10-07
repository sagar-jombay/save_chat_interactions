from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
from app.schemas import Interaction
from bson import ObjectId

class InteractionModel:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def save_interaction(self, interaction_data: Interaction):
        interaction = interaction_data.dict()
        result = await self.collection.insert_one(interaction)
        return str(result.inserted_id)

    async def get_interactions_by_user_id(self, user_id: str):
        cursor = self.collection.find({"user_id": user_id})
        interactions = await cursor.to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        
        for interaction in interactions:
            interaction["_id"] = str(interaction["_id"])
        
        return interactions

    async def get_interaction_by_id(self, interaction_id: str):
        interaction = await self.collection.find_one({"_id": ObjectId(interaction_id)})
        
        if interaction:
            # Convert ObjectId to string for JSON serialization
            interaction["_id"] = str(interaction["_id"])
            return interaction
        else:
            return None