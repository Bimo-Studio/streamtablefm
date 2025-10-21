FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    python3 \
    python3-pip \
    ffmpeg \
    pulseaudio \
    xvfb \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install OBS Studio
RUN wget -qO - https://obsproject.com/obsproject.key | apt-key add - && \
    echo "deb http://ppa.launchpad.net/obsproject/obs-studio/ubuntu jammy main" > /etc/apt/sources.list.d/obs-studio.list && \
    apt-get update && apt-get install -y obs-studio

# Install yt-dlp
RUN pip3 install yt-dlp

# Create directories
RUN mkdir -p /app/obs-config /app/chat-bot /app/music-queue /app/videos /app/music

# Copy configuration and scripts
COPY obs-config/ /app/obs-config/
COPY chat-bot/ /app/chat-bot/
COPY music-queue/ /app/music-queue/
COPY entrypoint.sh /app/

# Install Python dependencies for chat bot
RUN pip3 install -r /app/chat-bot/requirements.txt

# Set up OBS profiles and scenes
RUN mkdir -p /root/.config/obs-studio/basic/profiles /root/.config/obs-studio/basic/scenes

WORKDIR /app
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
