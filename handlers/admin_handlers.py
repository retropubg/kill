from pyrogram import Client, filters
from pyrogram.types import Message
from utils.data_manager import DataManager

class AdminHandlers:
    def __init__(self, data_manager: DataManager, owner_id: int):
        self.data_manager = data_manager
        self.owner_id = owner_id

    def register(self, app: Client):
        @app.on_message(filters.command("add") & filters.user(self.owner_id))
        async def add_credits(client, message: Message):
            try:
                # Parse user ID and credit amount
                _, user_id, credits = message.text.split(maxsplit=2)
                user_id = str(user_id)
                credits = int(credits)

                # Add credits and respond
                self.data_manager.add_credits(user_id, credits)
                await message.reply_text(f"✅ Successfully added {credits} credits to user {user_id}.")
            except ValueError:
                await message.reply_text("❌ Invalid input. Usage: /add <user_id> <credits>")
            except Exception as e:
                await message.reply_text(f"❌ An error occurred: {str(e)}")

        @app.on_message(filters.command("remove") & filters.user(self.owner_id))
        async def remove_credits(client, message: Message):
            try:
                # Parse user ID and credit amount
                _, user_id, credits = message.text.split(maxsplit=2)
                user_id = str(user_id)
                credits = int(credits)

                # Remove credits
                current_credits = self.data_manager.get_user_credits(user_id)
                if current_credits >= credits:
                    self.data_manager.remove_credits(user_id, credits)
                    await message.reply_text(f"✅ Successfully removed {credits} credits from user {user_id}.")
                else:
                    await message.reply_text(f"❌ User {user_id} has insufficient credits. Current: {current_credits}.")
            except ValueError:
                await message.reply_text("❌ Invalid input. Usage: /remove <user_id> <credits>")
            except Exception as e:
                await message.reply_text(f"❌ An error occurred: {str(e)}")

        @app.on_message(filters.command("info") & filters.user(self.owner_id))
        async def info_command(client, message: Message):
            try:
                # Retrieve all user data
                user_data = self.data_manager.user_credits
                if user_data:
                    response = "📊 **User Info:**\n"
                    for user_id, credits in user_data.items():
                        response += f"👤 User: `{user_id}` | Credits: `{credits}`\n"
                    await message.reply_text(response)
                else:
                    await message.reply_text("ℹ️ No user data available.")
            except Exception as e:
                await message.reply_text(f"❌ An error occurred: {str(e)}")
