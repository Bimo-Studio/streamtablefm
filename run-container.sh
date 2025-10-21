#!/bin/bash

# Read stream key from file (keep this file secure on host OS)
STREAM_KEY=$(cat /path/to/stream-key.txt)

podman run -d \
  --name obs-stream-daemon \
  --env STREAM_KEY="$STREAM_KEY" \
  --env STREAM_PROTOCOL="RTMP" \
  --env STREAM_PLACE_WS_URL="wss://stream.place/ws/chat" \
  --device /dev/dri:/dev/dri \
  --group-add keep-groups \
  --security-opt label=disable \
  --shm-size=2g \
  obs-stream-daemon
