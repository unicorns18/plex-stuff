dir="postprocessing_results/"

find "$dir" -name '*.json' | while read file; do
    result=$(jq 'recurse | objects | select(.has_excluded_extension == false and .seeds > 10)' "$file")

    if [[ $result != "" ]]; then
        echo "File: $file"
        echo "Matching object: $result"
    fi
done