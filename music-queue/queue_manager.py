#!/usr/bin/env python3
import threading
import time
import logging
import os
from collections import deque
from downloader import AudioDownloader

logger = logging.getLogger(__name__)

class MusicQueueManager:
    def __init__(self, max_queue_size=50):
        self.queue = deque()
        self.max_queue_size = max_queue_size
        self.current_playing = None
        self.processing = False
        self.lock = threading.Lock()
        self.downloader = AudioDownloader()
        
    def add_song(self, youtube_url, user):
        """Add a song to the queue"""
        with self.lock:
            if len(self.queue) >= self.max_queue_size:
                return False, "Queue is full! Please try again later."
                
            # Check if URL is already in queue
            if any(song['url'] == youtube_url for song in self.queue):
                return False, "This song is already in the queue!"
                
            # Add to queue
            song_data = {
                'url': youtube_url,
                'user': user,
                'filename': None,
                'added_time': time.time()
            }
            self.queue.append(song_data)
            
            # Start download in background
            threading.Thread(target=self._download_song, args=(song_data,), daemon=True).start()
            
            return True, f"Song added to queue (position: {len(self.queue)})"
            
    def _download_song(self, song_data):
        """Download song audio in background"""
        try:
            filename = self.downloader.download_audio(song_data['url'])
            if filename:
                song_data['filename'] = filename
                logger.info(f"Downloaded audio for: {song_data['url']}")
            else:
                logger.error(f"Failed to download audio for: {song_data['url']}")
                # Remove from queue if download fails
                with self.lock:
                    if song_data in self.queue:
                        self.queue.remove(song_data)
        except Exception as e:
            logger.error(f"Error downloading song: {e}")
            
    def get_next_song(self):
        """Get the next song to play"""
        with self.lock:
            if not self.queue:
                return None
                
            # Get first song that has been downloaded
            for i, song in enumerate(self.queue):
                if song['filename'] and os.path.exists(song['filename']):
                    self.current_playing = self.queue[i]
                    # Move to current playing and remove from queue
                    del self.queue[i]
                    return self.current_playing
            return None
            
    def finish_current_song(self):
        """Clean up after current song finishes"""
        if self.current_playing:
            try:
                # Delete audio file
                if (self.current_playing['filename'] and 
                    os.path.exists(self.current_playing['filename'])):
                    os.remove(self.current_playing['filename'])
                    logger.info(f"Deleted audio file: {self.current_playing['filename']}")
            except Exception as e:
                logger.error(f"Error deleting audio file: {e}")
            finally:
                self.current_playing = None
                
    def get_queue_position(self, youtube_url):
        """Get position of a song in the queue"""
        with self.lock:
            for i, song in enumerate(self.queue):
                if song['url'] == youtube_url:
                    return i + 1
            return None
            
    def start_processing(self):
        """Start processing the music queue"""
        self.processing = True
        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()
        
    def stop_processing(self):
        """Stop processing the music queue"""
        self.processing = False
        
    def _process_queue(self):
        """Main queue processing loop"""
        while self.processing:
            try:
                # This would integrate with OBS to play audio
                # For now, just simulate playback
                if not self.current_playing:
                    next_song = self.get_next_song()
                    if next_song:
                        logger.info(f"Now playing: {next_song['url']} (requested by {next_song['user']})")
                        # Simulate song duration (in real implementation, monitor playback)
                        time.sleep(180)  # Assume 3 minutes per song
                        self.finish_current_song()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                time.sleep(5)
