#!/bin/bash
dir_path="postprocessing_results/"
deleted_count=0
not_deleted_count=0

for filename in "$dir_path"*.json; do
    if jq -e '. | type == "array" and length > 0' "$filename" > /dev/null; then
        echo -e "\033[32m!!! $(basename "$filename") has data. !!!\e[0m"
        ((not_deleted_count++))
    else
        rm "$filename"
        echo -e "\033[31m$(basename "$filename") is deleted.\e[0m"
        ((deleted_count++))
    fi
done

echo "Deleted files: $deleted_count"
echo "Files with data: $not_deleted_count"
