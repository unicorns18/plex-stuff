#!/bin/bash

GREEN='\033[0;32m'       # Green color
BLUE='\033[0;34m'        # Blue color
RED='\033[0;31m'         # Red color
NC='\033[0m'             # No color

echo -e "${GREEN}Running check_torrent_files.sh...${NC}"

directory="/storage/torrent_files/"

if [ -d "$directory" ]; then
  # Loop through each item in the directory
  for item in "$directory"/*; do
    # Check if the item is a file or directory
    if [ -f "$item" ] || [ -d "$item" ]; then
      # Print the item's name with color
      echo -e "${BLUE}$(basename "$item")${NC}"
      # Attempt to forcefully delete the item
      if [ -f "$item" ]; then
        rm -f "$item" && echo -e "${RED}Deleted file: $item${NC}"
      elif [ -d "$item" ]; then
        rm -rf "$item" && echo -e "${RED}Deleted directory recursively: $item${NC}"
      fi
    fi
  done
else
  echo -e "${RED}Directory does not exist: $directory${NC}"
fi
