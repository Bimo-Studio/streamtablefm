#!/bin/bash

set -e

# Get stream key from environment variable
if [ -z "$STREAM_KEY" ]; then
    echo "ERROR: STREAM_KEY environment variable is required"
    exit 1
fi

# Set up virtual display for OBS
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# Wait for Xvfb to start
sleep 2

# Download background video if it doesn't exist
if [ ! -f "/app/videos/background.mp4" ]; then
    echo "Downloading background video..."
    yt-dlp -f "best[height<=1080]" -o "/app/videos/background.mp4" "https://www.youtube.com/watch?v=q8nPaqfRm_c"
fi

# Configure OBS with stream key
OBS_CONFIG_DIR="/root/.config/obs-studio"
mkdir -p $OBS_CONFIG_DIR

# Copy basic OBS configuration
cp /app/obs-config/basic.ini $OBS_CONFIG_DIR/basic/profiles/

# Configure stream settings based on protocol
if [ "$STREAM_PROTOCOL" = "WHIP" ]; then
    sed "s|{{SERVER}}|https://stream.place|g; s|{{KEY}}|$STREAM_KEY|g" /app/obs-config/stream.ini > $OBS_CONFIG_DIR/basic/profiles/stream.ini
else
    # Default to RTMP
    sed "s|{{SERVER}}|rtmps://stream.place:1935/live|g; s|{{KEY}}|$STREAM_KEY|g" /app/obs-config/stream.ini > $OBS_CONFIG_DIR/basic/profiles/stream.ini
fi

# Start the chat monitor in background
python3 /app/chat-bot/chat_monitor.py &

# Start OBS Studio with virtual display
echo "Starting OBS Studio..."
obs-studio --startstreaming --minimize-to-tray &

# Wait for OBS to start
sleep 10

# Monitor processes and keep container running
while true; do
    if ! pgrep obs-studio > /dev/null; then
        echo "OBS Studio stopped, exiting..."
        exit 1
    fi
    sleep 10
done
