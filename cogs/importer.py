from disnake.ext import commands
from disnake import Permissions
import json
import disnake
from pathlib import Path
from core.messages import MessageHandler
from core.bot import ImportBot

CHANNELS = [
    "discussion",
    "economics",
    "hadith-sciences",
    "history",
    "islamic-discourse",
    "philosophy",
    "quranic-sciences",
    "social-sciences",
]


class Importer(commands.Cog):
    def __init__(self, bot: ImportBot):
        self.bot = bot
        self.message_handler = MessageHandler(bot.upload_files, bot.choose_random_message)

    @commands.slash_command(
        name="test-import",
        description="Test importing messages",
        default_member_permissions=Permissions(kick_members=True),
    )
    async def test_import_messages(self, inter: disnake.ApplicationCommandInteraction):
        with open(
            Path(__file__).parents[1].joinpath(f"archived_channels/test.json"),
            "r",
        ) as f:
            data = json.load(f)
        print(f"Channel: test")
        await inter.response.send_message(
            content=f"Processing messages in test...", ephemeral=True, delete_after=5
        )
        await self.message_handler.process_messages(inter, data)

    @commands.slash_command(
        name="import",
        description="Import messages from a json file",
        default_member_permissions=Permissions(kick_members=True),
    )
    async def import_messages(
        self,
        inter: disnake.ApplicationCommandInteraction,
        channel: str = commands.Param(choices=CHANNELS),  # type: ignore
    ):
        with open(
            Path(__file__).parents[1].joinpath(f"archived_channels/{channel}.json"), "r"
        ) as f:
            data = json.load(f)

        print(f"Channel: {channel}")
        await inter.response.send_message(
            content=f"Processing messages in `{channel}`...",
            ephemeral=True,
            delete_after=15,
        )
        await self.message_handler.process_messages(inter, data)

    @commands.slash_command(name="show-hooks")
    async def show_hooks(self, inter: disnake.ApplicationCommandInteraction):
        webhooks = await inter.channel.webhooks()  # type: ignore
        # Format webhooks
        webhooks = [f"{webhook.name} - {webhook.url}" for webhook in webhooks]
        await inter.channel.send(webhooks)  # type: ignore

    @commands.slash_command(name="delete-hooks")
    async def delete_hooks(self, inter: disnake.ApplicationCommandInteraction):
        webhooks = await inter.channel.webhooks()  # type: ignore
        if len(webhooks) == 0:
            await inter.channel.send("No webhooks to delete.")
            return

        for webhook in webhooks:
            await disnake.Webhook.delete(webhook)

        await inter.channel.send("Deleted all webhooks.")

def setup(bot):
    bot.add_cog(Importer(bot))