#!/usr/bin/env bash
set -e

HISTORY_FILE="history.json"

for DIR in data/etiss-stats*
do
    echo "Processing $DIR"
    HISTORY_FILE="$DIR/history.json"
    COMBINED_FILE="$DIR/combined_stats.json"

    # Skip if combined_stats.json doesn't exist
    [ -f "$COMBINED_FILE" ] || continue

    # Create history.json if it doesn't exist
    if [ ! -f "$HISTORY_FILE" ]; then
      echo "[]" > "$HISTORY_FILE"
    fi

    # Append new data to existing history.json
    jq -s '.[0] + .[1]' "$HISTORY_FILE" "$COMBINED_FILE" > "${HISTORY_FILE}.tmp" && mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
    echo "Updated $HISTORY_FILE with $(jq length "$HISTORY_FILE") entries"
    rm $COMBINED_FILE
done
