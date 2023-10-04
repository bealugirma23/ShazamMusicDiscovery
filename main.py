import logging
from shazamio import Shazam
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
)

# create an instance of the logger
logger = logging.getLogger()

# logging set up
log_format = logging.Formatter("%(asctime)-15s %(levelname)-2s %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(log_format)

# add the handler
logger.addHandler(sh)
logger.setLevel(logging.INFO)


# Initialize Shazam
shazam = Shazam()


async def start(update, context):
    # Send Welcome message
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Hello, I am a bot that can recognize songs from voice samples or audio files. "
            "Just send me a voice message or an audio file and I will try to find the song for you."
        ),
    )

# Define a function to handle voice messages or audio files
async def recognize(update, context):
    message_idd = "is250"
    botusername = "shazam_music_recognition_bot"
    # Generate the forward link
    forward_link = (
        f"https://t.me/share/url?url=https://t.me/{botusername}?start={message_idd}"
    )
    # Defining and adding buttons
    keyboard = [
        [
            InlineKeyboardButton("Lyrics", callback_data="one"),
            InlineKeyboardButton("➡️Share", callback_data="two", url=forward_link),
        ],
        [InlineKeyboardButton("Download", callback_data="three")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get the file id of the voice message or audio file
    file_id = (
        update.message.voice.file_id
        if update.message.voice
        else update.message.audio.file_id
    )
    # Get the file object from Telegram
    file = await context.bot.get_file(file_id)
    # Download the file locally
    await file.download_to_drive("audio.ogg")
    # Send a message to indicate that the bot is processing the audio
    await context.bot.send_message(
        update.effective_message.chat_id, text=("Processing your audio... 🫡")
    )
    print("Processing your audio...")
    try:
        # Recognize the song using Shazam

        result = await shazam.recognize_song("audio.ogg")
        print(result)
        # Check if there is a match
        if result:
            # Get the song information
            image = result["track"]["images"]["coverart"]
            title = result["track"]["title"]
            artist = result["track"]["subtitle"]
            genre = result["track"]["genres"]["primary"]
            album = result["track"]["sections"][0]["metadata"][0]["text"]
            # spotify = result["track"]["hub"]["providers"][0]["actions"][0]["uri"]
            # Send the song information to the user
            message = await context.bot.send_photo(
                update.effective_chat.id,
                f"{image}",
                caption=(
                    f"🔎 Title: {title}\n"
                    f"🧑‍🎨 Artist: {artist}\n"
                    f"🎧 Genre: {genre}\n"
                    f"📀Album:  {album}\n\n"
                    # f"Spotify:  {spotify}\n\n"
                    f"You can listen to it on Spotify or YouTube."
                ),
                reply_markup=reply_markup,
            )
        else:
            # Send a message that no match was found
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=("Sorry, I could not find your song.😓"),
            )
    except Exception as e:
        # Handle any exceptions and send an error message
        logger.error(e)
        await context.bot.send_message(
            update.effective_message.chat_id,
            text=("Sorry, the voice is not clear. Please try again later.😐"),
        )


# Button OnClick .
async def queryHandler(update, context):
    query = update.callback_query.data
    # Answer the callback query.
    await update.callback_query.answer()
    result = await shazam.recognize_song("audio.ogg")
    # lyrics = result["track"]["sections"][1]["text"]
    try:
        lyrics = (
            "\n".join(result["track"]["sections"][1]["text"])
            .replace("[", "")
            .replace("]", "")
            .replace('" "', "\n")
        )
    except Exception as e:
        logger.error(e)
        await context.bot.send_message(
            update.effective_message.chat_id,
            text=("Sorry, i think this music dont have lyrics 😐"),
        )
    print(f"you clicked {query}")
    if "one" in query:
        try:
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=(f"{lyrics}\n"),
            )
        except Exception as e:
            # Handle any exceptions and send an error message
            logger.error(e)
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=("Sorry, i think this music dont have lyrics 😐"),
            )
    if "three" in query:
        try:
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=("Ok Ok im working on it dude jeez.😓"),
            )
        except Exception as e:
            logger.error(e)


async def unknown(update, context):
    # Send a message that the bot does not understand
    await context.bot.send_message(
        update.effective_message.chat_id,
        text=(
            "Sorry, I do not understand that. Please send me a voice message or an audio file."
        ),
    )


def main():
    print("Starting the bot...")
    # Create an Updater and attach a Dispatcher to it
    application = (
        ApplicationBuilder()
        .token("6508856967:AAE0VyOU9fjxCEHrMWHtVsf1du2GoV2cpY8")
        .build()
    )
 
    # Register the command handler
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.add_handler(CallbackQueryHandler(queryHandler))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, recognize))
    application.add_handler(MessageHandler(filters.COMMAND | filters.TEXT, unknown))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
