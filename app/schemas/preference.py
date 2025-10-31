from pydantic import BaseModel, Field, ConfigDict
from typing import List

class PreferenceRequest(BaseModel):
    center_landmark: str = Field(..., alias="centerLandmark")
    must_visit: List[str] = Field(..., alias="mustVisit")
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    transport_modes: List[str] = Field(..., alias="transportModes")
    allow_alcohol: bool = Field(..., alias="allowAlcohol")
    preferred_cuisine: List[str] = Field(..., alias="preferredCuisine")
    max_commute_time: int = Field(..., alias="maxCommuteTime")

    # ✅ Pydantic v2 新写法
    model_config = ConfigDict(populate_by_name=True)