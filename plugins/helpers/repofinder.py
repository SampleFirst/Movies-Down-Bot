from pyrogram import Client, filters, enums
import requests
from info import *


@Client.on_message(filters.command("repo") & filters.user(ADMINS))
async def repo(client, message):
    # Split the message text and check if there are enough elements
    command_parts = message.text.split("/repo ", 1)
    if len(command_parts) > 1:
        query = command_parts[1]
        headers = {"Authorization": "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"}
        url = f"https://api.github.com/search/repositories?q={query}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                repo = data["items"][0]
                repo_name = repo["full_name"]
                repo_url = repo["html_url"]
                fork_count = repo["forks_count"]
                repo_size = repo["size"] / 1024  # Convert size to KB
                language = repo["language"]
                repo_description = repo.get("description", "No description available")

                message_text = (
                    f"Repo: <b><i>{repo_name}</i></b>\n\n"
                    f"URL: <i>{repo_url}</i>\n\n"
                    f"Description: <b><i>{repo_description}</i></b>\n\n"
                    f"Language: <b><i>{language}</i></b>\n"
                    f"Size: {repo_size:.2f} KB\n"
                    f"Fork Count: {fork_count}"
                )

                await message.reply_text(
                    message_text,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML  # Enable HTML formatting
                )
            else:
                await message.reply_text("No matching repositories found.")
        else:
            await message.reply_text("An error occurred while fetching data.")
    else:
        await message.reply_text("Invalid usage. Provide a query after /repo command.")
