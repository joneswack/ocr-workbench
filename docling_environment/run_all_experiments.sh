#!/bin/sh

# Usage: ./run_all_experiments.sh [-a <accelerator-device>] [-i <pdf-path>]
# Options:
#   -a <accelerator-device>   Accelerator device: cpu, mps, or cuda (default: cpu)
#   -i <pdf-path>             Specific PDF file to process (default: all PDFs)

set -e
source .venv/bin/activate

# Configuration
ACCELERATOR_DEVICE="cpu"
SPECIFIC_PDF=""

# Parse command-line arguments
while getopts "a:i:" opt; do
    case $opt in
        a)
            ACCELERATOR_DEVICE="$OPTARG"
            ;;
        i)
            SPECIFIC_PDF="$OPTARG"
            ;;
        *)
            echo "Usage: $0 [-a <accelerator-device>] [-i <pdf-path>]"
            exit 1
            ;;
    esac
done

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
if [ -n "$SPECIFIC_PDF" ]; then
    # Process only the specific PDF file
    input_files="$SPECIFIC_PDF"
else
    # Process all PDF files in the input directory
    input_files="../data/input/*.pdf"
fi


# Read OCR methods from config.json
OCR_METHODS=$(python -c 'import json; print(" ".join(json.load(open("config.json"))["ocr_engines"]))')

for input_file in $input_files; do
    input_file=$(basename "$input_file")
    for method in $OCR_METHODS; do
        run_ocr_experiment "$method" "$input_file"
    done
done
