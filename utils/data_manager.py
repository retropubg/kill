import json
from typing import Dict, Any

class DataManager:
    def __init__(self, data_file: str, owner_id: int):
        self.data_file = data_file
        self.owner_id = owner_id
        self.data = self.load_data()

    def load_data(self) -> Dict[str, Any]:
        try:
            with open(self.data_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"authorized_users": [], "users": {}}
        except json.JSONDecodeError:
            print("Warning: Corrupted data file. Creating new data structure.")
            return {"authorized_users": [], "users": {}}

    def save_data(self) -> None:
        try:
            with open(self.data_file, "w") as file:
                json.dump(self.data, file, indent=4)
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def add_credits(self, user_id: str, credits: int) -> None:
        try:
            if "users" not in self.data:
                self.data["users"] = {}
            if user_id not in self.data["users"]:
                self.data["users"][user_id] = {"credits": 0}
            self.data["users"][user_id]["credits"] += credits
            self.save_data()
        except Exception as e:
            print(f"Error adding credits: {str(e)}")

    def remove_credits(self, user_id: str, credits: int) -> bool:
        try:
            if "users" in self.data and user_id in self.data["users"]:
                current_credits = self.data["users"][user_id].get("credits", 0)
                if current_credits >= credits:
                    self.data["users"][user_id]["credits"] -= credits
                    self.save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error removing credits: {str(e)}")
            return False

    def get_user_credits(self, user_id: str) -> int:
        try:
            return self.data.get("users", {}).get(user_id, {}).get("credits", 0)
        except Exception as e:
            print(f"Error getting credits: {str(e)}")
            return 0

    def get_authorized_users(self) -> list:
        return self.data.get("authorized_users", [])

    def add_authorized_user(self, username: str) -> None:
        try:
            if username not in self.data.get("authorized_users", []):
                if "authorized_users" not in self.data:
                    self.data["authorized_users"] = []
                self.data["authorized_users"].append(username)
                self.save_data()
        except Exception as e:
            print(f"Error adding authorized user: {str(e)}")

    def remove_authorized_user(self, username: str) -> None:
        try:
            if username in self.data.get("authorized_users", []):
                self.data["authorized_users"].remove(username)
                self.save_data()
        except Exception as e:
            print(f"Error removing authorized user: {str(e)}")