import logging
from shazamio import Shazam

# Create a logger for this service
logger = logging.getLogger(__name__)

class ShazamService:
    def __init__(self):
        self.shazam = Shazam()

    async def recognize_song(self, audio_file_path):

        try:
            logger.info(f"Recognizing song from file: {audio_file_path}")
            result = await self.shazam.recognize_song(audio_file_path)
            logger.info("Song recognition successful.")
            return result
        except Exception as e:
            logger.error(f"Error recognizing song: {e}")
            return None
    async def about_track(self, track_id):
        try:
            logger.info(f"Getting info about track: {track_id}")
            track = await self.shazam.track_about(track_id)
            logger.info("Got info about track.")
            return track
        except Exception as e:
            logger.error(f"Error getting info about track: {e}")
            return 
    async def similar_tracks(self, track_id):
        try:
            logger.info(f"Getting info about track: {track_id}")
            track = await self.shazam.related_tracks(track_id, limit=5, offset=2)
            logger.info("Got info about track.")
            return track
        except Exception as e:
            logger.error(f"Error getting info about track: {e}")
            return 
    async def search_artist(self, name_query, limit):
        try:
            logger.info("Searching")
            tracks = await self.shazam.search_artist(name_query, limit)
            print(tracks)
        except Exception as e:
            logger.error(f"Error recognizing song: {e}")
            return None
    async def get_top_songs(self):
        try:
            tracks = await self.shazam.top_world_tracks(limit=10)
            print(tracks)
            return tracks
        except Exception as e:
            logger.error(f"Error song: {e}")
            return None