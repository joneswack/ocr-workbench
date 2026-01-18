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

# Set TORCH_DEVICE environment variable
export TORCH_DEVICE="$ACCELERATOR_DEVICE"

# Run OCR experiment with memory profiling
run_ocr_experiment() {
    local input_file=$1
    local output_dir="../data/output/marker"
    local profile_file="$output_dir/$input_file$PROFILE_SUFFIX"

    local start_time=$(date +%s)
    
    rm -f "$profile_file"
    mprof run --output "$profile_file" marker_single \
        "../data/input/$input_file" \
        --output_format markdown \
        --output_dir "$output_dir" \
        --force_ocr

    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    echo "[$input_file] Execution time: ${execution_time}s ($(($execution_time / 60))m $(($execution_time % 60))s)"
}

# Go through each input file
if [ -n "$SPECIFIC_PDF" ]; then
    # Process only the specific PDF file
    input_files="$SPECIFIC_PDF"
else
    # Process all PDF files in the input directory
    input_files="../data/input/*.pdf"
fi

for input_file in $input_files; do
    input_file=$(basename "$input_file")
    
    run_ocr_experiment "$input_file"
done
