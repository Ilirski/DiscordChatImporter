import pyimgur
import pandas as pd
import time
from requests import HTTPError
import json
from os import environ
from dotenv import load_dotenv

def upload_image(title, image_path):
    while True:
        try:
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(image_path, title=title)
            return uploaded_image.link
        except HTTPError as e:
            try:
                response_json = json.loads(e.response.text)
                code = response_json["data"]["error"]["code"]
                if code == 400:
                    print("Bad request. Waiting for 5 seconds before retrying.")
                    time.sleep(5)
                elif code == 429:
                    print(
                        "Rate limit reached. Waiting for twenty minutes before retrying."
                    )
                    time.sleep(60 * 20)
                else:
                    print(response_json)
                    print("Unknown error. Waiting for ten minutes before retrying.")
                    time.sleep(600)
            except KeyError | IndexError as e:
                print(e)
                print("Unknown error. Waiting for ten minutes before retrying.")
                time.sleep(600)
        except Exception:  # replace this with the actual exception
            print(Exception)
            print("Rate limit reached. Waiting for an hour before retrying.")
            time.sleep(600)  # wait for an hour


def get_image_link(title, image_path, history):
    # Check if the image is already uploaded by looking into the history DataFrame
    if image_path in history["image_path"].values:
        # Image has been uploaded before. Retrieve the link.
        print("Image already uploaded. Retrieving the link.")
        link = history.loc[history["image_path"] == image_path, "link"].values[0]
    else:
        # Image hasn't been uploaded before. Upload the image and get the link.
        link = upload_image(title, image_path)
        # Save the image path and the link to the history
        new_index = len(history)
        history.loc[new_index] = [image_path, link]
        print("Image uploaded. Saving the link.")
        history.to_csv(
            "image_upload_history.csv", index=False
        )  # Update the history CSV file
    return link


if __name__ == "__main__":
    load_dotenv()
    
    CLIENT_ID = environ.get("IMGUR_CLIENT_ID")

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv("non_duplicates.csv", sep="\t", encoding="utf-8")

    # Load the history of uploaded images
    try:
        history = pd.read_csv("image_upload_history.csv")
    except FileNotFoundError:
        # If the history file doesn't exist, create an empty DataFrame
        history = pd.DataFrame(columns=["image_path", "link"])

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        total = len(df)
        author = row[0].strip()
        path = row[2].strip()
        uploaded_image_link = get_image_link(author, path, history)
        # Create a new column with the uploaded image links
        df.loc[index, "link"] = uploaded_image_link  # type: ignore
        # Show progress with author and link
        print(author, uploaded_image_link + f" ({index + 1}/{total})")  # type: ignore

    # Save
    df.to_csv("authors_with_links.csv", sep="\t", encoding="utf-8", index=False)
