#!/usr/bin/env bash
# Usage: ./merge_voice.sh voice.mp3   ->  out/promo_final.mp4
# Mixes the ElevenLabs voice over the video; SFX/music are ducked under the voice automatically.
set -e
V="$1"; [ -f "$V" ] || { echo "usage: $0 voice.mp3"; exit 1; }
cd "$(dirname "$0")"
ffmpeg -y -i out/promo_silent.mp4 -i out/sfx.wav -i "$V" -filter_complex \
 "[2:a]adelay=300|300,volume=1.6,asplit=2[vo][sc];[1:a][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[bed];[bed][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest out/promo_final.mp4
echo "done -> out/promo_final.mp4"
