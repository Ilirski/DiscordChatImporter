import re
import shutil

# Read authors.csv
with open("authors.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()
    lines = lines[1:]
    # Note: There might be missing authors because of windows file name restrictions substitution
    for line in lines:
        author = line.split("\t")[0].strip()
        author = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", author)
        avatar_path = line.split("\t")[1].strip()
        dst_path = f"avatars\\{author}.png"
        shutil.copyfile(avatar_path, dst_path)