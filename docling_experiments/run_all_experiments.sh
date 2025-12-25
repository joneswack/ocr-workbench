#!/bin/sh

# Usage: ./run_all_experiments.sh [cpu|mps|cuda]
# Default accelerator device is 'cpu' if not specified

set -e

# Configuration
ACCELERATOR_DEVICE="${1:-cpu}"
PROFILE_SUFFIX="_mem_${ACCELERATOR_DEVICE}.dat"

# Validate accelerator device
case "$ACCELERATOR_DEVICE" in
    cpu|mps|cuda)
        ;;
    *)
        echo "Error: Invalid accelerator device '$ACCELERATOR_DEVICE'"
        echo "Accepted values: cpu, mps, cuda"
        exit 1
        ;;
esac

# Run OCR experiment with memory profiling
run_ocr_experiment() {
    local method=$1
    local input_file=$2
    local output_dir="../data/output/$method"
    local profile_file="$output_dir/$input_file$PROFILE_SUFFIX"
    
    rm -f "$profile_file"
    mprof run --output "$profile_file" run_experiment.py \
        --input-file "../data/input/$input_file" \
        --output-dir "$output_dir" \
        --ocr-method "$method" \
        --accelerator-device "$ACCELERATOR_DEVICE"
}

# Go through each input file and OCR method
for input_file in ../data/input/*.pdf; do
    input_file=$(basename "$input_file")
    for method in tesseract easyocr suryaocr rapidocr; do
        echo "Running $method experiment..."
        run_ocr_experiment "$method" "$input_file"
    done
done
