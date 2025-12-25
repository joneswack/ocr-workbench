Relevant Datasets

- Neuralabs German OCR
https://huggingface.co/datasets/neuralabs/german-synth-ocr

- OCRBench v2
https://arxiv.org/abs/2501.00321

- [CVPR 2025] A Comprehensive Benchmark for Document Parsing and Evaluation
https://github.com/opendatalab/OmniDocBench

- University of San Francisco All Industries - Documents
https://www.industrydocuments.ucsf.edu/all-industries/documents/viewer/?iid=lxpj0226&id=lxpj0226&q=%5Bobject+Object%5D&db-set=documents&sort=&pg=1&npp=20&industry=all-industries&rtool=download

## Document X

| OCR-Engine | Text | Tables | Forms | Charts | Speed | Resource Consumption |
|------------|------|--------|-------|--------|-------|----------------------|
| Tesseract  | Poor | Poor   | Poor  | Poor   | 10 seconds  | X MB                 |

# Structure

I had to separate mineru_experiments from docling_experiments because SuryaOCR and MinerU were conflicting on pillow version.