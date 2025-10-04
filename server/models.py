# server/models.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import config

MONGO_URI = os.getenv("MONGO_URI", config.MONGO_URI)
DB_NAME = os.getenv("DB_NAME", config.DB_NAME)

class PersonIn(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None

class Event(BaseModel):
    camera: str
    timestamp: datetime
    image_path: Optional[str] = None
    matched_name: Optional[str] = None
    similarity: Optional[float] = None
    reason: str   # e.g., "unknown_person"

# DB helper
class DB:
    def __init__(self, uri=MONGO_URI, dbname=DB_NAME):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[dbname]
        self.people = self.db["people"]
        self.events = self.db["events"]

    async def add_person(self, name: str, embeddings: List[List[float]], metadata: dict = None):
        # Save multiple embeddings per person for robustness
        doc = {
            "name": name,
            "embeddings": embeddings,  # store as list of lists (float)
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        }
        res = await self.people.insert_one(doc)
        return res.inserted_id

    async def get_all_embeddings(self):
        # returns dict name->list of embeddings (we'll average client-side)
        cursor = self.people.find({})
        out = {}
        async for doc in cursor:
            # for convenience, store a single averaged embedding in memory
            embs = doc.get("embeddings", [])
            if len(embs) == 0:
                continue
            # average embeddings
            import numpy as np
            avg = np.mean(np.array(embs), axis=0).tolist()
            out[doc["name"]] = avg
        return out

    async def add_event(self, event: dict):
        await self.events.insert_one(event)
