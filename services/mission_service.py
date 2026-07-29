"""
services/mission_service.py
---------------------------
Mission Service Layer
"""

from models.mission import MissionModel
from services.xp_service import XPService
from services.coin_service import CoinService


class MissionService:
    """
    Business logic for Mission operations.
    """

    @staticmethod
    def create_mission(data, user_id=None):
        """
        Validate and create a new mission.
        """

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()

        if not title:
            raise ValueError("Mission title is required.")

        if not description:
            raise ValueError("Mission description is required.")

        return MissionModel.create(
            title=title,
            description=description,
            category_id=int(data.get("category_id")),
            difficulty=data.get("difficulty"),
            xp_reward=int(data.get("xp_reward")),
            coin_reward=int(data.get("coin_reward")),
            is_daily="is_daily" in data,
            created_by=user_id
        )

    @staticmethod
    def get_all_missions():
        """
        Return all missions.
        """
        return MissionModel.get_all()

    @staticmethod
    def get_mission(mission_id):
        """
        Return a mission by ID.
        """
        return MissionModel.get_by_id(mission_id)

    @staticmethod
    def update_mission(
        mission_id,
        data
    ):
        """
        Update an existing mission.
        """

        MissionModel.update(
            mission_id=mission_id,
            title=data.get("title").strip(),
            description=data.get("description").strip(),
            category_id=int(data.get("category_id")),
            difficulty=data.get("difficulty"),
            xp_reward=int(data.get("xp_reward")),
            coin_reward=int(data.get("coin_reward")),
            is_daily="is_daily" in data
        )

    @staticmethod
    def complete_mission(
        mission_id,
        user_id
    ):
        """
        Mark a mission as completed and reward the logged-in user.
        """

        mission = MissionModel.get_by_id(mission_id)

        if mission is None:
            raise ValueError("Mission not found.")

        if mission["is_completed"]:
            raise ValueError("Mission is already completed.")

        # Mark mission completed
        MissionModel.complete(mission_id)

        # Reward XP
        XPService.reward(
            user_id=user_id,
            amount=mission["xp_reward"],
            source="Mission",
            reference_id=mission_id
        )

        # Reward Coins
        CoinService.reward(
            user_id=user_id,
            amount=mission["coin_reward"],
            source="Mission",
            reference_id=mission_id
        )

        return mission

    @staticmethod
    def delete_mission(mission_id):
        """
        Delete a mission.
        """
        MissionModel.delete(mission_id)

    @staticmethod
    def total_missions():
        """
        Return total number of missions.
        """
        return MissionModel.count()