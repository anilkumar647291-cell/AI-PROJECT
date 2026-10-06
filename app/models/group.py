from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class GroupTrip(Base):
    __tablename__ = "group_trips"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), unique=True, nullable=False)
    invite_code = Column(String(32), unique=True, index=True, nullable=False)
    total_shared_budget = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="group_trip")
    members = relationship("GroupMember", back_populates="group_trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group_trip", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="group_trip", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_trip_id = Column(Integer, ForeignKey("group_trips.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member") # "admin", "member"
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    group_trip = relationship("GroupTrip", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    group_trip_id = Column(Integer, ForeignKey("group_trips.id"), nullable=False)
    paid_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), default="general") # food, transport, stay, ticket, misc
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    group_trip = relationship("GroupTrip", back_populates="expenses")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_owed = Column(Float, nullable=False)

    expense = relationship("Expense", back_populates="splits")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    group_trip_id = Column(Integer, ForeignKey("group_trips.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    proposal_type = Column(String(50), nullable=False) # "activity", "restaurant", "stay"
    proposal_id_or_title = Column(String(255), nullable=False)
    vote_value = Column(String(10), nullable=False) # "up", "down"
    voted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    group_trip = relationship("GroupTrip", back_populates="votes")
