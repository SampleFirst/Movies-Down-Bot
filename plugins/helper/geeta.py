from pyrogram import Client, filters
import requests
from info import ADMINS


# Define the command handler
@Client.on_message(filters.command("geetaverse") & filters.user(ADMINS))
def send_geeta_verse(client, message):
    # Free Geeta API endpoint
    api_url = "https://bhagavadgitaapi.in/api/v1/verse"

    try:
        # Make a GET request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        verse_data = response.json()

        # Extract the verse
        verse_text = verse_data["data"]["verse"]

        # Send the verse as a reply
        message.reply_text(verse_text)

    except Exception as e:
        # Handle any errors that might occur during the process
        message.reply_text(f"Error fetching Bhagavad Gita verse: {str(e)}")
