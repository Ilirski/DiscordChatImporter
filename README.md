# DiscordChatImporter

Discord Chat Importer allows you to import archived chats (JSON/HTML) saved with [Discord Chat Exporter](https://github.com/Tyrrrz/DiscordChatExporter) into any Discord text channel!

## Features
- Ability to turn HTML files into Discord Chat Exporter-styled JSON (not fully.
- Uses webhooks to 'impersonate' the profile picture and names of authors. Pfps have to be uploaded to imgur beforehand.
- You can jump to the reply of a message by clicking on the button.
- Reactions are also restored! Default / unicode emojis will show as usual, but custom emotes will appear as text :example:, or can appear as a custom emote on your / other server.
- Uploads images, videos, audio, any other type of files to the server (depending on server file size limit).
- If file size is too big, a link to the file can be appended to the message instead.

## Example:
![image](https://github.com/Ilirski/DiscordChatImporter/assets/24876805/f19f0340-264c-4137-ab17-e3af9ab37693)
![image](https://github.com/Ilirski/DiscordChatImporter/assets/24876805/a816d50d-a00d-426b-a329-8bf804fee873)
![image](https://github.com/Ilirski/DiscordChatImporter/assets/24876805/27f788de-ee2c-4221-85ea-f87fd8217703)

## TODO:
- Messages with embeds and message content are not scraped. Only embed-only messages are posted. This is because I'm not sure what to do with link embeds.
- An easier way of parsing HTML to JSON, uploading the profile pics to imgurs, and mapping custom emotes to their available equivalents

