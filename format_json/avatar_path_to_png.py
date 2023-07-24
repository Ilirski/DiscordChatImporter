import os
import json
import hashlib
import re
import shutil
import pandas as pd


def calculate_unicode_hash(author):
    return hashlib.md5(author.encode("utf-8")).hexdigest()


def calculate_hash(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
        return hashlib.md5(file_data).hexdigest()


def copy_file(author, src_path):
    dst_path = f"avatars_hashed\\{author}.png"
    shutil.copyfile(src_path, dst_path)
    return dst_path


files = [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".json")]

df = pd.DataFrame(columns=["author", "avatar_url", "message_count"])

lst = []

for file in files:
    print(f"Processing {file}")
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            author = row["author"]
            avatar_url = row["avatar_url"]
            message_count = len(
                row["message"]
            )  # Assuming one message per row in the json structure

            # If author already exists in the list, update the message count
            if author in [a["author"] for a in lst]:
                for a in lst:
                    if a["author"] == author:
                        a["message_count"] += message_count
            else:  # Otherwise, append a new row to the lst
                lst.append(
                    {
                        "author": author,
                        "avatar_url": avatar_url,
                        "message_count": message_count,
                    }
                )

df = pd.DataFrame(lst)

# Sort the DataFrame by message count
df = df.sort_values(by=["message_count"], ascending=False)

# Apply the functions to the DataFrame
df["author_hash"] = df["author"].apply(calculate_unicode_hash)
df["image_hash"] = df["avatar_url"].apply(calculate_hash)
df["new_path"] = df.apply(
    lambda row: copy_file(row["author_hash"], row["avatar_url"]), axis=1
)

# Remove avatar_url column
df = df.drop(columns=["avatar_url", "author_hash"])

# Reorder columns
df = df[df.columns[[0, 3, 2, 1]]]

# Create a dictionary where the keys are the unique image hashes and the values are the first occurrence of each hash
hash_dict = df.drop_duplicates("image_hash").set_index("image_hash").new_path.to_dict()

# Replace the hashes in the 'image_hash' column with the first occurrence of each hash using the dictionary
df["new_path"] = df["image_hash"].map(hash_dict)

# Show all duplicates
print(
    f"Number of duplicated avatars: {len(df[df.duplicated('image_hash', keep=False)])}"
)

df.to_csv("authors.csv", sep="\t", encoding="utf-8", index=False)
