from pyrogram import Client, filters
import requests
from info import ADMINS

# Define the command handler
@Client.on_message(filters.command("geetaverse") & filters.user(ADMINS))
def send_geeta_verse(client, message):
    # Free Geeta API endpoint
    api_url = "https://bhagavadgitaapi.in/slok"

    try:
        # Make a GET request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses

        # Check if the response contains valid JSON
        if response.headers.get("content-type") == "application/json":
            # Parse the JSON response
            verse_data = response.json()

            # Extract the verse
            verse_text = verse_data["data"]["verse"]

            # Send the verse as a reply
            message.reply_text(verse_text)
        else:
            # If the response is not JSON, handle it accordingly
            message.reply_text("Unexpected response format: Not a JSON")

    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors (e.g., 404 Not Found, 500 Internal Server Error)
        message.reply_text(f"HTTP error occurred: {http_err}")

    except Exception as e:
        # Handle any other errors that might occur during the process
        message.reply_text(f"Error fetching Bhagavad Gita verse: {str(e)}")

