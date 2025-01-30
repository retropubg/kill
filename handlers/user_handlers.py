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

                cc, mm, yyyy, cvv = card_details.split("|")

                # Process card and get result
                result = self.stripe_service.check_card(card_details)
                
                # Format the response
                if "Do Not Honor" in result:
                    response = (
                        "┏━━━━━━━⍟\n"
                        "┃**#CC_KILLER☠**\n"
                        "┗━━━━━━━━━━━⊛\n\n"
                        f"**💳 CC: `{cc}|{mm}|{yyyy}|{cvv}`**\n\n"
                        "**❌ Do Not Honor Error**\n\n"
                        "**Possible Reasons:**\n"
                        "• Insufficient funds in account\n"
                        "• Bank blocked transaction\n"
                        "• Card restrictions active\n"
                        "• Daily limit exceeded\n"
                        "• International transactions blocked\n\n"
                        "**Solutions:**\n"
                        "1. Check account balance\n"
                        "2. Contact bank for verification\n"
                        "3. Try different card\n"
                        "4. Check card restrictions\n\n"
                        f"**🕒 KILL TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n"
                        "**🤖 BOT BY: @vclubdrop**"
                    )
                else:
                    response = (
                        "┏━━━━━━━⍟\n"
                        "┃**#CC_KILLER☠**\n"
                        "┗━━━━━━━━━━━⊛\n\n"
                        f"**💳 CC: `{cc}|{mm}|{yyyy}|{cvv}`**\n"
                        f"**✨ STATUS: {result}**\n"
                        f"**🕒 KILL TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n"
                        "**🤖 BOT BY: @vclubdrop**"
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
            try:
                user_id = str(message.from_user.id)
                username = message.from_user.username or "No username"
                credits = self.data_manager.get_user_credits(user_id)
                is_owner = user_id == str(self.data_manager.owner_id)
                is_authorized = username in self.data_manager.get_authorized_users()

                status = "👑 Owner" if is_owner else "⭐️ VIP User" if is_authorized else "👤 Regular User"
                credits_display = "♾️ Unlimited" if is_owner or is_authorized else f"🎟️ {credits}"

                info_text = (
                    "┏━━━ 👤 **User Info** ━━━┓\n"
                    f"┣ **ID:** `{user_id}`\n"
                    f"┣ **Username:** @{username}\n"
                    f"┣ **Status:** {status}\n"
                    f"┣ **Credits:** {credits_display}\n"
                    "┗━━━━━━━━━━━━━━━━━┛\n\n"
                    "**Need more credits?**\n"
                    "Contact @vclubdrop to purchase!"
                )

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Buy Credits", url="https://t.me/vclubdrop")],
                    [InlineKeyboardButton("Join Channel", url="https://t.me/+tjKMDddCeSFkNjFl")]
                ])

                await message.reply_text(info_text, reply_markup=keyboard)
            except Exception as e:
                await message.reply_text(f"❌ An error occurred while fetching your information: {str(e)}")
