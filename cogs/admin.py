import disnake
from disnake.ext import commands
from core.bot import ImportBot


class AdminCog(commands.Cog):
    def __init__(self, bot: ImportBot):
        self.bot = bot

    @commands.slash_command(name="view-settings")
    @commands.has_permissions(kick_members=True)
    async def view_settings(self, ctx):
        embed = disnake.Embed(
            title="Bot Settings",
            description=f"Upload Files: {self.bot.upload_files}\n"
            f"Choose Random Message: {self.bot.choose_random_message}",
            color=disnake.Color.blue(),
        )
        await ctx.send(embed=embed)

    @commands.slash_command(name="set-upload")
    @commands.has_permissions(kick_members=True)
    async def set_upload(self, ctx, value: bool):
        self.bot.upload_files = value
        self.bot.save_settings()
        await ctx.send(f"Upload Files setting has been set to {value}")

    @commands.slash_command(name="set-random-message")
    @commands.has_permissions(kick_members=True)
    async def set_random_message(self, ctx, value: bool):
        self.bot.choose_random_message = value
        self.bot.save_settings()
        await ctx.send(f"Choose Random Message setting has been set to {value}")


def setup(bot):
    bot.add_cog(AdminCog(bot))
