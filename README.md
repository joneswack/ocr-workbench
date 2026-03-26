# OCR Workbench

OCR Workbench is a ready-to-use framework for easily comparing popular OCR libraries in Python. It abstracts away the individual setup and usage details of each library, allowing you to focus on evaluating results on your data rather than spending time implementing each method yourself.

Simply provide a collection of PDF files and compare all libraries using a single script.

## Supported Libraries

Currently, the following libraries are supported:
- [Docling](https://docling-project.github.io/docling/) including tesseract, EasyOCR, RapidOCR, surya, Granite
- [MinerU](https://opendatalab.github.io/MinerU/)
- [Marker](https://github.com/datalab-to/marker)
- [Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence)
- [LightOnOCR-2-1B](https://huggingface.co/lightonai/LightOnOCR-2-1B)
- [Chandra OCR 2](https://github.com/datalab-to/chandra)

This selection focuses on benchmarking open source libraries against proprietary Azure Document Intelligence.

**Features**
- Running experiments with the above libraries via a single script
- Automatic conversion of all provided PDF files in ``data/input`` into markdown using all methods
- Hardware acceleration using CPU, MPS and CUDA
- Time and cpu-memory tracking for each method

## Qualitative Evaluation on 4 Sample Documents

Using our script, we produced OCR outputs for four example documents and compared them in terms of OCR quality as well as resource consumption.

The following publicly available PDFs were used:
- [Information About Coca-Cola Volume Growth](https://www.industrydocuments.ucsf.edu/all-industries/documents/viewer/?iid=lxpj0226&id=lxpj0226&q=%5Bobject+Object%5D&db-set=documents&sort=&pg=1&npp=20&industry=all-industries&rtool=download)
- [Handwriting Sample from NIST Special Database 19](https://www.nist.gov/srd/nist-special-database-19) (the sample image was saved as a PDF file)
- [2020 Annual Report Midwest Food Bank](https://midwestfoodbank.org/images/AR_2020_WEB2.pdf)
- [RKI: Epidemiologisches Bulletin](https://www.rki.de/DE/Aktuelles/Publikationen/Epidemiologisches-Bulletin/2025/50_25.pdf?__blob=publicationFile&v=8) (German)

Speed is measured on a Macbook Air M4 for CPU and MPS, and on an NVIDIA RTX 5090 GPU (32 GB VRAM).
Memory usage is measured only once for CPU.
OCR quality is subjectively graded and compared based on the markdown output stored in ``data/output/<ocr-method>/<file-name>.md``.

### Summary

The following table summarizes the comparison of all methods on all PDFs. Extraction quality (Excellent, Very good, Good, Medium, Poor) and GPU extraction speed in seconds are shown, as well as cost per page when running on an NVIDIA RTX 5090 GPU hosted on [runpod.io](https://www.runpod.io/) for 89ct/hour. We did not carry out any specific runtime optimizations for any method.

<table>
  <thead>
    <tr>
      <th>OCR-Library</th>
      <th>Coca-Cola</th>
      <th>NIST Handwriting</th>
      <th>World Food Bank</th>
      <th>RKI Bulletin (German)</th>
      <th>Cost / page</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>LightOnOCR-2-1B</td>
      <td>🏆 <strong>Excellent</strong> (192s)</td>
      <td>🏆 <strong>Excellent</strong> (23s)</td>
      <td>🏆 <strong>Excellent</strong> (191s)</td>
      <td>🏆 <strong>Excellent</strong> (416s)</td>
      <td>0.5 ct</td>
    </tr>
    <tr>
      <td>Chandra OCR 2</td>
      <td>🏆 <strong>Excellent</strong> (376s)</td>
      <td>🏆 <strong>Excellent</strong> (120s)</td>
      <td>🏆 <strong>Excellent</strong> (476s)</td>
      <td>🏆 <strong>Excellent</strong> (863s)</td>
      <td>1.4 ct</td>
    </tr>
    <tr>
      <td>Document Intelligence</td>
      <td>🟢 Very good (8s)</td>
      <td>🟢 Good (5s)</td>
      <td>🟢 Very good (14s)</td>
      <td>🏆 <strong>Excellent</strong> (10s)</td>
      <td>1 ct</td>
    </tr>
    <tr>
      <td>Docling - suryaocr</td>
      <td>🟢 Very good (31s)</td>
      <td>🔴 Poor (8s)</td>
      <td>🟢 Good (49s)</td>
      <td>🟢 Very good (270s)</td>
      <td>0.17 ct</td>
    </tr>
    <tr>
      <td>Docling - RapidOCR</td>
      <td>🟢 Good (12s)</td>
      <td>🔴 Poor (4s)</td>
      <td>🟢 Good (28s)</td>
      <td>🟢 Very good (52s)</td>
      <td><strong>0.06 ct</strong></td>
    </tr>
    <tr>
      <td>MinerU</td>
      <td>🟢 Good (42s)</td>
      <td>🔴 Poor (16s)</td>
      <td>🟢 Good (60s)</td>
      <td>🟢 Very good (88s)</td>
      <td>0.17 ct</th>
    </tr>
    <tr>
      <td>marker</td>
      <td>🟢 Good (29)</td>
      <td>🔴 Poor (5s)</td>
      <td>🟢 Good (35s)</td>
      <td>🟡 Medium (143s)</td>
      <td>0.11 ct</td>
    </tr>
    <tr>
      <td>Docling - Granite</td>
      <td>🔴 Poor (343s)</td>
      <td>🟡 Medium (108s)</td>
      <td>🔴 Poor (171s)</td>
      <td>🟢 Good (597s)</td>
      <td>1.16 ct</td>
    </tr>
    <tr>
      <td>Docling - EasyOCR</td>
      <td>🟡 Medium (37s)</td>
      <td>🔴 Poor (7s)</td>
      <td>🟡 Medium (41s)</td>
      <td>🟢 Very good (95s)</td>
      <td>0.11 ct</td>
    </tr>
    <tr>
      <td>Docling - Tesseract</td>
      <td>🔴 Poor (32s)</td>
      <td>🔴 Poor (10s)</td>
      <td>🔴 Poor (50s)</td>
      <td>🟢 Good (101s)</td>
      <td>0.13 ct</td>
    </tr>
  </tbody>
</table>

We can see that the open weights models LightOnOCR-2-1B and Chandra OCR 2 yield the best results. In the case of LightOnOCR-2-1B this is impressive, since it means that an open weights model can be used to save costs without sacrificing on extraction quality! The proprietary Azure Document Intelligence yields second-best results and has the highest speed, at least when compared against an NVIDIA RTX 5090 GPU. RapidOCR was the fastest open source alternative and therefore the cheapest model in our experiments.

Especially when extraction speed does not matter as much (e.g., in offline computation settings), open source methods can be a much cheaper alternative. Moreover, more powerful GPUs (H100 or better) could be used to catch up with Document Intelligence speed. Frameworks like [vLLM](https://docs.vllm.ai/en/latest/) and specifically compiled modules like [FlashAttention](https://github.com/dao-ailab/flash-attention) can then be used to further optimize inference speed.

Details about the qualitative evaluation can be found in the [qualitative evaluation details](#quatlitative-evaluation-details).

## Why do we still care about OCR?

Scanned documents are essentially collections of images stored in PDF format. While easy to view and share, their text content is not machine-readable by default. Extracting this text requires specialized machine learning techniques. Optical Character Recognition (OCR) converts text in images into structured, machine-readable data that can be reliably used for tasks such as document search, analysis, and automated processing.

In this repository, we compare open source OCR engines against proprietary ones. We also include VLM based approaches.

## Installation

Since the dependencies of different OCR libraries can have conflicts, we use a separate Python environment per OCR library. Each one uses [uv](https://docs.astral.sh/uv/) as a dependency manager. Make sure to install uv before moving on.

Set up the respective environment using:
```console
cd <environment-name>
uv sync
```
where ``<environment-name>`` is one of ``docling_environment``, ``marker_environment``, ``mineru_environment``, ``azure_environment``, ``lighton_environment``.

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

In order to use Azure Document Intelligence, you need to set up an account on Microsoft Azure and create a [Document Intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence) resource. Then place the endpoint URL and API key in `docint_environment/config.json`.

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

## Quatlitative Evaluation Details

### Information About Coca-Cola Volume Growth

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (misses text, confuses table entries, doesn't read checkboxes correctly) | CPU: 34<br>MPS: 34<br>GPU: 32 | 3 GB |
| Docling - EasyOCR | Medium (reads text well, confuses some table entries, doesn't read checkboxes correctly) | CPU: 129<br>MPS: 52<br>GPU: 37 | 11.4 GB |
| Docling - RapidOCR | Good (reads text well, gets table entries correct, doesn't read checkboxes correctly) | CPU: 161<br>MPS: 160<br>GPU: 12 | 6.4 GB |
| Docling - suryaocr | Very good (reads text well, gets table entries correct, gets most checkboxes correct) | CPU: 369<br>MPS: 337<br>GPU: 31 | 3.7 GB |
| Docling - Granite | Poor (misses great share of text, gets table entries correct, misses checkboxes) | CPU: 1564<br>MPS: 313<br>GPU: 343 | 5.8 GB |
| marker | Good (reads text well, confuses some table entries, gets most checkboxes correct) | CPU: 229<br>MPS: 212<br>GPU: 29 | 11.8 GB |
| MinerU | Good (reads text well, gets table entries correct, doesn't read checkboxes correctly) | CPU: 160<br>MPS: 50<br>GPU: 42 | 4.3 GB |
| Document Intelligence | Very good (reads text well, gets table entries correct, gets some checkboxes correct) | 8 | 70 MB (processing happens in cloud) |
| LightOnOCR-2-1B | Excellent (reads text well, gets table entries correct, gets all checkboxes correct) | CPU: 1828<br>MPS: 1993<br>GPU: 192 | 15.7 GB |
| Chandra OCR 2 | Excellent (reads text well, gets table entries correct, gets all checkboxes correct) | CPU: X<br>MPS: X<br>GPU: 376 | OOM on MacBook Air M4 |

### NIST Handwriting Sample

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (mistakes most text for images) | CPU: 3<br>MPS: 4<br>GPU: 10 | 1.4 GB |
| Docling - EasyOCR | Poor (mistakes most text for images) | CPU: 12<br>MPS: 6<br>GPU: 7 | 11.2 GB |
| Docling - RapidOCR | Poor (mistakes most text for images) | CPU: 18<br>MPS: 16<br>GPU: 4 | 2.9 GB |
| Docling - suryaocr | Poor (mistakes most text for images) | CPU: 48<br>MPS: 46<br>GPU: 8 | 1.8 GB |
| Docling - Granite | Medium (recognizes around half the text correctly) | CPU: 164<br>MPS: 7<br>GPU: 108 | 1.5 GB |
| marker | Poor (mistakes half of the form for image, reads out remaining text well) | CPU: 31<br>MPS: 39<br>GPU: 5 | 7.8 GB |
| MinerU | Poor (misses text and makes mistakes, does not align captions with content well) | CPU: 25<br>MPS: 16<br>GPU: 16 | 4.6 GB |
| Document Intelligence | Good (reads all handwriting and text well, does not align captions with contents well) | 5 | 46 MB (processing happens in cloud) |
| LightOnOCR-2-1B | Excellent (reads all handwriting and text well, aligns all form contents perfectly) | CPU: 170<br>MPS: 168<br>GPU: 23 | 12.4 GB |
| Chandra OCR 2 | Excellent (reads all handwriting and text well, aligns all form contents perfectly) | CPU: X<br>MPS: X<br>GPU: 120 | OOM on MacBook Air M4 |

### World Food Bank 2020 Annual Report

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Poor (reads text well, mistakes table of content for image, gets double column layout mostly correct, mistakes tables for images) | CPU: 30<br>MPS: 29<br>GPU: 50 | 8 GB |
| Docling - EasyOCR | Medium (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables mostly correct) | CPU: 166<br>MPS: 54<br>GPU: 41 | 13 GB |
| Docling - RapidOCR | Good (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables correct) | CPU: 227<br>MPS: 200<br>GPU: 28 | 6.5 GB |
| Docling - suryaocr | Good (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables correct) | CPU: 370<br>MPS: 358<br>GPU: 49 | 7.8 GB |
| Docling - Granite | Poor (reads text well but often swallows it, gets table of contents correct, gets double layout sometimes correct, misses tables) | CPU: 838<br>MPS: 127<br>GPU: 171 | 1.8 GB |
| marker | Good (reads text well, misses page numbers in table of contents, gets double column layout mostly correct, gets table entries correct) | CPU: 193<br>MPS: 168<br>GPU: 35 | 11.2 GB |
| MinerU | Good (reads text well, gets table of contents mostly correct, gets double column layout mostly correct, gets tables correct) | CPU: 263<br>MPS: 130<br>GPU: 60 | 4.4 GB |
| Document Intelligence | Very good (reads text well, gets table of contents correct, gets double column layout mostly correct, gets table entries correct) | 14 | 64 MB (processing happens in cloud) |
| LightOnOCR-2-1B | Excellent (reads text well, gets table of contents correct, gets double column layout correct, gets table entries correct) | CPU: 2440<br>MPS: 1881<br>GPU: 191 | 15 GB |
| Chandra OCR 2 | Excellent (reads text well, gets table of contents correct, gets double column layout correct, gets table entries correct) | CPU: X<br>MPS: X<br>GPU: 476 | OOM on MacBook Air M4 |

### RKI: Epidemiologisches Bulletin

| OCR-Library | Extraction Quality | Speed \[seconds\] | CPU Memory Usage |
|-------------|--------------------|-------------------|------------------|
| Docling - Tesseract | Good (reads text well, gets table of contents correct, does not structure table well) | CPU: 70<br>MPS: 68<br>GPU: 101 | 7.1 GB |
| Docling - EasyOCR | Very good (reads text well, gets table of contents correct, gets table entries correct) | CPU: 241<br>MPS: 108<br>GPU: 95 | 14 GB |
| Docling - RapidOCR | Very good (reads text well, gets table of contents correct, gets table entries correct) | CPU: 542<br>MPS: 511<br>GPU: 52 | 6.4 GB |
| Docling - suryaocr | Very good (reads text well, gets table of contents correct, gets table entries correct) | CPU: 712<br>MPS: 704<br>GPU: 270 | 8.2 GB |
| Docling - Granite | Good (reads text well, gets table of contents correct, misses some tables) | CPU: 153<br>MPS: 152<br>GPU: 597 | 1.7 GB |
| marker | Medium (reads text well, gets table of contents correct, mixes up table entries) | CPU: 479<br>MPS: 617<br>GPU: 143 | 12.1 GB |
| MinerU | Very good (reads text well, gets table of contents partially correct, gets table entries correct) | CPU: 544<br>MPS: 156<br>GPU: 88 | 4.8 GB |
| Document Intelligence | Excellent (reads text well, gets table of contents correct, gets table entries correct) | 10 | 96 MB (processing happens in cloud) |
| LightOnOCR-2-1B | Excellent (reads text well, gets table of contents correct, gets table entries correct) | CPU: 4187<br>MPS: 3987<br>GPU: 416 | 14.9 GB |
| Chandra OCR 2 | Excellent (reads text well, gets table of contents correct, gets table entries correct) | CPU: X<br>MPS: X<br>GPU: 863 | OOM |
