from pyrogram import Client
from config import (
    API_ID, API_HASH, BOT_TOKEN, OWNER_ID,
    DATA_FILE, PROXY_LIST
)
from utils.data_manager import DataManager
from utils.proxy_manager import ProxyManager
from services.stripe_service import StripeService
from handlers.admin_handlers import AdminHandlers
from handlers.user_handlers import UserHandlers
from fake_useragent import UserAgent

def main():
    try:
        # Initialize services
        data_manager = DataManager(DATA_FILE, OWNER_ID)
        proxy_manager = ProxyManager(PROXY_LIST)
        
        # Use dynamic user agent
        user_agent = UserAgent().random
        stripe_service = StripeService(proxy_manager, user_agent)

        # Initialize bot
        app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

        # Register handlers
        admin_handlers = AdminHandlers(data_manager, OWNER_ID)
        user_handlers = UserHandlers(data_manager, stripe_service)

        admin_handlers.register(app)
        user_handlers.register(app)

        # Start the bot
        print("Bot started successfully!")
        app.run()
    except Exception as e:
        print(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    main()