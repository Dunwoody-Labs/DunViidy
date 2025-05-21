#!/bin/bash

LOGFILE="/var/log/move_vids.log"
MAXSIZE=10485760  # 10 MB 
SOURCE="/home/dunviidy/MediaCMS/video_store/proccessed_vids"
DESTINATION="/home/dunviidy/MediaCMS/video_store/archived_vids"

# Log rotation everytime log hits 10MB to prevent indefinate growth
if [ -f "$LOGFILE" ]; then
    FILESIZE=$(stat -c%s "$LOGFILE")
    if [ "$FILESIZE" -ge "$MAXSIZE" ]; then
        mv "$LOGFILE" "${LOGFILE}.1"
        echo "$(date): Log rotated (previous log archived to ${LOGFILE}.1)" > "$LOGFILE"
    fi
fi

# Get current day as base-10 to prevent errors on day 8 of the month
DAY=$(date +%d | sed 's/^0*//')

# Runs every other day based on even days
if [ $(( DAY % 2 )) -eq 0 ]; then
    echo "$(date): All files being moved from $SOURCE to $DESTINATION" >> "$LOGFILE"
    mv "$SOURCE"/* "$DESTINATION"/ >> "$LOGFILE" 2>&1
else
    echo "$(date): Skipping task due to odd day." >> "$LOGFILE"
fi

# Add to crontab
# crontab -e

# Runs at midnight but script above moves every other night
# 0 0 * * * /home/dunviidy/MediaCMS/video_store/move_vids.sh