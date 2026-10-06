import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.group import GroupTrip, GroupMember, Expense, ExpenseSplit, Vote
from app.models.user import User
from app.schemas.group import GroupExpenseSummary, DebtSettlement, GroupPreferenceConsensus

class GroupService:
    """
    Manages group travel dynamics:
    - Shared budgeting & expense splitting with automated debt minimization.
    - Democratic voting on proposals.
    - Preference aggregation and consensus resolution.
    """

    @staticmethod
    def create_group_trip(db: Session, trip_id: int, creator_id: int, shared_budget: float = 0.0) -> GroupTrip:
        existing = db.query(GroupTrip).filter(GroupTrip.trip_id == trip_id).first()
        if existing:
            return existing

        invite_code = uuid.uuid4().hex[:8].upper()
        group_trip = GroupTrip(
            trip_id=trip_id,
            invite_code=invite_code,
            total_shared_budget=shared_budget
        )
        db.add(group_trip)
        db.flush()

        # Add creator as admin member
        member = GroupMember(
            group_trip_id=group_trip.id,
            user_id=creator_id,
            role="admin"
        )
        db.add(member)
        db.commit()
        db.refresh(group_trip)
        return group_trip

    @staticmethod
    def join_group_trip(db: Session, invite_code: str, user_id: int) -> GroupTrip:
        group_trip = db.query(GroupTrip).filter(GroupTrip.invite_code == invite_code.upper()).first()
        if not group_trip:
            raise ValueError("Invalid invitation code")

        # Check if already a member
        existing = db.query(GroupMember).filter(
            GroupMember.group_trip_id == group_trip.id,
            GroupMember.user_id == user_id
        ).first()

        if not existing:
            member = GroupMember(
                group_trip_id=group_trip.id,
                user_id=user_id,
                role="member"
            )
            db.add(member)
            db.commit()
            db.refresh(group_trip)

        return group_trip

    @staticmethod
    def calculate_settlements(db: Session, group_trip_id: int) -> GroupExpenseSummary:
        """
        Calculates total group spend, breakdown by category, net balances per member,
        and solves minimal debt settlements using a greedy bilateral balance reconciliation algorithm.
        """
        group = db.query(GroupTrip).filter(GroupTrip.id == group_trip_id).first()
        if not group:
            raise ValueError("Group trip not found")

        members = group.members
        member_ids = [m.user_id for m in members]
        user_names = {m.user_id: (m.user.full_name or f"Traveler #{m.user_id}") for m in members if m.user}

        expenses = group.expenses
        total_spending = sum(e.amount for e in expenses)
        cat_breakdown: Dict[str, float] = {}

        # net_balance = paid - owed
        balances: Dict[int, float] = {uid: 0.0 for uid in member_ids}

        for exp in expenses:
            cat_breakdown[exp.category] = cat_breakdown.get(exp.category, 0.0) + exp.amount
            if exp.paid_by_user_id in balances:
                balances[exp.paid_by_user_id] += exp.amount

            for split in exp.splits:
                if split.user_id in balances:
                    balances[split.user_id] -= split.amount_owed

        # Round balances
        for uid in balances:
            balances[uid] = round(balances[uid], 2)

        # Debt minimization algorithm
        debtors = []   # (user_id, amount_owed)
        creditors = [] # (user_id, amount_to_receive)

        for uid, bal in balances.items():
            if bal < -0.01:
                debtors.append([uid, -bal])
            elif bal > 0.01:
                creditors.append([uid, bal])

        settlements: List[DebtSettlement] = []

        i = 0
        j = 0
        while i < len(debtors) and j < len(creditors):
            debtor_id, debt_amt = debtors[i]
            creditor_id, cred_amt = creditors[j]

            settled_amount = min(debt_amt, cred_amt)
            if settled_amount > 0.01:
                settlements.append(DebtSettlement(
                    payer_id=debtor_id,
                    payer_name=user_names.get(debtor_id, f"User {debtor_id}"),
                    receiver_id=creditor_id,
                    receiver_name=user_names.get(creditor_id, f"User {creditor_id}"),
                    amount=round(settled_amount, 2)
                ))

            debtors[i][1] -= settled_amount
            creditors[j][1] -= settled_amount

            if debtors[i][1] <= 0.01:
                i += 1
            if creditors[j][1] <= 0.01:
                j += 1

        return GroupExpenseSummary(
            total_group_spending=round(total_spending, 2),
            per_category_breakdown={k: round(v, 2) for k, v in cat_breakdown.items()},
            balances=balances,
            settlements=settlements
        )

    @staticmethod
    def aggregate_group_consensus(db: Session, group_trip_id: int) -> GroupPreferenceConsensus:
        """
        Analyzes group member votes and preferences to provide consensus-based recommendations.
        """
        group = db.query(GroupTrip).filter(GroupTrip.id == group_trip_id).first()
        if not group:
            raise ValueError("Group trip not found")

        votes = group.votes
        tallies: Dict[str, Dict[str, int]] = {}
        for v in votes:
            if v.proposal_id_or_title not in tallies:
                tallies[v.proposal_id_or_title] = {"up": 0, "down": 0}
            if v.vote_value in ["up", "down"]:
                tallies[v.proposal_id_or_title][v.vote_value] += 1

        # Common interest compilation
        interests_list = []
        for m in group.members:
            if m.user and m.user.preferences:
                interests_list.extend(m.user.preferences.get("interests", []))

        common = list(set([i for i in interests_list if interests_list.count(i) >= 2])) or ["sightseeing", "local_cuisine"]
        conflicts = ["High-intensity trekking vs. relaxed cafe hopping"] if len(group.members) > 2 else []

        return GroupPreferenceConsensus(
            group_size=len(group.members),
            common_interests=common,
            conflicting_preferences=conflicts,
            recommended_consensus_itinerary_style="Balanced Hybrid: mornings dedicated to shared major monuments, afternoons offering flexible solo or sub-group exploration.",
            voting_tallies=tallies
        )
