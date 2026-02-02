# OCR Workbench

OCR Workbench is a ready-to-use framework for easily comparing popular OCR libraries in Python. It abstracts away the individual setup and usage details of each library, allowing you to focus on evaluating results on your data rather than spending time implementing each method yourself.

Simply provide a collection of PDF files and compare all libraries using a single script.

Currently, the following libraries are supported:
- [Docling](https://docling-project.github.io/docling/) including tesseract, EasyOCR, RapidOCR, surya
- [MinerU](https://opendatalab.github.io/MinerU/)
- [Marker](https://github.com/datalab-to/marker)
- [Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence)

This selection focuses on benchmarking open source libraries against proprietary Azure Document Intelligence.

**Features**
- Running experiments with the above libraries via a single script
- Automatic conversion of all provided PDF files in ``data/input`` into markdown using all methods
- Hardware acceleration using CPU, MPS and CUDA
- Time and cpu-memory tracking for each method

## Why do we still care about OCR?

Scanned documents are essentially collections of images stored in PDF format. While easy to view and share, their text content is not machine-readable by default. Extracting this text requires specialized machine learning techniques. Optical Character Recognition (OCR) converts text in images into structured, machine-readable data that can be reliably used for tasks such as document search, analysis, and automated processing.

**Aren't VLMs much better than OCR engines?**

While Vision-Language Models (VLMs) excel at reading text from images and understanding visual context, they produce non-deterministic outputs. This unpredictability, combined with potential text hallucinations or omissions, makes them less suitable for production systems and regulated industries. Traditional OCR engines remain the preferred choice in these scenarios due to their reliability and reproducibility.

Although VLMs for OCR are rapidly evolving and attracting significant research attention, this repository currently focuses exclusively on traditional OCR methods. We may incorporate VLM comparisons in future releases.

## Installation

Since the dependencies of different OCR libraries can have conflicts, we use a separate Python environment per OCR library. Each one uses [uv](https://docs.astral.sh/uv/) as a dependency manager. Make sure to install uv before moving on.

Set up the respective environment using:
```console
cd <environment-name>
uv sync
```
where ``<environment-name>`` is one of ``docling_environment``, ``marker_environment``, ``mineru_environment``, ``azure_environment``.

**Docling with tesseract**

If you want to run docling with tesseract, tesseract needs to be installed:
```console
# Ubuntu:
sudo apt install tesseract-ocr-all
# Via brew on Mac OS:
brew install tesseract
brew install tesseract-lang
```

Additionally, the correct path for the tesseract data directory needs to be set in ``docling_environment/config.json``.
See [https://tesseract-ocr.github.io/tessdoc/Installation.html](https://tesseract-ocr.github.io/tessdoc/Installation.html) for an explanation.
If you do not wish to use tesseract, simply remove it from ``ocr_engines`` in ``docling_environment/config.json``.

**Azure Document Intelligence**

In order to use Azure Document Intelligence, you need to set up an account on Microsoft Azure and create a [Document Intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence) resource. Then place the API key in `docint_environment/config.json`.

## Running experiments

Place some PDF files to be parsed in ``data/input``.

Then run:

```console
bash run_ocr_experiments.sh -a <accelerator> -e <environment>
```

where ``<accelerator>`` is one of ``cpu``, ``mps``, ``cuda`` and ``<environment>`` is one of ``docling``, ``marker``, ``mineru``, ``docint``.

By default, the script processes all PDF files in ``data/input``.

If you want to run a single experiment instead, run the following:

```console
bash run_ocr_experiments.sh -i <input-file> -a <accelerator> -e <environment>
```

The markdown output is stored in ``data/output/<ocr-method>/<file-name>.md``.

In order to visualize CPU memory over time, run:
```console
source <environment>/.venv/bin/activate
mprof plot data/output/<ocr-method>/<file-name>_mem_cpu.dat
```

For almost every environment, there exists an additional ``config.json`` file with some preconfigured defaults. You can change it based on your needs.

## Evaluation on a few sample documents

Using our script, we produced OCR outputs for four example documents and compared them in terms of OCR quality as well as resource consumption.

The following publicly available PDFs were used and saved in ``data/input``:
- [Information About Coca-Cola Volume Growth](https://www.industrydocuments.ucsf.edu/all-industries/documents/viewer/?iid=lxpj0226&id=lxpj0226&q=%5Bobject+Object%5D&db-set=documents&sort=&pg=1&npp=20&industry=all-industries&rtool=download)
- [Handwriting Sample from NIST Special Database 19](https://www.nist.gov/srd/nist-special-database-19) (the sample image was saved as a PDF file)
- [2020 Annual Report Midwest Food Bank](https://midwestfoodbank.org/images/AR_2020_WEB2.pdf)
- [RKI: Epidemiologisches Bulletin](https://www.rki.de/DE/Aktuelles/Publikationen/Epidemiologisches-Bulletin/2025/50_25.pdf?__blob=publicationFile&v=8) (German)

Speed is measured on a Macbook Air M4 for CPU and MPS, and on an NVIDIA RTX 5090 GPU (32 GB VRAM).
Memory usage is measured only once for CPU.
OCR quality is subjectively graded and compared based on the markdown output stored in ``data/output/<ocr-method>/<file-name>.md``.

### Summary

| OCR-Library | Coca-Cola | NIST Handwriting | World Food Bank | RKI Bulletin |
|---|---|---|---|---|
| Docling - Tesseract | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (32s)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (10s)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (50s)` | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (101s)` |
| Docling - EasyOCR | ![#ffa500](https://via.placeholder.com/15/ffa500/000000?text=+) `Medium (37s)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (7s)` | ![#ffa500](https://via.placeholder.com/15/ffa500/000000?text=+) `Medium (41s)` | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (95s)` |
| Docling - RapidOCR | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (12s)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (4s)` | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (28s)` | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (52s)` |
| Docling - suryaocr | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (31s)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (8s)` | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (49s)` | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (270s)` |
| marker | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (X)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (5s)` | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (35s)` | ![#ffa500](https://via.placeholder.com/15/ffa500/000000?text=+) `Medium (143s)` |
| MinerU | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (42s)` | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Poor (16s)` | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (60s)` | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (88s)` |
| Document Intelligence | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (8s)` | ![#57b4f7](https://via.placeholder.com/15/57b4f7/000000?text=+) `Good (5s)` | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (14s)` | ![#2eb82e](https://via.placeholder.com/15/2eb82e/000000?text=+) `Very good (10s)` |

### Information About Coca-Cola Volume Growth

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (misses text, confuses table entries, doesn't read checkboxes correctly) | CPU: 34<br>MPS: 34<br>GPU: 32 | 3 GB |
| Docling - EasyOCR | Medium (reads text well, confuses some table entries, doesn't read checkboxes correctly) | CPU: 129<br>MPS: 52<br>GPU: 37 | 11.4 GB |
| Docling - RapidOCR | Good (reads text well, gets table entries correct, doesn't read checkboxes correctly) | CPU: 161<br>MPS: 160<br>GPU: 12 | 6.4 GB |
| Docling - suryaocr | Very good (reads text well, gets table entries correct, gets most checkboxes correct) | CPU: 369<br>MPS: 337<br>GPU: 31 | 3.7 GB |
| marker | Good (reads text well, confuses some table entries, gets most checkboxes correct) | CPU: 229<br>MPS: 212<br>GPU: X | 11.8 GB |
| MinerU | Good (reads text well, gets table entries correct, doesn't read checkboxes correctly) | CPU: 160<br>MPS: 50<br>GPU: 42 | 4.3 GB |
| Document Intelligence | Very good (reads text well, gets table entries correct, gets some checkboxes correct) | 8 | 70 MB (processing happens in cloud) |

### NIST Handwriting Sample

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (mistakes most text for images) | CPU: 3<br>MPS: 4<br>GPU: 10 | 1.4 GB |
| Docling - EasyOCR | Poor (mistakes most text for images) | CPU: 12<br>MPS: 6<br>GPU: 7 | 11.2 GB |
| Docling - RapidOCR | Poor (mistakes most text for images) | CPU: 18<br>MPS: 16<br>GPU: 4 | 2.9 GB |
| Docling - suryaocr | Poor (mistakes most text for images) | CPU: 48<br>MPS: 46<br>GPU: 8 | 1.8 GB |
| marker | Poor (mistakes half of the form for image, reads out remaining text well) | CPU: 31<br>MPS: 39<br>GPU: 5 | 7.8 GB |
| MinerU | Poor (misses text and makes mistakes, does not align captions with content well) | CPU: 25<br>MPS: 16<br>GPU: 16 | 4.6 GB |
| Document Intelligence | Good (reads all handwriting and text well, does not align captions with contents well) | 5 | 46 MB (processing happens in cloud) |

### World Food Bank 2020 Annual Report

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (reads text well, mistakes table of content for image, gets double column layout mostly correct, mistakes tables for images) | CPU: 30<br>MPS: 29<br>GPU: 50 | 8 GB |
| Docling - EasyOCR | Medium (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables mostly correct) | CPU: 166<br>MPS: 54<br>GPU: 41 | 13 GB |
| Docling - RapidOCR | Good (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables correct) | CPU: 227<br>MPS: 200<br>GPU: 28 | 6.5 GB |
| Docling - suryaocr | Good (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables correct) | CPU: 370<br>MPS: 358<br>GPU: 49 | 7.8 GB |
| marker | Good (reads text well, misses page numbers in table of contents, gets double column layout mostly correct, gets table entries correct) | CPU: 193<br>MPS: 168<br>GPU: 35 | 11.2 GB |
| MinerU | Good (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables correct) | CPU: 263<br>MPS: 130<br>GPU: 60 | 4.4 GB |
| Document Intelligence | Very good (reads text well, gets table of contents correct, gets double column layout mostly correct, gets table entries correct) | 14 | 64 MB (processing happens in cloud) |

### RKI: Epidemiologisches Bulletin

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Good (reads text well, gets table of contents correct, does not structure table well) | CPU: 70<br>MPS: 68<br>GPU: 101 | 7.1 GB |
| Docling - EasyOCR | Very good (reads text well, gets table of contents correct, gets table entries correct) | CPU: 241<br>MPS: 108<br>GPU: 95 | 14 GB |
| Docling - RapidOCR | Very good (reads text well, gets table of contents correct, gets table entries correct) | CPU: 542<br>MPS: 511<br>GPU: 52 | 6.4 GB |
| Docling - suryaocr | Very good (reads text well, gets table of contents correct, gets table entries correct) | CPU: 712<br>MPS: 704<br>GPU: 270 | 8.2 GB |
| marker | Medium (reads text well, gets table of contents correct, mixes up table entries) | CPU: 479<br>MPS: 617<br>GPU: 143 | 12.1 GB |
| MinerU | Very good (reads text well, gets table of contents partially correct, gets table entries correct) | CPU: 544<br>MPS: 156<br>GPU: 88 | 4.8 GB |
| Document Intelligence | Very good (reads text well, gets table of contents correct, gets table entries correct) | 10 | 96 MB (processing happens in cloud) |