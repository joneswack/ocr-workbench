#!/bin/sh

# lxpj0226.pdf

rm -f ../data/output/mineru/lxpj0226_mem_cpu.dat
mprof run --output ../data/output/mineru/lxpj0226_mem_cpu.dat mineru \
    -d cpu -m ocr -l en -b pipeline \
    -p ../data/input/lxpj0226.pdf \
    -o ../data/output/mineru
