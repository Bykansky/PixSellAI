from pydantic import BaseModel
import uuid

class GenerationJobResponse(BaseModel):
    job_id: str
    product_id: uuid.UUID

    class Config:
        from_attributes = True
