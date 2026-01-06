from __future__ import annotations

import json
import os

from disnake import Activity, ActivityType, Intents
from disnake.ext.commands import InteractionBot


class ImportBot(InteractionBot):
    """A bot that imports messages from a json file"""

    def __init__(self, upload_files: bool = False, choose_random_message: bool = False):
        super().__init__(
            intents=Intents.all(),
            owner_ids={246673685866479626},
            activity=Activity(type=ActivityType.playing, name="around with disnake"),
        )
        self.COGS: list[str] = []

        # Check if the settings file exists
        if os.path.isfile("settings.json"):
            with open("settings.json") as f:
                settings = json.load(f)
            self.upload_files = settings.get("upload_files", False)
            self.choose_random_message = settings.get("choose_random_message", False)
        else:
            self.upload_files = upload_files
            self.choose_random_message = choose_random_message

        for file in os.listdir("./cogs"):
            if not file.startswith("_"):
                self.COGS.append(f"cogs.{file}")

    def save_settings(self):
        settings = {
            "upload_files": self.upload_files,
            "choose_random_message": self.choose_random_message,
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    async def on_ready(self) -> None:
        guild = self.get_guild(1027340354908864613)
        if not guild:
            raise Exception("Guild not found")

        role = guild.get_role(1027343777293148190)
        if not role:
            raise Exception("Role not found")

        for admin in role.members:
            self.owner_ids.add(admin.id)

        print(f"Admins: {[self.get_user(admin_id).name for admin_id in self.owner_ids]}")  # type: ignore
        print(f"We have logged in as {self.user}")

    def setup(self) -> None:
        for file in self.COGS:
            if file.endswith(".py"):
                self.load_extension(f"{file[:-3]}")
                print(f"Loaded cog: {file}")
            else:
                self.load_extension(file)
        print("Cogs loaded")

    def run(self, token: str) -> None:
        print("Setting up bot...")
        self.setup()
        print("Running bot...")
        self.save_settings()
        super().run(token)
