import pandas as pd
import os
import json

d = pd.read_csv(
    "./format_json/authors_to_links.csv", sep="\t", encoding="utf-8"
).to_dict("records")

# Make a dictionary with author as key and link as value
author_to_link = {}
for row in d:
    author_to_link[row["author"]] = row["link"]

files = [f for f in os.listdir("./new_channels")]

# Replace the avatar_url in json with link
os.chdir("./new_channels")
for file in files:
    print(f"Processing {file}")

    with open(file, "r", encoding="utf-8") as f:
        channel = json.loads(f.read())

    for message in channel["messages"]:
        message["author"]["avatarUrl"] = author_to_link[message["author"]["name"]]

    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(channel, indent=4))
