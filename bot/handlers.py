import json
from bot.config import FORWARD_LINK
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.shazam_service import ShazamService
import logging

logger = logging.getLogger(__name__)

shazam_service = ShazamService()

song_data = []
# / Start Command
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
    # Defining and adding buttons
    keyboard = [
        [
            InlineKeyboardButton("Lyrics", callback_data="one"),
            InlineKeyboardButton("About Track", callback_data="two")
        ],
        [
            InlineKeyboardButton("Similar Songs", callback_data="four"),
            InlineKeyboardButton("Download", callback_data="three")],
        [InlineKeyboardButton("➡️Share", callback_data="fifth", url=FORWARD_LINK)],
        [InlineKeyboardButton("🎧Listen on Spotify", callback_data="sixth")]
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

        result = await shazam_service.recognize_song("audio.ogg")
        # print(result)
        # Check if there is a match
        if result:
            # Get the song information
            image = result["track"]["images"]["coverart"]
            title = result["track"]["title"]
            track_id = result["track"]["key"]
            artist = result["track"]["subtitle"]
            genre = result["track"]["genres"]["primary"]
            album = result["track"]["sections"][0]["metadata"][0]["text"]
            spotify = result["track"]["hub"]["providers"][0]["actions"][0]["uri"]
            # Send the song information to the user
            await context.bot.send_photo(
                update.effective_chat.id,
                f"{image}",
                caption=(
                    f"🔎 Track Id: {track_id}\n"
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
      
async def top(update, context):
    result = await shazam_service.get_top_songs()
    await context.bot.send_message(
        update.effective_message.chat_id,
        text=(f"{result}")
    )
async def help(update, context):
    await context.bot.send_message(
        update.effective_message.chat_id,
        text=("hello welcome to the this bot this bot is completely free you can search ")
    )
async def search(update, context):
    await context.bot.send_message(
        update.effective_message.chat_id,
        text=("Please send the artist name you want to search ? ")
    )
    artist_name = update.message.text
    print(artist_name)
    result = await shazam_service.search_artist(name_query=artist_name, limit=3)
    results =  json.loads(result)
    artists = results['artists']['hits']
    for artist_info in artists:
        artist = artist_info['artist']
        await context.bot.send_message(
        update.effective_message.chat_id,
        text=(f"Name: {artist['name']}"
              f"Verified: {artist['verified']}"
              f"Web URL: {artist['weburl']}"
              f"Adam ID: {artist['adamid']}\n"
              )
             )
   
    
    logger.info(result)
# Button OnClick 
async def query_handler(update, context):
    global song_data
    query = update.callback_query.data
    # Answer the callback query.
    await update.callback_query.answer()
    result = await shazam_service.recognize_song("audio.ogg")
    # lyrics = result["track"]["sections"][1]["text"]
# track_id   
    song_data.append(result["track"]["key"]) 
    print(f"you clicked {query}")
    if "one" in query:
        try:
            # print("result", result)
            lyrics = (
                "\n".join(result["track"]["sections"][1]["text"])
                .replace("[", "")
                .replace("]", "")
                .replace('" "', "\n")
            )
            await context.bot.send_message(
                    update.effective_message.chat_id,
                    text=(f"{lyrics}\n"),
                )
        except Exception as e:
            logger.error(e)
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=("Sorry, i think this music dont have lyrics 😐"),
            )
    if 'two' in query: 
        try:
            about_track = await shazam_service.about_track(track_id=song_data[0])
            
            print(about_track)
            # await context.bot.send_message(
            #     update.effective_message.chat_id,
            #     text=(f"{about_track}"),
            # )
        except Exception as e: 
            print(e)      
    if "three" in query:
        try:
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=("Ok Ok im working on it dude jeez.😓"),
            )
        except Exception as e:
            logger.error(e)
    
    if "four" in query:
        try:
            similar_tracks = await shazam_service.similar_tracks(track_id=song_data[0])
            print(similar_tracks)
            # await context.bot.send_message(
            #     update.effective_message.chat_id,
            #     text=(f"{similar_tracks}"),
            # )
        except Exception as e:
            logger.error(e)
     
    if 'sixth' in query: 
        try:
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=(" getting the info"),
            )
        except Exception as e: 
            print(e)
# If Command unknown
async def unknown(update, context):
    # Send a message that the bot does not understand
    await context.bot.send_message(
        update.effective_message.chat_id,
        text=(
            "Sorry, I do not understand that. Please send me a voice message or an audio file."
        ),
    )

