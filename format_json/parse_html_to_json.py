import os
import re
import json
from bs4 import BeautifulSoup, Tag
import urllib.parse
import emoji
from natsort import os_sorted


def parse_message_group(message_group):
    parsed_messages = []
    messages = message_group.find_all("div", "chatlog__message")
    for i in range(len(messages)):
        # Only first message in message group has reference
        reference = parse_reference(message_group) if i == 0 else None
        parsed_messages.append(
            parse_message(
                messages[i], parse_author(message_group), reference
            )
        )
    return parsed_messages


def parse_reference(message_group):
    message_id = message_group.find("span", "chatlog__reference-link")
    if not message_id:
        return None
    return {"messageId": re.findall(r"'(\d+)'", message_id["onclick"])[0]}


def parse_author(message_group):
    author_json = {}
    author_json["name"] = message_group.find("span", "chatlog__author-name")["title"]
    avatar_url = message_group.find("img", "chatlog__author-avatar")
    author_json["avatarUrl"] = os.path.join(
        SUBFOLDER_PATH, urllib.parse.unquote(avatar_url["src"]).replace("/", "\\")
    )
    bot_tag = message_group.find("span", "chatlog__bot-tag")
    author_json["isBot"] = bool(bot_tag)
    return author_json


def parse_message(message, author, reference):
    message_to_add = {}
    message_to_add["id"] = message["data-message-id"]

    message_to_add["type"] = "Default"
    if reference:
        message_to_add["type"] = "Reply"

    message_to_add["isPinned"] = "chatlog__message--pinned" in message["class"]

    message_to_add["content"] = parse_message_content(
        message.find("span", "preserve-whitespace")
    )

    message_to_add["author"] = author

    message_to_add["embeds"] = []
    if author["isBot"]:
        embed = message.find_all(
            "div", "chatlog__embed"
        )  # TODO: Handle multiple embeds
        embed_to_add = parse_embeds(embed)
        message_to_add["embeds"] = embed_to_add

    message_to_add["attachments"] = parse_attachments(
        message.find_all("div", "chatlog__attachment")
    )

    # Add at the end to follow DiscordChatExporter's format
    if reference:
        message_to_add["reference"] = reference

    return message_to_add


def parse_message_content(content):
    new_content = ""
    if content:
        for i in content.children:
            if type(i) == Tag:
                if i.name == "img":
                    # Emote
                    emote_name = str(i["alt"])
                    if emoji.is_emoji(emote_name):
                        new_content = new_content + emote_name
                    else:
                        new_content = new_content + ":" + emote_name + ":"
                elif i.name == "div" and i["class"] == ["quote"]:
                    # Quote
                    new_content = new_content + ">" + i.text
                elif i.name == "div" and "pre--multiline" in i["class"]:
                    # Multi-line code block
                    new_content = new_content + "```" + i.text + "```"
                elif i.name == "span" and "pre--inline" in i["class"]:
                    # Inline code block
                    new_content = new_content + "`" + i.text + "`"
                elif i.name == "strong":
                    # Bold
                    new_content = new_content + "**" + i.text + "**"
                elif i.name == "em":
                    # Italics
                    new_content = new_content + "*" + i.text + "*"
                elif i.name == "u":
                    # Underline
                    new_content = new_content + "__" + i.text + "__"
                elif i.name == "span" and i["class"] == ["spoiler"]:
                    # Spoiler
                    new_content = new_content + "||" + i.text + "||"
                elif i.name == "span" and i["class"] == ["strike"]:
                    # Strikethrough
                    new_content = new_content + "~~" + i.text + "~~"
                elif i.name == "span" and i["class"] == ["mention"]:
                    # Mention
                    new_content = new_content + '`' + i.text + '`'
                else:
                    # Anything else (links, etc)
                    new_content = new_content + i.text
            else:
                new_content = new_content + str(i)
    return new_content


def parse_attachments(attachments):
    attachments_to_add = []
    for attachment in attachments:
        generic_attachment = attachment.find("div", "chatlog__attachment-generic")
        if generic_attachment:
            # <a> tag in <div> tag
            generic_attachment_path = urllib.parse.unquote(
                generic_attachment.find("a")["href"]
            ).replace("/", "\\")
            generic_attachment_path = os.path.join(
                SUBFOLDER_PATH, generic_attachment_path
            )
            generic_attachment_name = generic_attachment.find("a").get_text().strip()
            generic_attachment_size = (
                generic_attachment.find("div", "chatlog__attachment-generic-size")
                .get_text()
                .strip()
            )  # TODO: Convert to bytes
            attachments_to_add.append(
                {
                    "url": generic_attachment_path,
                    "fileName": generic_attachment_name,
                    "size": generic_attachment_size,
                }
            )

        media_attachment = attachment.find("img", "chatlog__attachment-media")
        if media_attachment:
            media_attachment_path = urllib.parse.unquote(
                media_attachment["src"]
            ).replace("/", "\\")
            media_attachment_path = os.path.join(SUBFOLDER_PATH, media_attachment_path)
            media_attachment_name = media_attachment["title"]
            # Strip first 7 characters (e.g. "Image: ")
            media_attachment_name = media_attachment_name[7:]
            # Get text between brackets (e.g. "(4.2 MB)")
            media_attachment_size = re.findall(r"\((.*?)\)", media_attachment_name)[0]
            # Strip text between brackets
            media_attachment_name = re.sub(
                r"\(.*?\)", "", media_attachment_name
            ).strip()
            attachments_to_add.append(
                {
                    "file": media_attachment_path,
                    "fileName": media_attachment_name,
                    "size": media_attachment_size,
                }
            )
    return attachments_to_add


def parse_embeds(embeds):
    embeds_to_add = []

    if embeds:
        for embed in embeds:
            embed_to_add = {}
            embed_title = embed.find("div", "chatlog__embed-title")
            embed_to_add["title"] = ""
            if embed_title:
                embed_to_add["title"] = embed_title.get_text().strip()

            embed_description = embed.find("div", "chatlog__embed-description")
            embed_to_add["description"] = ""
            if embed_description:
                embed_to_add["description"] = embed_description.get_text().strip()

            embed_color = embed.find("div", "chatlog__embed-color-pill")
            if embed_color:
                try:
                    embed_color = embed_color["style"]
                    # Get rgb values, not rgba
                    embed_color = embed_color[
                        embed_color.find("(") + 1 : embed_color.find(")")
                    ][:-4]
                    embed_color = "#%02x%02x%02x" % tuple(
                        map(int, embed_color.split(","))
                    )
                    embed_to_add["color"] = embed_color
                except KeyError:
                    embed_to_add["color"] = "#000000"  # Black

            embed_footer = embed.find("div", "chatlog__embed-footer")
            if embed_footer:
                embed_to_add["footer"] = {
                    "text": embed_footer.get_text().strip()
                }  # TODO: Handle multiple texts
            embeds_to_add.append(embed_to_add)

            embed_fields = embed.find_all("div", "chatlog__embed-field")
            embed_to_add["fields"] = []
            if embed_fields:
                for field in embed_fields:
                    field_inline = field.find("div", "chatlog__embed-field--inline")
                    field_name = (
                        field.find("div", "chatlog__embed-field-name")
                        .get_text()
                        .strip()
                    )
                    field_value = (
                        field.find("div", "chatlog__embed-field-value")
                        .get_text()
                        .strip()
                    )
                    embed_to_add["fields"].append(
                        {
                            "name": field_name,
                            "value": field_value,
                            "isInline": bool(field_inline),
                        }
                    )
                    
            author_json = {}

            embed_author = embed.find("span", "chatlog__embed-author-name")
            author_json["name"] = ""
            if embed_author:
                author_json["name"] = embed_author.get_text().strip()
                
            author_json["embed_author_url"] = None
                
            embed_author_icon = embed.find("img", "chatlog__embed-author-icon")
            author_json["author_icon"] = None
            if embed_author_icon:
                author_json["author_icon"] = embed_author_icon["src"]

            embed_to_add["author"] = author_json

    return embeds_to_add


def read_html(file_path):
    with open(file_path, "r", encoding="utf") as file:
        html_doc = file.read()
        soup = BeautifulSoup(html_doc, "lxml")
    return soup


def save_json(data, file_name):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)


def main():
    # List absolute path of directories in FOLDER_PATH
    directories = [
        os.path.abspath(os.path.join(FOLDER_PATH, name))
        for name in os.listdir(FOLDER_PATH)
        if os.path.isdir(os.path.join(FOLDER_PATH, name))
    ]

    # Sort reverse alphabetically
    directories = sorted(directories, reverse=True)

    for directory in directories:
        print(f"Processing {directory}")

        folder_name = os.path.basename(os.path.normpath(directory))

        global SUBFOLDER_PATH
        SUBFOLDER_PATH = directory

        # Get all files in directory sorted according to windows (https://stackoverflow.com/a/11969014/17771525)
        files = os_sorted(
            [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            ]
        )

        # However last file is supposed to be first
        files.insert(0, files.pop())

        # Combine all html files into one (https://stackoverflow.com/a/73469828/17771525)
        soup = BeautifulSoup()
        soup.append(soup.new_tag("html"))
        soup.html.append(soup.new_tag("body"))  # type: ignore
        for file in files:
            with open(file, "r", encoding="utf") as html_file:
                soup.body.extend(BeautifulSoup(html_file.read(), "lxml").body)  # type: ignore

        preamble = list(soup.find("div", "preamble__entries-container").children)  # type: ignore
        preamble = [i for i in preamble if type(i) == Tag]
        guild_name = preamble[0].get_text().strip()
        channel_name = preamble[1].get_text().strip()
        try:
            channel_topic = preamble[2].get_text().strip()
        except IndexError:
            channel_topic = ""  # No topic

        guild = {"name": guild_name}
        channel = {"name": channel_name, "topic": channel_topic}

        message_groups = soup.find_all("div", "chatlog__message-group")
        parsed_messages = []
        for group in message_groups:
            parsed_messages.extend(parse_message_group(group))
        messages = {"guild": guild, "channel": channel, "messages": parsed_messages}

        # Get file name
        save_json(messages, f"{folder_name}.json")


if __name__ == "__main__":
    FOLDER_PATH = r"C:\Users\User\Downloads\IT\IT discord server archive\New folder (2)"
    main()
