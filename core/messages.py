import json
from disnake import (
    ApplicationCommandInteraction,
    Webhook,
    NotFound,
    ButtonStyle,
    WebhookMessage,
    Embed,
    Color,
    File,
    TextChannel,
)
from disnake.ui import Button, ActionRow
from pathlib import Path
import random
import emoji
import re


class FileTooLarge(Exception):
    def __init__(self, message, files):
        self.message: str = message
        self.files: set = files

    def __str__(self):
        return f"{self.message}: {self.files}"


class MessageHandler:
    MESSAGE_CHARACTER_LIMIT = 2000
    FILE_SIZE_LIMIT = 0
    REGIONAL_INDICATORS: set[str] = {
        "🇦",
        "🇧",
        "🇨",
        "🇩",
        "🇪",
        "🇫",
        "🇬",
        "🇭",
        "🇮",
        "🇯",
        "🇰",
        "🇱",
        "🇲",
        "🇳",
        "🇴",
        "🇵",
        "🇶",
        "🇷",
        "🇸",
        "🇹",
        "🇺",
        "🇻",
        "🇼",
        "🇽",
        "🇾",
        "🇿",
    }

    def __init__(self, upload_files, choose_random_message):
        self.upload_files = upload_files
        self.choose_random_message = choose_random_message
        self.message_history: dict[str, str] = self.load_history("message_history.json")
        self.channel_history: dict[str, int] = self.load_history("channel_history.json")
        self.emote_history: dict[str, str] = self.load_history("emote_history.json")

    @staticmethod
    def load_history(file_name):
        if Path(file_name).exists():
            with open(file_name, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_to_file(file_name, data):
        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)

    def create_payloads(self, text):
        if len(text) <= self.MESSAGE_CHARACTER_LIMIT:
            return [text]

        print("Message too long, splitting into chunks")
        first_part = text[: self.MESSAGE_CHARACTER_LIMIT].rsplit(" ", 1)[0]
        second_part = text[len(first_part) :].lstrip()
        return [first_part, second_part]

    def parse_emotes_in_replies(self, text):
        pattern = r'<:([^:>]*):[^>]*>'

        def replace_func(match):
            return ':' + match.group(1) + ':'

        text = re.sub(pattern, replace_func, text)
        return text

    async def send_reply(
        self, webhook: Webhook, message, author, avatar_url, reference_id
    ):
        files = self.upload_attachments(message["attachments"], self.upload_files)
        embeds = self.embed_attachments(message["attachments"], self.upload_files)

        # Read the message that is being referenced
        try:
            referenced_message = await webhook.channel.fetch_message(reference_id)  # type: ignore
            user_reference_url = referenced_message.jump_url
            user_reference_label = referenced_message.author.display_name
            message_reference_label: str = self.parse_emotes_in_replies(referenced_message.content)[:80]
            if len(referenced_message.content) == 0:
                message_reference_label = "No message content"

            disabled = False
        except NotFound:
            user_reference_url = "https://discord.com/"
            user_reference_label = "User not found"
            message_reference_label = "Message not found"
            disabled = True

        components = [
            ActionRow(
                Button(
                    style=ButtonStyle.url,
                    label=user_reference_label,
                    url=user_reference_url,
                    disabled=disabled,
                ),
                Button(
                    style=ButtonStyle.primary,
                    label=message_reference_label,
                    custom_id="message_reference",
                    disabled=disabled,
                ),
            )
        ]

        # Add reactions to the message, if any
        components.extend(self.process_reactions(message["reactions"]))

        return await webhook.send(
            message["content"],
            username=author,
            avatar_url=avatar_url,
            files=files,
            embeds=embeds,
            components=components,
            wait=True,
        )

    async def send_default(self, webhook: Webhook, message, author, avatar_url):
        embeds = []
        files = []
        reactions = []

        try:
            files = self.upload_attachments(message["attachments"], self.upload_files)
            reactions = self.process_reactions(message["reactions"])
            embeds = self.embed_attachments(message["attachments"], self.upload_files)
        except FileTooLarge as e:
            # Remove files that are too large from files
            files = [
                File(f["file"], filename=f["fileName"])
                for f in message["attachments"]
                if f not in e.files
            ]

            file_links: set[str] = set()
            for file in e.files:
                notif = await self.channel.send(
                    f"File `{file['fileName']}` is too large to upload, {self.interactor.mention}. please upload the file somewhere and send a message with the link in the terminal."
                )
                file_link = input(
                    f"Upload {file['fileName']} and enter its link, it will be appended to the message: "
                )
                file_links.add(file_link.strip())
                await notif.delete()

            # Pray to God that the message is not too long
            message["content"] += "\n" + "\n".join(file_links)

            return await webhook.send(
                message["content"],
                username=author,
                avatar_url=avatar_url,
                files=files,
                wait=True,
            )
        except FileNotFoundError as e:
            files = []
            files_not_found = []
            for f in message["attachments"]:
                if r"https:\\cdn.discordapp.com\attachments" in f["file"]:
                    files_not_found.append(f)
                else:
                    files.append(File(f["file"], filename=f["fileName"]))

            if files_not_found:
                embeds = self.embed_attachments(files_not_found, False)
                for embed in embeds:
                    embed.title = "The following file could not be found"

        return await webhook.send(
            message["content"],
            username=author,
            avatar_url=avatar_url,
            files=files,
            embeds=embeds,
            components=reactions,
            wait=True,
        )

        # TODO: What to do with broken links with no embeds that used to have embeds?
        # Type below in history html 2
        # https://twitter.com/depthsofwiki/status/1463637178509139968

    def process_reactions(self, reactions) -> list[ActionRow]:
        action_rows: list[ActionRow] = []
        reactions_to_add = []

        for reaction in reactions:
            reactions_to_add.append((reaction["emoji"]["name"], reaction["count"]))

        # TODO: Limit to 5 action rows (or 4)
        for reaction in reactions_to_add:
            if len(action_rows) == 0:
                action_rows.append(ActionRow())
            if len(action_rows[-1].children) == 5:
                action_rows.append(ActionRow())
            if emoji.is_emoji(reaction[0]) or reaction[0] in self.REGIONAL_INDICATORS:
                reaction_label = reaction[1]
                reaction_emoji = reaction[0]
            elif reaction[0] in self.emote_history:
                reaction_label = reaction[1]
                reaction_emoji = self.emote_history[reaction[0]]
            else:
                reaction_label = f":{reaction[0]}: {reaction[1]}"
                reaction_emoji = None
            action_rows[-1].add_button(
                style=ButtonStyle.secondary,
                label=reaction_label,
                emoji=reaction_emoji,
            )

        return action_rows

    def embed_attachments(self, attachments, upload_files):
        if upload_files:
            return []

        return [
            Embed(title="File uploaded", description=f"`{f['fileName']}`")
            for f in attachments
        ]

    def upload_attachments(self, attachments, upload_files):
        if attachments and not upload_files:
            return []

        attachments_too_large = [
            attachment
            for attachment in attachments
            if attachment["fileSizeBytes"] > self.FILE_SIZE_LIMIT
        ]

        if attachments_too_large:
            raise FileTooLarge("File too large", attachments_too_large)

        files = []
        for f in attachments:
            if r"https:\\cdn.discordapp.com\attachments" in f["file"]:
                raise FileNotFoundError("File is a link.")
            files.append(File(f["file"], filename=f["fileName"]))
        return files

    async def send_bot(self, webhook: Webhook, message, author, avatar_url):
        embeds: list[Embed] = []
        for embed in message["embeds"]:
            r, g, b = tuple(
                int(embed["color"].lstrip("#")[i : i + 2], 16)
                for i in (0, 2, 4)  # hex to rgb
            )
            embed_to_send = Embed(
                color=Color.from_rgb(r, g, b),
            )

            if "title" in embed:
                embed_to_send.title = embed["title"]

            if "description" in embed:
                embed_to_send.description = embed["description"]

            if "author" in embed:
                embed_to_send.set_author(
                    name=embed["author"]["name"],
                    # url=embed["author"]["url"],
                    # icon_url=embed["author"]["iconUrl"],
                )
            for field in embed["fields"]:
                embed_to_send.add_field(
                    name=field["name"], value=field["value"], inline=field["isInline"]
                )
            if "footer" in embed:
                embed_to_send.set_footer(text=embed["footer"]["text"])
            embeds.append(embed_to_send)

        return await webhook.send(
            message["content"],
            username=author,
            avatar_url=avatar_url,
            embeds=embeds,
            wait=True,
        )

    async def handle_message(self, webhook, message):
        author = message["author"]["name"]
        is_bot = message["author"]["isBot"]
        avatar_url = message["author"]["avatarUrl"]
        reference_id = ""
        posted_message: WebhookMessage
        try:
            reference_id = message["reference"]["messageId"]
        except KeyError:
            pass

        # Check if referenced message is in history
        if reference_id and reference_id in self.message_history:
            # If it is, replace the reference id with the posted message id
            reference_id = self.message_history[reference_id]

        if is_bot:
            posted_message = await self.send_bot(webhook, message, author, avatar_url)
        elif message["embeds"] and not message["content"]:
            posted_message = await self.send_bot(
                webhook, message, author, avatar_url
            )
        # Either message has reply or no reply
        elif reference_id:
            posted_message = await self.send_reply(
                webhook, message, author, avatar_url, reference_id
            )
        else:
            posted_message = await self.send_default(
                webhook, message, author, avatar_url
            )
        print(
            f"{posted_message.author.name}: {posted_message.content}"
        )
        if posted_message.embeds:
            print(f"Embeds:\n{[embed.title for embed in posted_message.embeds]}")
        if posted_message.attachments:
            print(f"Attachments:\n{[attachment.filename for attachment in posted_message.attachments]}")
        # Map the message id to the posted message id
        self.message_history[message["id"]] = str(posted_message.id)

        if message["isPinned"]:
            await posted_message.pin()

    async def process_messages(
        self, inter: ApplicationCommandInteraction, start_number, data
    ):
        if not isinstance(inter.channel, TextChannel):
            await inter.send(
                f"ERROR: Cannot import messages to {type(inter.channel)}, channel must be TextChannel."
            )
            return
        self.channel = inter.channel
        webhook = await self.channel.create_webhook(name="importer")

        self.FILE_SIZE_LIMIT = inter.guild.filesize_limit  # type: ignore
        self.interactor = inter.author
        print(f"File size limit: {self.FILE_SIZE_LIMIT}")

        number_of_messages = len(data["messages"])
        start = 0
        if self.choose_random_message:
            start = random.randint(int(number_of_messages // 1.2), number_of_messages)
        if self.choose_random_message and start_number > 0:
            start = start_number
        if start_number > 0:
            start = start_number

        print(f"Starting from message {start+1} / {number_of_messages}")
        print(f"Number of messages: {number_of_messages}")
        try:
            for i, message in enumerate(data["messages"][start:], start=start):
                print(f"Message {i+1} / {number_of_messages}")
                self.channel_history[data["channel"]["name"]] = i

                # Nitro users be like:
                text = message["content"]
                emotes = set(re.findall(r"\:(\S*?)\:", text))  # Avoid duplicate emotes
                for emote in emotes:
                    if emote in self.emote_history:
                        text = text.replace(f":{emote}:", self.emote_history[emote])
                payloads = self.create_payloads(text)

                try:
                    embeds = message["embeds"]
                    attachments = message["attachments"]
                    for j, payload in enumerate(payloads):
                        message["content"] = payload
                        message["embeds"] = (
                            embeds if j == len(payloads) - 1 else []
                        )  # Embeds only on last message
                        message["attachments"] = (
                            attachments
                            if j == len(payloads) - 1
                            else []  # Attachments only on last message
                        )
                        await self.handle_message(webhook, message)
                except Exception as e:
                    await self.channel.send(
                        f"{self.interactor.mention} Error while processing message no. {i+1}/{number_of_messages} in #{data['channel']['name']}:\n```{e}```"
                    )
                    raise e
                finally:
                    self.save_to_file("message_history.json", self.message_history)
                    self.save_to_file("channel_history.json", self.channel_history)
            # Done
            print(
                f"Finished processing {number_of_messages} messages in #{data['channel']['name']}"
            )
            await self.channel.send(
                f"{self.interactor.mention} Finished importing all {number_of_messages} messages.",
                mention_author=True,
            )
        finally:
            await webhook.delete()
