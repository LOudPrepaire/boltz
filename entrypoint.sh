#!/bin/sh
# entrypoint.sh

nvidia-smi
python3 aws_version.py "$INPUT" "$OUTPUT"
