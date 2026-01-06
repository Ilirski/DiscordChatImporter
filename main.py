from os import environ

from dotenv import load_dotenv

from core import ImportBot

if __name__ == "__main__":
    load_dotenv()
    token = environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise Exception("Token not found, please set DISCORD_BOT_TOKEN in .env")
    ImportBot().run(token)
