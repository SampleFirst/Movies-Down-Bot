import os
import PyPDF2
from pyrogram import Client, filters
from gtts import gTTS
from info import LOG_CHANNEL, DOWNLOAD_LOCATION

# A thank you message
Thanks = """Thank you for using this service."""


@Client.on_message(filters.command(["audiobook"]))
async def pdf_to_audio(bot, message):
    try:
        # Check if the command is a reply to a PDF file
        if message.reply_to_message and message.reply_to_message.document:
            pdf_path = os.path.join(DOWNLOAD_LOCATION, f"{message.chat.id}.pdf")
            
            # Inform the user that the PDF is being downloaded
            txt = await message.reply("Downloading PDF...")
            await message.reply_to_message.download(pdf_path)
            await txt.edit("Downloaded PDF")

            # Open the downloaded PDF file and extract its text content
            with open(pdf_path, 'rb') as pdf:
                pdf_reader = PyPDF2.PdfFileReader(pdf)
                num_of_pages = pdf_reader.getNumPages()
                await txt.edit(f"Found {num_of_pages} page(s)")

                page_content = ""
                for page in range(num_of_pages):
                    page_no = pdf_reader.getPage(page)
                    page_content += page_no.extractText()

            # Inform the user that the audio book is being created
            await txt.edit("Creating Your Audio Book... Please wait.")
            
            # Combine PDF text content with a thank you message
            output_text = page_content + Thanks
            
            # Set the language for text-to-speech conversion
            language = 'en-in'
            
            # Use gTTS to convert text to an audio file
            tts_file = gTTS(text=output_text, lang=language, slow=False)
            audio_path = os.path.join(DOWNLOAD_LOCATION, f"{message.chat.id}.mp3")
            tts_file.save(audio_path)

            # Send the generated audio file as a voice message
            with open(audio_path, "rb") as speech:
                await bot.send_audio(message.chat.id, speech)

            # Inform the user that the process is complete
            await txt.edit("Thanks for using this service!")

            # Send the audio file to the LOG_CHANNEL as a backup
            await bot.send_audio(LOG_CHANNEL, audio_path)

            # Remove temporary PDF and audio files
            os.remove(pdf_path)
            os.remove(audio_path)
        else:
            await message.reply("Please reply to a PDF file.")
    except Exception as error:
        print(error)
        await txt.delete()
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
