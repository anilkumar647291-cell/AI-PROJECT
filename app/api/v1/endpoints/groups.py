from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.group import GroupTrip, GroupMember, Expense, ExpenseSplit, Vote
from app.schemas.group import (
    GroupTripCreate,
    GroupTripResponse,
    GroupJoinRequest,
    ExpenseCreate,
    ExpenseResponse,
    GroupExpenseSummary,
    VoteCreate,
    VoteResponse,
    GroupPreferenceConsensus
)
from app.api.deps import get_current_user
from app.services.group_service import GroupService

router = APIRouter()

@router.post("/create", response_model=GroupTripResponse, status_code=status.HTTP_201_CREATED)
def create_group_trip(
    group_in: GroupTripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize a collaborative group trip with shared budget and unique invite code."""
    group_trip = GroupService.create_group_trip(
        db,
        trip_id=group_in.trip_id,
        creator_id=current_user.id,
        shared_budget=group_in.total_shared_budget or 0.0
    )
    return group_trip

@router.post("/join", response_model=GroupTripResponse)
def join_group_trip(
    join_in: GroupJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join an existing group trip via 8-character invite code."""
    try:
        group_trip = GroupService.join_group_trip(db, join_in.invite_code, current_user.id)
        return group_trip
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/expenses/{group_trip_id}", response_model=ExpenseResponse)
def add_group_expense(
    group_trip_id: int,
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a shared group expense and split it evenly or custom across members."""
    group = db.query(GroupTrip).filter(GroupTrip.id == group_trip_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group trip not found")

    members = group.members
    if not members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No members in this group")

    expense = Expense(
        group_trip_id=group_trip_id,
        paid_by_user_id=current_user.id,
        title=expense_in.title,
        amount=expense_in.amount,
        category=expense_in.category
    )
    db.add(expense)
    db.flush()

    if expense_in.split_type == "equal" or not expense_in.custom_splits:
        split_per_person = round(expense_in.amount / len(members), 2)
        for m in members:
            split = ExpenseSplit(
                expense_id=expense.id,
                user_id=m.user_id,
                amount_owed=split_per_person
            )
            db.add(split)
    else:
        for item in expense_in.custom_splits:
            split = ExpenseSplit(
                expense_id=expense.id,
                user_id=item.user_id,
                amount_owed=item.amount_owed
            )
            db.add(split)

    db.commit()
    db.refresh(expense)
    return expense

@router.get("/expenses/{group_trip_id}/summary", response_model=GroupExpenseSummary)
def get_expense_settlements(
    group_trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns total spend, category breakdown, individual member balances,
    and optimized debt settlement transactions (who pays whom).
    """
    try:
        summary = GroupService.calculate_settlements(db, group_trip_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/votes/{group_trip_id}", response_model=VoteResponse)
def cast_vote(
    group_trip_id: int,
    vote_in: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cast a group vote ('up' or 'down') for an attraction, accommodation, or activity."""
    vote = Vote(
        group_trip_id=group_trip_id,
        user_id=current_user.id,
        proposal_type=vote_in.proposal_type,
        proposal_id_or_title=vote_in.proposal_id_or_title,
        vote_value=vote_in.vote_value.lower()
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote

@router.get("/consensus/{group_trip_id}", response_model=GroupPreferenceConsensus)
def get_group_consensus(
    group_trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggregates preferences and voting results to recommend a unified itinerary style
    that resolves group conflicts.
    """
    try:
        consensus = GroupService.aggregate_group_consensus(db, group_trip_id)
        return consensus
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
