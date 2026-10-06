from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class GroupTripCreate(BaseModel):
    trip_id: int
    total_shared_budget: Optional[float] = 0.0

class GroupMemberResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str] = None
    role: str
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GroupTripResponse(BaseModel):
    id: int
    trip_id: int
    invite_code: str
    total_shared_budget: float
    members: List[GroupMemberResponse] = []
    model_config = ConfigDict(from_attributes=True)

class GroupJoinRequest(BaseModel):
    invite_code: str

class ExpenseSplitItem(BaseModel):
    user_id: int
    amount_owed: float

class ExpenseCreate(BaseModel):
    title: str = Field(..., examples=["Ryokan Group Dinner"])
    amount: float = Field(..., gt=0, examples=[240.0])
    category: str = Field(default="food", examples=["food"])
    split_type: str = Field(default="equal", examples=["equal"]) # equal, custom
    custom_splits: Optional[List[ExpenseSplitItem]] = None

class ExpenseResponse(BaseModel):
    id: int
    group_trip_id: int
    paid_by_user_id: int
    title: str
    amount: float
    category: str
    date: datetime
    model_config = ConfigDict(from_attributes=True)

class DebtSettlement(BaseModel):
    payer_id: int
    payer_name: str
    receiver_id: int
    receiver_name: str
    amount: float

class GroupExpenseSummary(BaseModel):
    total_group_spending: float
    per_category_breakdown: Dict[str, float]
    balances: Dict[int, float] # user_id -> balance (+ means owed, - means owes)
    settlements: List[DebtSettlement]

class VoteCreate(BaseModel):
    proposal_type: str = Field(..., examples=["activity"]) # activity, restaurant, stay
    proposal_id_or_title: str = Field(..., examples=["Arashiyama Bamboo Grove Walk"])
    vote_value: str = Field(..., examples=["up"]) # up, down

class VoteResponse(BaseModel):
    id: int
    group_trip_id: int
    user_id: int
    proposal_type: str
    proposal_id_or_title: str
    vote_value: str
    voted_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GroupPreferenceConsensus(BaseModel):
    group_size: int
    common_interests: List[str]
    conflicting_preferences: List[str]
    recommended_consensus_itinerary_style: str
    voting_tallies: Dict[str, Dict[str, int]]
