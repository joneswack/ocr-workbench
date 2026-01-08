#!/bin/sh

# Usage: ./run_all_experiments.sh [-i <pdf-path>]
# Options:
#   -i <pdf-path>             Specific PDF file to process (default: all PDFs)

set -e
source .venv/bin/activate

# Configuration
SPECIFIC_PDF=""

# Parse command-line arguments
while getopts "i:" opt; do
    case $opt in
        i)
            SPECIFIC_PDF="$OPTARG"
            ;;
        *)
            echo "Usage: $0 [-i <pdf-path>]"
            exit 1
            ;;
    esac
done

PROFILE_SUFFIX="_mem_cpu.dat"

# Run OCR experiment with memory profiling
run_ocr_experiment() {
    local input_file=$1
    local output_dir="../data/output/docint"
    local profile_file="$output_dir/$input_file$PROFILE_SUFFIX"
    
    local start_time=$(date +%s)
    
    rm -f "$profile_file"
    mprof run --output "$profile_file" run_experiment.py \
        --input-file "../data/input/$input_file" \
        --output-dir "$output_dir" \
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    echo "Execution time: ${execution_time}s ($(($execution_time / 60))m $(($execution_time % 60))s)"
}

# Go through each input file and OCR method
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
