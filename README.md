Relevant Datasets

- Neuralabs German OCR
https://huggingface.co/datasets/neuralabs/german-synth-ocr

- OCRBench v2
https://arxiv.org/abs/2501.00321

- [CVPR 2025] A Comprehensive Benchmark for Document Parsing and Evaluation
https://github.com/opendatalab/OmniDocBench

- University of San Francisco All Industries - Documents
https://www.industrydocuments.ucsf.edu/all-industries/documents/viewer/?iid=lxpj0226&id=lxpj0226&q=%5Bobject+Object%5D&db-set=documents&sort=&pg=1&npp=20&industry=all-industries&rtool=download

# OCR Workbench

OCR Workbench is a ready-to-use framework for easily comparing popular OCR libraries in Python. It abstracts away the individual setup and usage details of each library, allowing you to focus on evaluating results on your data rather than spending time implementing each method yourself.

Simply provide a collection of PDF files and run the experiments.
Then select the library that works best for your use case.

Currently, the following libraries are supported:
- [Docling](https://docling-project.github.io/docling/) including tesseract, EasyOCR, RapidOCR, surya
- [MinerU](https://opendatalab.github.io/MinerU/)
- [Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence)

Features:
- Prepared code setups for the above libraries
- Automatic conversion of all provided PDF files into markdown
- Memory and time tracking

## Why do we still care about OCR?

Scanned documents are essentially collections of images stored in PDF format. While easy to view and share, their text content is not machine-readable by default. Extracting this text requires specialized machine learning techniques. Optical Character Recognition (OCR) converts text in images into structured, machine-readable data that can be reliably used for tasks such as document search, analysis, and automated processing.

**What about VLMs?**
Vision-Language Models (VLMs) can read and interpret text in images, but their outputs are inherently non-deterministic. This lack of reproducibility—along with the risk of hallucinated or missing text—often makes them unsuitable for production and regulated environments.

## Installation

Since the dependencies of different OCR libraries can have conflicts, we have one Python environment per OCR library. All of them use uv as a dependency manager. Make sure to have installed it as a prerequisite.

Setup the respective environment using:
```console
cd <environment-name>
uv sync
```

For docling with tesseract OCR, tesseract needs to be installed:
```console
# Ubuntu:
sudo apt install tesseract-ocr-all
# Via brew on Mac OS:
brew install tesseract
brew install tesseract-lang
```

Additionally, the correct paths for the tesseract and modelscope directories need to be set in ``docling_environment/config.json``.

## Running experiments

Place some PDF files to be parsed in ``data/input``.

Then run:

```console
cd <environment-name>
sh run_experiments.sh -a [cpu|mps|cuda]
```

The argument ``[cpu|mps|cuda]`` determines the accelerator on which to run the experiments.
By default, the script processes all PDF files in ``data/input``.

If you want to run a single experiment instead, run the following:

```console
cd <environment-name>
sh run_experiments.sh -i <input-file> -a [cpu|mps|cuda]
```

The markdown output can then be found in ``data/output/<method-name>/<file-name>.md``.

For docling, there exists an additional ``config.json`` file with some preconfigured defaults. You can change it based on your needs. In particular, you can select the OCR engines to compare.

## Some sample results

The following publicly available PDFs were placed in ``data/input``:
- [Information About Coca-Cola Volume Growth](https://www.industrydocuments.ucsf.edu/all-industries/documents/viewer/?iid=lxpj0226&id=lxpj0226&q=%5Bobject+Object%5D&db-set=documents&sort=&pg=1&npp=20&industry=all-industries&rtool=download)
- [Handwriting Sample from NIST Special Database 19](https://www.nist.gov/srd/nist-special-database-19)*
- [2020 Annual Report Midwest Food Bank](https://midwestfoodbank.org/images/AR_2020_WEB2.pdf)
- [RKI: Epidemiologisches Bulletin (German)](https://www.rki.de/DE/Aktuelles/Publikationen/Epidemiologisches-Bulletin/2025/50_25.pdf?__blob=publicationFile&v=8)

* the sample image was saved as a PDF file.

### Information About Coca-Cola Volume Growth

| OCR-Library          | Text | Tables | Forms | Charts | Speed \[seconds\] | Resource Consumption |
|----------------------|------|--------|-------|--------|-------------------|----------------------|
| Docling - Tesseract  | Poor | Poor   | Poor  | Poor   | CPU: 34, MPS: X   | 1685 MB              |
