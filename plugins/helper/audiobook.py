import os
import PyPDF2
from pyrogram import Client, filters
from gtts import gTTS
from info import DOWNLOAD_LOCATION

# A thank you message
Thanks = """Thank you for using this service."""


@Client.on_message(filters.command(["audiobook"])) 
async def pdf_to_text(bot, message):
    try:
        if message.reply_to_message and message.reply_to_message.document:
            pdf_path = os.path.join(DOWNLOAD_LOCATION, f"{message.chat.id}.pdf")
            txt = await message.reply("Downloading PDF...")
            await message.reply_to_message.download(pdf_path)
            await txt.edit("Downloaded PDF")

            pdf = open(pdf_path, 'rb')
            pdf_reader = PyPDF2.PdfFileReader(pdf)
            num_of_pages = pdf_reader.getNumPages()
            await txt.edit(f"Found {num_of_pages} page(s)")

            page_content = ""
            for page in range(num_of_pages):
                page_no = pdf_reader.getPage(page)
                page_content += page_no.extractText()

            await txt.edit("Creating Your Audio Book... Please wait.")
            output_text = page_content + Thanks
            language = 'en-in'
            tts_file = gTTS(text=output_text, lang=language, slow=False)
            audio_path = os.path.join(DOWNLOAD_LOCATION, f"{message.chat.id}.mp3")
            tts_file.save(audio_path)

            with open(audio_path, "rb") as speech:
                await bot.send_voice(message.chat.id, speech)

            await txt.edit("Thanks for using this service!")
            os.remove(pdf_path)
            os.remove(audio_path)
        else:
            await message.reply("Please reply to a PDF file.")
    except Exception as error:
        print(error)
        await txt.delete()
        os.remove(pdf_path)
