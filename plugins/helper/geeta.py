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
    response = requests.get(url)
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

