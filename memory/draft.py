from typing import TypedDict, Dict, List

class DraftState(TypedDict):
    task: dict
    topic: str
    draft: dict
    review: str
    revision_notes: str
    # New fields for personalized diet and eateries
    diet_plan: Dict[str, str]  # Structure: {meal_time: meal_description}
    eateries: List[Dict[str, str]]  # List of eateries with name and location
