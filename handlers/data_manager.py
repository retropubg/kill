class DataManager:
    def __init__(self):
        self.owner_id = "6699273462"  # Replace with your actual owner ID
        self.authorized_users = ["6699273462", "authorized_username2"]  # Replace with your authorized usernames

    def get_authorized_users(self):
        return self.authorized_users

    def get_user_credits(self, user_id):
        # Logic to get the user's credits, this is a placeholder
        return 1  # Example: return 1 credit for simplicity

    def remove_credits(self, user_id, amount):
        # Logic to remove credits from the user, this is a placeholder
        pass
      
