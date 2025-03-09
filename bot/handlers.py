import json

from dataclass_factory import Unknown
from bot.config import FORWARD_LINK
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.shazam_service import ShazamService
import logging
import os
import uuid

logger = logging.getLogger(__name__)
shazam_service = ShazamService()


def initialize_global(value):
    global song_data 
    song_data = value

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

    # Get the file id of the voice message or audio file
    file_id = (
        update.message.voice.file_id
        if update.message.voice
        else update.message.audio.file_id
    )
    
    # Generate a unique filename for the audio file
    unique_filename = f"audio_{uuid.uuid4().hex}.ogg"
    file_path = os.path.join("./uploads", unique_filename)

    # Get the file object from Telegram
    file = await context.bot.get_file(file_id)
    
    # Download the file locally with the unique filename
    await file.download_to_drive(file_path)
    
    # Send a message to indicate that the bot is processing the audio
    await context.bot.send_message(
        update.effective_message.chat_id, text=("Processing your audio... 🫡")
    )
    print("Processing your audio...")
    
    try:
        # Recognize the song using Shazam
        result = await shazam_service.recognize_song(file_path)
        initialize_global(result["track"]["key"])
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
            spotify_url = spotify.replace("spotify:search:", "https://open.spotify.com/search/")
            print(spotify_url)
            keyboard = [
                [
                    InlineKeyboardButton("Lyrics", callback_data="one"),
                    InlineKeyboardButton("About Track", callback_data="two")
                ],
                [
                    InlineKeyboardButton("Similar Songs", callback_data="four"),
                    InlineKeyboardButton("Download", callback_data="three")],
                [InlineKeyboardButton("➡️Share", callback_data="fifth", url=FORWARD_LINK)],
                        [InlineKeyboardButton("🎧Listen on Spotify", url=spotify_url)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
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
    finally:
        # Clean up: Delete the downloaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)   
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
    # Ask for the artist name in a more engaging way
    await context.bot.send_message(
        update.effective_message.chat_id,
        text="🎤 Who's the artist you're looking for? Send me their name!"
    )

    # Wait for the user to send the artist name
    artist_name = update.message.text
    print(f"User searched for: {artist_name}")

    # Indicate that the bot is processing the request
    await context.bot.send_message(
        update.effective_message.chat_id,
        text=f"🔍 Searching for '{artist_name}'... Hold on!"
    )

    try:
        # Search for the artist using Shazam API
        result = await shazam_service.search_artist(name_query=artist_name, limit=3)
        print("Shazam API Response:", result)

        # Check if results are found
        if not result or 'artists' not in result or not result['artists']['hits']:
            await context.bot.send_message(
                update.effective_message.chat_id,
                text=f"😔 Sorry, I couldn't find any artists matching '{artist_name}'. Try another name!"
            )
            return

        # Extract artist information
        artists = result['artists']['hits']
        for artist_info in artists:
            artist = artist_info['artist']
            name = artist.get('name', 'N/A')
            adamid = artist.get('adamid', 'N/A')
            genre = artist.get('genre', 'N/A')
            bio = artist.get('bio', 'No bio available.')
            image = artist.get('avatar', 'https://via.placeholder.com/150')  # Default placeholder image

            # Create a rich response message
            message = (
                f"🎤 **Artist Name:** {name}\n"
                f"🎧 **Genre:** {genre}\n"
                f"📝 **Bio:** {bio}\n"
                f"🔗 **Apple Music ID:** {adamid}\n"
            )

            # Send the artist image and details
            await context.bot.send_photo(
                update.effective_chat.id,
                photo=image,
                caption=message
            )

    except Exception as e:
        # Handle any errors during the process
        print(f"Error: {e}")
        await context.bot.send_message(
            update.effective_message.chat_id,
            text="😓 Oops! Something went wrong. Please try again later."
        )

# Button OnClick 
async def query_handler(update, context):
    query = update.callback_query.data
    # Answer the callback query.
    await update.callback_query.answer()
    result = await shazam_service.recognize_song("./uploads/audio.ogg")
    # lyrics = result["track"]["sections"][1]["text"]
# track_id   
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
            about_track = await shazam_service.about_track(track_id=song_data)
            
            print("rsult", about_track['title'])
            if about_track:

                await context.bot.send_message(
                update.effective_message.chat_id,
                text=(
                    "About the Track\n\n"
                    f"Title: {about_track['title']}\n"
                    f"Artist: {about_track['subtitle']}\n"
                    f"Album: {about_track['sections'][0]['metadata'][0]['text']}\n"
                    f"Label: {about_track['sections'][0]['metadata'][1]['text']}\n"
                    f"Release Date: {about_track['sections'][0]['metadata'][2]['text']}\n"
                ),
                )
            else:
            # Send a message that no match was found
                await context.bot.send_message(
                    update.effective_message.chat_id,
                    text=("Sorry, I could not Detail about the song.😓"),
                )
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
            similar_tracks = await shazam_service.similar_tracks(track_id=song_data)
            # print(similar_tracks)
            for track in similar_tracks['tracks']:
                spotify_url = f"https://open.spotify.com/search/{track['title']}"
                sec_keyboard = [
                [InlineKeyboardButton("➡️Share", callback_data="fifth", url=FORWARD_LINK)],
                [InlineKeyboardButton("🎧Listen on Spotify", url=spotify_url)]
            ]
                sec_keyboard = InlineKeyboardMarkup(sec_keyboard)
                await context.bot.send_photo(
                update.effective_message.chat_id,
                f"{track['images']['coverart']}",
                caption=(
                    f"🔎 Track Id: {track["key"]}\n"
                    f"🔎 Title: {track['title']}\n"
                    f"🧑‍🎨 Artist: {track['subtitle']}\n"
                    # f"🎧 Genre: {track["genres"]["primary"]}\n"
                    # f"📀Album:  {track["sections"][0]["metadata"][0]["text"]}\n\n"
                    # f"*{track['title']}* by {track['subtitle']}\n"
                    # f"Listen on spotify: [Listen here]({track['url']})\n"
                ),
                reply_markup=sec_keyboard,
                parse_mode='Markdown'
            )
                

            
        
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

