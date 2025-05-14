#!/bin/sh
set -e

nvidia-smi
echo "CWD: $(pwd)"

echo "Environment vars:"
env | grep -E 'INPUT|OUTPUT|BUCKET'


echo "Listing /workspace:"
ls -l /workspace

echo "Looking for boltz binary:"
if ! command -v boltz > /dev/null 2>&1; then
    echo "❌ 'boltz' command not found in PATH. Exiting."
    exit 1
fi

echo "boltz found: $(which boltz)"
echo "Running BoltzFold prediction"
python3 aws_version.py "$INPUT" "$OUTPUT" "$BUCKET"
