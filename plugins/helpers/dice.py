from pyrogram import Client, filters
from plugins.helper_functions.cust_p_filters import f_onw_fliter


# EMOJI CONSTANTS
DICE_EMOJI = "🎲"
# EMOJI CONSTANTS


@Client.on_message(filters.command(["roll", "dice"]) & f_onw_fliter)
async def roll_dice(client, message):
    rep_msg_id = message.message_id
    if message.reply_to_message:
        rep_msg_id = message.reply_to_message.message_id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=DICE_EMOJI,
        disable_notification=True,
        reply_to_message_id=rep_msg_id
    )
