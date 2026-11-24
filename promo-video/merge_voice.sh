#!/usr/bin/env bash
# Usage: ./merge_voice.sh voice.mp3   ->  out/promo_final.mp4
# Mixes: music (out/music.mp3 if present) + SFX + ElevenLabs voice.
# Music and SFX are ducked automatically under the voice.
set -e
V="$1"; [ -f "$V" ] || { echo "usage: $0 voice.mp3"; exit 1; }
cd "$(dirname "$0")"
BED=out/bed.wav
[ -f "$BED" ] || BED=out/sfx.wav
ffmpeg -y -i out/promo_silent.mp4 -i "$BED" -i "$V" -filter_complex \
 "[2:a]adelay=300|300,volume=1.6,asplit=2[vo][sc];[1:a][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[bed];[bed][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest out/promo_final.mp4
echo "done -> out/promo_final.mp4"
