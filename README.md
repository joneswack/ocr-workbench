# OCR Workbench

OCR Workbench is a ready-to-use framework for easily comparing popular OCR libraries in Python. It abstracts away the individual setup and usage details of each library, allowing you to focus on evaluating results on your data rather than spending time implementing each method yourself.

Simply provide a collection of PDF files and run the experiments.
Then select a library for your use case that gives the best evaluation results.

Currently, the following libraries are supported:
- [Docling](https://docling-project.github.io/docling/) including tesseract, EasyOCR, RapidOCR, surya
- [MinerU](https://opendatalab.github.io/MinerU/)
- [Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence)

Features:
- Executable code setup for the above libraries
- Automatic conversion of all provided PDF files in ``data/input`` into markdown using all methods
- Hardware acceleration using CPU, MPS and CUDA
- Time and cpu-memory tracking for each method

## Why do we still care about OCR?

Scanned documents are essentially collections of images stored in PDF format. While easy to view and share, their text content is not machine-readable by default. Extracting this text requires specialized machine learning techniques. Optical Character Recognition (OCR) converts text in images into structured, machine-readable data that can be reliably used for tasks such as document search, analysis, and automated processing.

**Aren't VLMs much better than OCR engines?**

Vision-Language Models (VLMs) can read text in images and even understand image semantics, but their outputs are inherently non-deterministic. This lack of reproducibility—along with the risk of hallucinated or missing text output—often makes them unsuitable for production and regulated environments. As of today, OCR engines are still the preferred choice by many companies in these scenarios. This repository focuses on OCR methods only. Future work may focus on VLMs instead.

## Installation

Since the dependencies of different OCR libraries can have conflicts, we use a separate Python environment per OCR library. Each one uses [uv](https://docs.astral.sh/uv/) as a dependency manager. Make sure to install uv before moving on.

Set up the respective environment using:
```console
cd <environment-name>
uv sync
```
where ``<environment-name>`` is one of ``docling_environment``, ``mineru_environment``, ``azure_environment``.

For docling with tesseract OCR, tesseract needs to be installed:
```console
# Ubuntu:
sudo apt install tesseract-ocr-all
# Via brew on Mac OS:
brew install tesseract
brew install tesseract-lang
```

Additionally, the correct paths for the tesseract and modelscope (used by RapidOCR) directories need to be set in ``docling_environment/config.json``.

## Running experiments

Place some PDF files to be parsed in ``data/input``.

Then run:

```console
cd <environment-name>
sh run_experiments.sh -a <accelerator>
```

where ``<accelerator>`` is one of ``cpu``, ``mps``, ``cuda``.

By default, the script processes all PDF files in ``data/input``.

If you want to run a single experiment instead, run the following:

```console
cd <environment-name>
sh run_experiments.sh -i <input-file> -a <accelerator>
```

The markdown output is stored in ``data/output/<ocr-method>/<file-name>.md``.

In order to visualize CPU memory over time, run:
```console
mprof plot ../data/output/<ocr-method>/<file-name>_mem_cpu.dat
```

For docling, there exists an additional ``config.json`` file with some preconfigured defaults. You can change it based on your needs. In particular, you can select the OCR engines to compare.

## Evaluation on a few sample documents

We produced OCR outputs for four example documents and compared them in terms of OCR quality as well as OCR resource consumption.

The following publicly available PDFs were used and saved in ``data/input``:
- [Information About Coca-Cola Volume Growth](https://www.industrydocuments.ucsf.edu/all-industries/documents/viewer/?iid=lxpj0226&id=lxpj0226&q=%5Bobject+Object%5D&db-set=documents&sort=&pg=1&npp=20&industry=all-industries&rtool=download)
- [Handwriting Sample from NIST Special Database 19](https://www.nist.gov/srd/nist-special-database-19)*
- [2020 Annual Report Midwest Food Bank](https://midwestfoodbank.org/images/AR_2020_WEB2.pdf)
- [RKI: Epidemiologisches Bulletin](https://www.rki.de/DE/Aktuelles/Publikationen/Epidemiologisches-Bulletin/2025/50_25.pdf?__blob=publicationFile&v=8) (German)

\* the sample image was saved as a PDF file.

Speed is measured on a Macbook Air M4 for CPU and MPS, and on an NVIDIA X for CUDA.
Memory usage is measured only once for CPU.
OCR quality is subjectively graded and compared based on the markdown output stored in ``data/output/<ocr-method>/<file-name>.md``.

### Information About Coca-Cola Volume Growth

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (misses text, confuses table entries, doesn't read checkboxes correctly) | CPU: 34<br>MPS: 34 | 3 GB |
| Docling - EasyOCR | Medium (reads text well, confuses some table entries, doesn't read checkboxes correctly) | CPU: 129<br>MPS: 52 | 11.4 GB |
| Docling - suryaocr | Very good (reads text well, gets table entries correct, gets most checkboxes correct) | CPU: 369<br>MPS: 379 | 3.7 GB |
| Docling - RapidOCR | Good (reads text well, gets table entries correct, gets some checkboxes correct) | CPU: 161<br>MPS: 160 | 6.4 GB |
| MinerU | Good (reads text well, gets table entries correct, doesn't read checkboxes correctly) | CPU: 160<br>MPS: 50 | 4.3 GB |
| Document Intelligence | Very good (reads text well, gets table entries correct, gets some checkboxes correct) | 8 | 70 MB |
