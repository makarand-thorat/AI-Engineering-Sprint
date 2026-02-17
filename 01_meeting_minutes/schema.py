from pydantic import BaseModel, Field
from typing import List, Literal, Optional # Use capital L and Optional

class ActionItem(BaseModel):
    task: str = Field(description="The specific task to be completed")
    owner: str = Field(description="The person responsible for the task")
    # Literal is safe in 3.9, but we define it explicitly
    priority: Literal["High", "Medium", "Low"] = Field(description="Urgency level")

class MeetingSummary(BaseModel):
    title: str = Field(description="A concise title for the meeting")
    # Use List[str] instead of list[str]
    key_points: List[str] = Field(description="3-5 main discussion points")
    action_items: List[ActionItem] = Field(description="List of tasks assigned")
    sentiment: Literal["Productive", "Tense", "Informational"]