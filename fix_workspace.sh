#!/bin/bash
# Move jobs from relative to absolute workspace location

SOURCE_DIR="/home/bk/source/plotty/~/.local/share/plotty/workspace"
TARGET_DIR="/home/bk/.local/share/plotty/workspace"

echo "Moving jobs from $SOURCE_DIR to $TARGET_DIR"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Move jobs if they exist
if [ -d "$SOURCE_DIR/jobs" ]; then
    if [ -d "$TARGET_DIR/jobs" ]; then
        echo "Target jobs directory already exists, merging..."
        cp -r "$SOURCE_DIR/jobs/"* "$TARGET_DIR/jobs/"
    else
        echo "Moving jobs directory..."
        mv "$SOURCE_DIR/jobs" "$TARGET_DIR/"
    fi
    echo "Jobs moved successfully"
else
    echo "No jobs directory found in source"
fi

# Clean up the relative directory structure
rm -rf "/home/bk/source/plotty/~/.local"

echo "Cleanup completed"