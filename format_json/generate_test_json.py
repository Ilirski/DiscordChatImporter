import uuid
import json


# Function to generate an ID
def generate_id():
    return str(uuid.uuid4())


# Function to create and append the JSON object
def create_json_object(
    content,
    isPinned=False,
    author="Bricks#9999",
    avatarUrl="https://i.imgur.com/CmRJzBW.png",
    isBot=False,
    embeds=[],
    attachments=[],
    reference="",
):
    if embeds:
        isBot = True

    json_obj = {
        "id": generate_id(),
        "type": "Default",
        "isPinned": isPinned,
        "content": content,
        "author": {"name": author, "avatarUrl": avatarUrl, "isBot": isBot},
        "embeds": embeds,
        "attachments": attachments,
    }

    if reference:
        json_obj["reference"] = {"messageId": reference}

    test_channel["messages"].append(json_obj)


test_channel = {
    "guild": {"name": "Test"},
    "channel": {
        "name": "Test Channel",
        "topic": "This is a test channel for testing purposes.",
    },
    "messages": [],
}

# Test the function with the examples you provided
embed = {
    "title": "This is a test title.",
    "description": "This is a test embed.",
    "color": "#048c28",
    "author": {
        "name": "Author Name",
    },
    "fields": [
        {"name": "Field 1", "value": "I am not inline", "isInline": False},
        {"name": "Field 2", "value": "I am inline", "isInline": True},
    ],
    "footer": {"text": "Footer"},
}

long_message = """
This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. 
""".strip()

long_message_embed = """
This is a message with 2000 characters and embed. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. 
""".strip()

long_message_attachment = """
This is a message with 2000 characters and attachment. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters. This is a message with 2000 characters.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit.This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. This is now past the 2000 character limit. 
""".strip()

attachment = {
    "file": r"C:\Users\User\Downloads\725994301741465600.webp",
    "fileName": "725994301741465600.webp",
    "size": "6.85 kb",
}

create_json_object("This is a normal message.")
create_json_object("This is a pinned message.", isPinned=True)
create_json_object("This message is from a bot.", isBot=True)
create_json_object("**Bolded**")
create_json_object("*Italicized*")
create_json_object("__Underlined__")
create_json_object("~~Strikethrough~~")
create_json_object("||Spoiler||")
create_json_object("```Code block```")
create_json_object("```py\nCode block with language```")
create_json_object("`Inline code block`")
create_json_object("**__Bolded and underlined__**.")
create_json_object("***Bolded and italicized***.")
create_json_object("*__Italicized and underlined__*.")
create_json_object("||~~__***Combined***__~~||.")
create_json_object("Embed with a message.", embeds=[embed])
create_json_object("", embeds=[embed])
create_json_object("Multiple embeds with a message", embeds=[embed, embed])
create_json_object("", embeds=[embed, embed])
create_json_object("This is a message with an attachment.", attachments=[attachment])
create_json_object("", attachments=[attachment])
create_json_object(
    "Multiple attachments with a message", attachments=[attachment, attachment]
)
create_json_object("", attachments=[attachment, attachment])
create_json_object("Reply to a message.", reference=test_channel["messages"][0]["id"])

# Edge cases
create_json_object(long_message)
create_json_object(long_message_embed, embeds=[embed])
create_json_object(long_message_attachment, attachments=[attachment])


# Save the test data to a json file
with open("test.json", "w") as file:
    json.dump(test_channel, file, indent=4)
