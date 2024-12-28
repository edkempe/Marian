#!/bin/bash

# Function to get commit prefix based on file path
get_prefix() {
    local file="$1"
    if [[ $file == tests/* ]]; then
        echo "test"
    elif [[ $file == src/* ]]; then
        echo "feat"
    elif [[ $file == shared_lib/* ]]; then
        echo "lib"
    elif [[ $file == docs/* ]]; then
        echo "docs"
    else
        echo "chore"
    fi
}

# Get list of modified files
modified_files=$(git status --porcelain | grep '^.M\|^M' | cut -c4-)

# If no files are modified, exit
if [ -z "$modified_files" ]; then
    echo "No modified files found"
    exit 0
fi

# For each modified file
while IFS= read -r file; do
    # Get the prefix based on file path
    prefix=$(get_prefix "$file")
    
    # Get the filename without path
    filename=$(basename "$file")
    
    echo "Committing $file..."
    
    # Add and commit the file
    git add "$file"
    git commit -m "$prefix: Update $filename" "$file"
    
done <<< "$modified_files"

echo "All files committed successfully"
