#!/usr/bin/env python3
import yt_dlp
import os
import logging

logger = logging.getLogger(__name__)

class AudioDownloader:
    def __init__(self, download_dir="/app/music"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
    def download_audio(self, youtube_url):
        """Download audio from YouTube URL"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info)
                # Change extension to .mp3 due to postprocessing
                base_filename = os.path.splitext(filename)[0]
                mp3_filename = base_filename + '.mp3'
                
                if os.path.exists(mp3_filename):
                    return mp3_filename
                else:
                    logger.error(f"Downloaded file not found: {mp3_filename}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading {youtube_url}: {e}")
            return None
