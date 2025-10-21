#!/usr/bin/env python3
import websocket
import json
import threading
import time
import logging
import os
from queue_manager import MusicQueueManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatMonitor:
    def __init__(self):
        self.queue_manager = MusicQueueManager()
        self.ws = None
        self.connected = False
        
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.handle_chat_message(data)
        except json.JSONDecodeError:
            logger.warning("Received non-JSON message")
            
    def handle_chat_message(self, data):
        # Extract chat message (adjust this based on stream.place API)
        if data.get('type') == 'chat_message':
            message = data.get('message', '').strip()
            user = data.get('user', 'Unknown')
            
            logger.info(f"Chat message from {user}: {message}")
            
            # Check if message is a YouTube URL
            if message.startswith('http') and ('youtube.com/watch' in message or 'youtu.be/' in message):
                self.handle_song_request(message, user)
                
    def handle_song_request(self, youtube_url, user):
        """Handle song requests from chat"""
        try:
            success, message = self.queue_manager.add_song(youtube_url, user)
            
            # Send response back to chat
            if success:
                response = f"@{user} Song added to queue! Position: {self.queue_manager.get_queue_position(youtube_url)}"
            else:
                response = f"@{user} {message}"
                
            self.send_chat_message(response)
            
        except Exception as e:
            logger.error(f"Error handling song request: {e}")
            self.send_chat_message(f"@{user} Error processing your song request")
            
    def send_chat_message(self, message):
        """Send message back to chat"""
        # Implement based on stream.place chat API
        if self.connected and self.ws:
            chat_msg = {
                'type': 'chat_message',
                'message': message
            }
            self.ws.send(json.dumps(chat_msg))
            
    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket connection closed")
        self.connected = False
        
    def on_open(self, ws):
        logger.info("Connected to stream.place chat")
        self.connected = True
        
    def connect(self, websocket_url):
        """Connect to stream.place WebSocket"""
        self.ws = websocket.WebSocketApp(websocket_url,
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close,
                                        on_open=self.on_open)
        
        # Run in separate thread
        def run_ws():
            self.ws.run_forever()
            
        thread = threading.Thread(target=run_ws)
        thread.daemon = True
        thread.start()
        
    def start_monitoring(self):
        """Start monitoring chat and processing music queue"""
        # Connect to stream.place WebSocket (URL needs to be configured)
        websocket_url = os.getenv('STREAM_PLACE_WS_URL', 'wss://stream.place/ws/chat')
        self.connect(websocket_url)
        
        # Start queue processing
        self.queue_manager.start_processing()
        
        # Keep the monitor running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping chat monitor")
            self.queue_manager.stop_processing()

if __name__ == "__main__":
    monitor = ChatMonitor()
    monitor.start_monitoring()
