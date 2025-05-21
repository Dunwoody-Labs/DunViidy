#!/bin/bash

Uploaded_Vids="/home/dunviidy/MediaCMS/video_store/unproccessed_vids"
Converted_Vids="/home/dunviidy/MediaCMS/video_store/proccessed_vids"
Log_File="/home/dunviidy/MediaCMS/video_store/handbrake_convert.log"
FIFO_Queue="/home/dunviidy/MediaCMS/video_store/fifo_queue.txt"

touch "$FIFO_Queue"

log() {
    log_rotate
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$Log_File"
}

# Rotates logs every 20MB, saves original as backup
log_rotate() {
    local max_size=$((20 * 1024 * 1024))
    if [[ -f "$Log_File" ]]; then
        local size=$(stat -c %s "$Log_File")
        if (( size >= max_size )); then
            timestamp=$(date '+%Y%m%d-%H%M%S')
            mv "$Log_File" "${Log_File}.${timestamp}.bak"
            touch "$Log_File"
            log "Log rotated: ${Log_File}.${timestamp}.bak"
        fi
    fi
}


# Check if the video is fully copied by checking if video size stops changing every 2 seconds
file_checker() {
    local vid="$1"
    local prev_size=0
    local current_size=1

    while [[ "$prev_size" -ne "$current_size" ]]; do
        prev_size=$(stat --printf="%s" "$vid" 2>/dev/null || echo 0)
        sleep 2  # Wait 2 secs
        current_size=$(stat --printf="%s" "$vid" 2>/dev/null || echo 0)
    done
}


# Process video files
process_video() {
    local input_vid="$1"
    local output_vid="$Converted_Vids/$(basename "${input_vid%.*}.mp4")"

    log "Waiting for $input_vid to finish copying..."
    file_checker "$input_vid"

    log "Starting conversion: $input_vid"

    # HandBrakeCLI video conversion
    flatpak run --command=HandBrakeCLI fr.handbrake.ghb -i "$input_vid" -o "$output_vid" --preset="Fast 1080p30"

    if [ $? -eq 0 ]; then
        log "$(date): Conversion successful. Deleting $input_vid."
        rm "$input_vid"  # Remove original video after successful conversion
    else
        log "Error converting $input_vid"
    fi
}


# First In First Out function
FIFO_func() {
    while true; do
        if [[ -s "$FIFO_Queue" ]]; then
            # Sort queue by video mtime (modified) for FIFO and update video queue
            sort -n "$FIFO_Queue" | uniq > "${FIFO_Queue}.tmp"
            mv "${FIFO_Queue}.tmp" "$FIFO_Queue"

            # Read and remove the oldest vid from the first line
            IFS="|" read -r mtime vid < "$FIFO_Queue"
            sed -i '1d' "$FIFO_Queue"

            # Convert the vid if it still exists
            if [[ -f "$vid" ]]; then
                process_video "$vid"
            else
                log "Skipped missing vid: $vid"
            fi
        fi
        sleep 3  # Avoid loop
    done
}


# Monitor the folder and converts new videos
inotifywait -m -e close_write,moved_to --format "%w%f" "$Uploaded_Vids" | while read video; do
    if [[ "$video" =~ \.(mp4|mkv|avi|mov|flv|wmv|m4v|webm)$ ]]; then
        if [[ -f "$video" ]]; then
            mtime=$(stat -c "%Y" "$video" 2>/dev/null)
            if [[ -n "$mtime" ]]; then
                if ! grep -qF "|$video" "$FIFO_Queue"; then
                    echo "$mtime|$video" >> "$FIFO_Queue"
                    log "Queued video: $video"
                else
                    log "Skipped duplicate queue: $video"
                fi
            else
                log "Failed to get mtime for: $video"
            fi
        else
            log "File missing at queue time: $video"
        fi
    fi
done &


# Runs FIFO in background
FIFO_func &

# Break Glass in case of Emergency
# pkill -f handbrake_convert.sh
# Run with: nohup /home/dunviidy/MediaCMS/video_store/handbrake_convert.sh
