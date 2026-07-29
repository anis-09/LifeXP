"""
services/mission_service.py
---------------------------
Mission Service Layer
"""

from models.mission import MissionModel


class MissionService:
    """
    Business logic for Mission operations.
    """

    @staticmethod
    def create_mission(data):
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
            created_by=None      # Replace with logged-in user later
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
    def complete_mission(mission_id):
        """
        Mark a mission as completed.
        """

        mission = MissionModel.get_by_id(mission_id)

        if mission is None:
            raise ValueError("Mission not found.")

        if mission["is_completed"]:
            raise ValueError("Mission is already completed.")

        MissionModel.complete(mission_id)

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