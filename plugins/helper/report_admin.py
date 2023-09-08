import asyncio
import os
from pyrogram import filters, enums, Client
from Script import script
from info import ADMINS

# Dictionary to store reported messages
reported_messages = {}

@Client.on_message(filters.command(["report"]) & filters.group)
async def report_user(client, message):
    if not message.group:
        await message.reply_text("Reporting commands are only available in group chats.")
        return
    
    if message.reply_to_message:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        report = f"𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋: {mention} ({reporter})" + "\n"
        report += f"𝖬𝖾𝗌𝗌𝖺𝗀𝖾: {message.reply_to_message.link}"
        
        # Store reported message with a unique key (message_id)
        reported_messages[message.reply_to_message.message_id] = report

        # Forward the report to chat administrators
        async for admin in client.iter_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not admin.user.is_bot:
                try:
                    await message.reply_to_message.forward(admin.user.id)
                    await client.send_message(
                        chat_id=admin.user.id,
                        text=report,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    print(f"Error forwarding report to admin: {e}")

@Client.on_message(filters.command(["getreport"]) & filters.private)
async def get_report(client, message):
    if message.from_user.id in ADMINS:
        if message.text.isdigit():
            message_id = int(message.text)
            if message_id in reported_messages:
                report = reported_messages[message_id]
                await message.reply_text(report)
            else:
                await message.reply_text("Report not found.")
        else:
            await message.reply_text("Invalid command format. Use /getreport <message_id>.")
    else:
        await message.reply_text("This command is only for ADMINS.")
