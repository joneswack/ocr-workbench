#!/bin/sh

# Global script to run experiments for different environments
# Usage: ./run_all_experiments.sh -e <environment> [-a <accelerator-device>] [-i <pdf-path>]
# Options:
#   -e <environment>          Environment to run: docling, docint, marker, mineru
#   -a <accelerator-device>   Accelerator device: cpu, mps, or cuda (default: cpu)
#   -i <pdf-path>             Specific PDF file to process (default: all PDFs)

set -e

# Default Configuration
ACCELERATOR_DEVICE="cpu"
SPECIFIC_PDF=""
ENVIRONMENT=""

# Parse command-line arguments
while getopts "e:a:i:" opt; do
    case $opt in
        e)
            ENVIRONMENT="$OPTARG"
            ;;
        a)
            ACCELERATOR_DEVICE="$OPTARG"
            ;;
        i)
            SPECIFIC_PDF="$OPTARG"
            ;;
        *)
            echo "Usage: $0 -e <environment> [-a <accelerator-device>] [-i <pdf-path>]"
            exit 1
            ;;
    esac
done

# Validate environment
if [ -z "$ENVIRONMENT" ]; then
    echo "Error: Environment must be specified with -e option."
    echo "Accepted values: docling, docint, marker, mineru"
    exit 1
fi

# Go to the environment directory
if [ -d "${ENVIRONMENT}_environment" ]; then
    cd "${ENVIRONMENT}_environment"
else
    echo "Error: Invalid environment '$ENVIRONMENT'"
    echo "Directory '${ENVIRONMENT}_environment' not found."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Common logic for input files
if [ -n "$SPECIFIC_PDF" ]; then
    input_files=$(basename "$SPECIFIC_PDF")
else
    input_files="../data/input/*.pdf"
fi

PROFILE_SUFFIX="_mem_${ACCELERATOR_DEVICE}.dat"

# --- Helper Functions ---
run_experiment() {
    local profile_file=$1
    shift
    local cmd=("$@")

    local start_time=$(date +%s)
    
    rm -f "$profile_file"
    mprof run --output "$profile_file" "${cmd[@]}"
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    echo "Execution time: ${execution_time}s ($(($execution_time / 60))m $(($execution_time % 60))s)"
}

# --- Environment-specific logic ---

case "$ENVIRONMENT" in
    docling)
        echo "Running docling experiment..."
        case "$ACCELERATOR_DEVICE" in
            cpu|mps|cuda) ;;
            *) echo "Error: Invalid accelerator device '$ACCELERATOR_DEVICE' for docling"; exit 1 ;;
        esac

        OCR_METHODS=$(python -c 'import json; print(" ".join(json.load(open("config.json"))["ocr_engines"]))')
        for input_file in $input_files; do
            input_file=$(basename "$input_file")
            for method in $OCR_METHODS; do
                output_dir="../data/output/$method"
                profile_file="$output_dir/$(basename "$input_file" .pdf)$PROFILE_SUFFIX"
                cmd=(run_experiment.py --input-file "../data/input/$input_file" --output-dir "$output_dir" --ocr-method "$method" --accelerator-device "$ACCELERATOR_DEVICE")
                echo "Running for method: $method"
                run_experiment "$profile_file" "${cmd[@]}"
            done
        done
        ;;

    docint)
        echo "Running docint experiment..."
        PROFILE_SUFFIX="_mem_cpu.dat"
        output_dir="../data/output/docint"
        for input_file in $input_files; do
            input_file=$(basename "$input_file")
            profile_file="$output_dir/$(basename "$input_file" .pdf)$PROFILE_SUFFIX"
            cmd=(run_experiment.py --input-file "../data/input/$input_file" --output-dir "$output_dir")
            run_experiment "$profile_file" "${cmd[@]}"
        done
        ;;

    marker)
        echo "Running marker experiment..."
        case "$ACCELERATOR_DEVICE" in
            cpu|mps|cuda) ;;
            *) echo "Error: Invalid accelerator device '$ACCELERATOR_DEVICE' for marker"; exit 1 ;;
        esac
        export TORCH_DEVICE="$ACCELERATOR_DEVICE"
        output_dir="../data/output/marker"

        for input_file in $input_files; do
            input_file=$(basename "$input_file")
            profile_file="$output_dir/$(basename "$input_file" .pdf)$PROFILE_SUFFIX"
            cmd=(marker_single "../data/input/$input_file" --output_format markdown --output_dir "$output_dir" --force_ocr)
            run_experiment "$profile_file" "${cmd[@]}"
        done
        ;;

    mineru)
        echo "Running mineru experiment..."
        case "$ACCELERATOR_DEVICE" in
            cpu|mps|cuda) ;;
            *) echo "Error: Invalid accelerator device '$ACCELERATOR_DEVICE' for mineru"; exit 1 ;;
        esac
        LANGUAGE=$(python -c 'import json; print(json.load(open("config.json"))["language"])')
        output_dir="../data/output/mineru"

        for input_file in $input_files; do
            input_file=$(basename "$input_file")
            profile_file="$output_dir/$(basename "$input_file" .pdf)$PROFILE_SUFFIX"
            cmd=(mineru -d "$ACCELERATOR_DEVICE" -m ocr -l "$LANGUAGE" -b pipeline -p "../data/input/$input_file" -o "$output_dir")
            run_experiment "$profile_file" "${cmd[@]}"
        done
        ;;
    *)
        echo "Error: Invalid environment '$ENVIRONMENT'"
        echo "Accepted values: docling, docint, marker, mineru"
        cd ..
        exit 1
        ;;
esac

cd ..
echo "Experiment for '$ENVIRONMENT' finished."
