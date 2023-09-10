import random
from pyrogram import Client, filters

RUN_STRINGS = (
    "Oh... destiny... just the same... no change... can't escape fate...!!!",
    "Hey... every person's passion...",
    "I don't know how to write, dear. I don't even know how to read...",
    "Today, you won't escape... after winning today's race...",
    "If there's no spark to check what you believe is a lie, it'll burst.",
    "Only one life, make up your mind, there's no heaven, there's no hell, it's just one life, how you want it, it's up to you.",
    "Go Avengers! Suck it Disclosure!",
    "Go, stupid in the House of My Wife and Daughter, Yuvi! Not in a minute off the Today... get out.",
    "I can do that, I can't do that.",
    "In biscuits, there's cream, but thinking there should be a tiger in Tiger biscuits, it's absurd. Work is a pain, dude...",
    "Threw the book, hit the wall, didn't it work!",
    "My dear Lord... You are the only one who can save me...",
    "She gave me a chicken with cream biscuits...",
    "Where was all this time!",
    "English, not a single word...",
    "A guy's dreams are like twinkling stars...",
    "My dear Grandfather, you made him a way.",
    "Take away the dowry you got from the guys, dear.",
    "You wandered aimlessly without achieving anything.",
    "Apply kohl to your eyes, it seems.",
    "Go away, you devil. You people, die.",
    "Go and die. Why did you leave me?",
    "Why did you leave? What do people say?",
)


@Client.on_message(filters.command("runs"))
async def runs(_, message):
    """ /runs strings """
    effective_string = random.choice(RUN_STRINGS)
    if message.reply_to_message:
        await message.reply_to_message.reply_text(effective_string)
    else:
        await message.reply_text(effective_string)
