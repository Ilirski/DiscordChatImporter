import os
import re
import json
import sys
from bs4 import BeautifulSoup, Tag, NavigableString
import urllib.parse
import emoji
from natsort import os_sorted


def convert_to_bytes(size: str):
    if size.endswith("KB"):
        return float(size[:-3]) * 1024
    elif size.endswith("MB"):
        return float(size[:-3]) * 1024 * 1024
    else:
        return float(size[:-6])


def clean_and_join_url(sub_folder_path, url):
    return os.path.join(SUBFOLDER_PATH, *urllib.parse.unquote(url).split("/"))


def parse_message_group(message_group):
    parsed_messages = []
    messages = message_group.find_all("div", "chatlog__message")
    for i in range(len(messages)):
        # Only first message in message group has reference
        reference = parse_reference(message_group) if i == 0 else None
        parsed_messages.append(
            parse_message(messages[i], parse_author(message_group), reference)
        )
    return parsed_messages


def parse_reference(message_group):
    message_id = message_group.find("span", "chatlog__reference-link")
    if not message_id:
        return None
    return {"messageId": re.findall(r"'(\d+)'", message_id["onclick"])[0]}


def replace(match):
    word = match.group()
    return word[0:4] + "*" + word[5:]


def parse_author(message_group):
    author_json = {}
    author_json["name"] = message_group.find("span", "chatlog__author-name")["title"]
    if re.search(r"discord", author_json["name"], re.IGNORECASE):
        author_json["name"] = re.sub(
            r"discord", replace, author_json["name"], flags=re.IGNORECASE
        )
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
    # if author["isBot"]:
    # Right now I do not care about non-bot embeds. Maybe in the future
    embeds = message.find_all("div", "chatlog__embed")
    embeds_to_add = parse_embeds(embeds)
    message_to_add["embeds"] = embeds_to_add

    message_to_add["attachments"] = parse_attachments(
        message.find_all("div", "chatlog__attachment")
    )

    # Add at the end to follow DiscordChatExporter's format
    if reference:
        message_to_add["reference"] = reference

    message_to_add["reactions"] = parse_reactions(
        message.find("div", "chatlog__reactions")
    )

    # "reactions": [
    #     {
    #       "emoji": {
    #         "id": "",
    #         "name": "⭐",
    #         "code": "star",
    #         "isAnimated": false,
    #         "imageUrl": "https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/2b50.svg"
    #       },
    #       "count": 8
    #     }
    #   ],

    return message_to_add


def parse_reactions(reactions):
    reactions_to_add = []
    if reactions:
        reactions = reactions.find_all("div", "chatlog__reaction")
        for reaction in reactions:
            reaction_to_add = {}
            img_path = reaction.find("img")["src"]
            emoji_id = img_path[img_path.rfind("/") + 1 : img_path.rfind(".")]
            emoji_id = emoji_id[: emoji_id.rfind("-")]
            reaction_to_add["emoji"] = {}
            reaction_to_add["emoji"]["id"] = ""
            if len(emoji_id) == 18:
                # Custom emoji
                reaction_to_add["emoji"]["id"] = emoji_id
            reaction_to_add["emoji"]["name"] = reaction.find("img")["alt"]
            reaction_to_add["emoji"]["code"] = reaction.find("img")["alt"]
            reaction_to_add["emoji"]["isAnimated"] = False  # Don't know how check
            reaction_to_add["emoji"]["imageUrl"] = clean_and_join_url(
                SUBFOLDER_PATH, img_path
            )
            reaction_to_add["count"] = int(
                reaction.find("span", "chatlog__reaction-count").get_text().strip()
            )
            reactions_to_add.append(reaction_to_add)
    return reactions_to_add


def process_img(node, content):
    emote_name = str(node["alt"])
    if emoji.is_emoji(emote_name):
        return emote_name
    else:
        return ":" + emote_name + ":"


def process_div(node, content):
    classes = node.get("class", [])
    if classes == ["quote"]:
        return "> " + content
    elif "pre--multiline" in classes:
        return "```" + content + "```"
    return content


def process_span(node, content):
    classes = node.get("class", [])
    if "pre--inline" in classes:
        return "`" + content + "`"
    elif "spoiler-text" in classes:
        return "||" + content + "||"
    elif classes == ["mention"]:
        if "title" in node.attrs:
            return "`@" + node["title"] + "`"
        else:
            return "`" + content + "`"
    return content


def process_common_formatting(node, content):
    common_formattings = {
        "strong": "**" + content + "**",
        "em": "*" + content + "*",
        "u": "__" + content + "__",
        "s": "~~" + content + "~~",
    }
    return common_formattings.get(node.name, content)


tag_processors = {"img": process_img, "div": process_div, "span": process_span}


def parse_node(node):
    if isinstance(node, NavigableString):
        return str(node)
    elif isinstance(node, Tag):
        content = "".join(parse_node(child) for child in node.contents)
        if node.name in tag_processors:
            content = tag_processors[node.name](node, content)
        else:
            content = process_common_formatting(node, content)
        return content
    else:
        return ""


def parse_message_content(content):
    if content:
        return parse_node(content)
    else:
        return ""


def parse_attachment(attachment, tag_name, class_name, is_generic=False):
    media_attachment = attachment.find(tag_name, class_name)
    if media_attachment:
        if is_generic:
            media_attachment_path = urllib.parse.unquote(
                media_attachment.find("a")["href"]
            ).replace("/", "\\")
            media_attachment_path = os.path.join(SUBFOLDER_PATH, media_attachment_path)
            media_attachment_name = media_attachment.find("a").get_text().strip()
            media_attachment_size = (
                media_attachment.find("div", "chatlog__attachment-generic-size")
                .get_text()
                .strip()
            )
        else:
            media_attachment_path = urllib.parse.unquote(
                media_attachment["src"]
                if tag_name == "img"
                else media_attachment.find("source")["src"]
            ).replace("/", "\\")
            media_attachment_path = os.path.join(SUBFOLDER_PATH, media_attachment_path)
            media_attachment_name = (
                media_attachment["title"]
                if tag_name == "img"
                else media_attachment.find("source")["title"]
            )
            media_attachment_size = re.findall(r"\((.*?)\)", media_attachment_name)[0]
            media_attachment_name = re.sub(
                r"\(.*?\)", "", media_attachment_name
            ).strip()
        media_attachment_size = convert_to_bytes(media_attachment_size)
        return {
            "file": media_attachment_path,
            "fileName": media_attachment_name,
            "fileSizeBytes": media_attachment_size,
        }
    return None


def parse_attachments(attachments):
    attachments_to_add = []
    for attachment in attachments:
        generic_attachment = parse_attachment(
            attachment, "div", "chatlog__attachment-generic", True
        )
        img_media_attachment = parse_attachment(
            attachment, "img", "chatlog__attachment-media"
        )
        vid_media_attachment = parse_attachment(
            attachment, "video", "chatlog__attachment-media"
        )
        aud_media_attachment = parse_attachment(
            attachment, "audio", "chatlog__attachment-media"
        )
        if generic_attachment:
            attachments_to_add.append(generic_attachment)
        elif img_media_attachment:
            attachments_to_add.append(img_media_attachment)
        elif vid_media_attachment:
            attachments_to_add.append(vid_media_attachment)
        elif aud_media_attachment:
            attachments_to_add.append(aud_media_attachment)
        else:
            raise Exception(f"Unknown attachment type: {attachment}")

    return attachments_to_add


def parse_embeds(embeds):
    embeds_to_add = []

    if embeds:
        for embed in embeds:
            embed_to_add = {}
            embed_title_link = embed.find("div", "chatlog__embed-title-link")
            embed_to_add["title"] = ""
            if embed_title_link:
                embed_to_add["title"] = embed_title_link.get_text().strip()
                embed_to_add["url"] = embed_title_link["href"]
            else:
                embed_title = embed.find("div", "chatlog__embed-title")
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


def main(folder_path):
    # List absolute path of directories in FOLDER_PATH
    directories = [
        os.path.abspath(os.path.join(folder_path, name))
        for name in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, name))
    ]

    # If the only subdirectories are those that end with .html_Files, just process the directory itself
    if all(
        name.endswith(".html_Files")
        for name in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, name))
    ):
        directories = [folder_path]

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
    # The first element of sys.argv list is always the script name itself
    if len(sys.argv) < 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    main(folder_path)
