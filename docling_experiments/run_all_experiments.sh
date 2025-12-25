# CPU Runs (with memory profiling)

# lxpj0226.pdf

# Tesseract
# rm -f ../data/output/tesseract/mem_cpu.dat
# mprof run --output ../data/output/tesseract/mem_cpu.dat run_experiment.py \
#     --input-file ../data/input/lxpj0226.pdf \
#     --output-dir ../data/output/tesseract \
#     --ocr-method tesseract \
#     --accelerator-device cpu

# EasyOCR
# rm -f ../data/output/easyocr/mem_cpu.dat
# mprof run --output ../data/output/easyocr/mem_cpu.dat run_experiment.py \
#     --input-file ../data/input/lxpj0226.pdf \
#     --output-dir ../data/output/easyocr \
#     --ocr-method easyocr \
#     --accelerator-device cpu

# SuryaOCR
rm -f ../data/output/suryaocr/mem_cpu.dat
mprof run --output ../data/output/suryaocr/mem_cpu.dat run_experiment.py \
    --input-file ../data/input/lxpj0226.pdf \
    --output-dir ../data/output/suryaocr \
    --ocr-method suryaocr \
    --accelerator-device cpu

# MPS Runs (without memory profiling)