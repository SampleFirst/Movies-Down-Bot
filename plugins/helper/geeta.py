from pyrogram import Client, filters
from bs4 import BeautifulSoup
import requests
from info import *

@Client.on_message(filters.command("geetaverse"))
def send_geeta_verse(client, message):
    verse_with_meaning = get_bhagavad_gita_verse()
    message.reply_text(verse_with_meaning)

def get_bhagavad_gita_verse():
    url = "https://www.holy-bhagavad-gita.org/"
    
    # Set a user agent in the request headers
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, "html.parser")

        # Extracting verse and meaning
        verse_element = soup.find("div", class_="verse")
        meaning_element = soup.find("div", class_="verse-meaning")

        # Check if elements are found before accessing their text attributes
        if verse_element and meaning_element:
            verse = verse_element.text.strip()
            meaning = meaning_element.text.strip()
            return f"{verse}\n\n{meaning}"
        else:
            return "Verse or meaning not found on the webpage."

    except requests.RequestException as e:
        return f"Error fetching data from the webpage: {str(e)}"

