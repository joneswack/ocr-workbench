import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from typing import Annotated, Any, Literal

import psutil
import typer
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_surya import SuryaOcrOptions

logger: Logger = logging.getLogger(__name__)


def _get_rapidocr_config(config: dict[str, Any]) -> RapidOcrOptions:
    """Create RapidOCR configuration with model paths."""
    base_path = Path(config["modelscope_model_cache_dir"])
    return RapidOcrOptions(
        force_full_page_ocr=False,
        det_model_path=str(base_path / config["rapidocr_det_model_rel_path"]),
        rec_model_path=str(base_path / config["rapidocr_rec_model_rel_path"]),
        cls_model_path=str(base_path / config["rapidocr_cls_model_rel_path"]),
    )


def get_ocr_config_map(config: dict[str, Any]) -> dict[str, OcrOptions]:
    """Create OCR configurations with the provided modelscope cache directory."""
    return {
        "tesseract": TesseractOcrOptions(
            force_full_page_ocr=False, lang=["fra", "deu", "spa", "eng"]
        ),
        "easyocr": EasyOcrOptions(force_full_page_ocr=False),
        "rapidocr": _get_rapidocr_config(config),
        "suryaocr": SuryaOcrOptions(force_full_page_ocr=False),
    }


ACCELERATOR_CONFIGS: dict[str, AcceleratorOptions] = {
    "cpu": AcceleratorOptions(num_threads=10, device=AcceleratorDevice.CPU),
    "mps": AcceleratorOptions(num_threads=10, device=AcceleratorDevice.MPS),
}


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from JSON file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def setup_environment(config: dict[str, Any]) -> None:
    """Configure environment variables based on config."""
    os.environ.setdefault("TESSDATA_PREFIX", config["tessdata_prefix"])


def get_pdf_pipeline_options(
    ocr_options: OcrOptions, accelerator_options: AcceleratorOptions
) -> PdfPipelineOptions:
    """Create PDF pipeline options with OCR and accelerator configurations."""
    additional_options: dict[str, Any] = {}
    if isinstance(ocr_options, SuryaOcrOptions):
        additional_options["ocr_model"] = "suryaocr"

    return PdfPipelineOptions(
        do_ocr=True,
        do_table_structure=True,
        ocr_options=ocr_options,
        accelerator_options=accelerator_options,
        allow_external_plugins=True,
        **additional_options,
    )


def convert_document_to_markdown(
    pipeline_options: PdfPipelineOptions, source: str | Path
) -> str:
    """Convert a document to markdown using the provided pipeline options."""
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    try:
        conversion_result: ConversionResult = doc_converter.convert(source=source)
        return conversion_result.document.export_to_markdown()
    except Exception:
        logger.exception("Failed to convert source %s", source)
        return ""


def save_markdown_to_file(output_path: Path, markdown_content: str) -> None:
    """Save markdown content to a file in the specified output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_content)
    logger.info("Wrote markdown: %s", output_path)


@contextmanager
def print_memory_usage(poll_interval: float = 0.01):
    """Context manager to monitor and print peak memory usage."""
    process = psutil.Process(os.getpid())
    peak_rss: float = 0.0
    stop_event = threading.Event()

    def monitor():
        nonlocal peak_rss
        while not stop_event.is_set():
            rss = process.memory_info().rss
            peak_rss = max(peak_rss, rss)
            time.sleep(poll_interval)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    try:
        yield
    finally:
        stop_event.set()
        monitor_thread.join()
        logger.info("Peak RSS: %.2f MB", peak_rss / 1024**2)


def main(
    ocr: Annotated[
        Literal["tesseract", "easyocr", "rapidocr", "suryaocr"], typer.Option()
    ],
    accelerator: Annotated[Literal["cpu", "mps"], typer.Option()],
    input: Annotated[str, typer.Option()],
    output_dir: Annotated[str, typer.Option()],
) -> None:
    """Main function to run the OCR experiment.

    Args:
        ocr: OCR engine to use.
        accelerator: Accelerator type (cpu or mps).
        input: Path to input PDF file.
        output_dir: Directory to save output markdown.
    """
    output_dir_path: Path = Path(output_dir)
    input_path: Path = Path(input)

    handler = logging.FileHandler(
        filename=output_dir_path / f"{input_path.stem}_{accelerator}.log",
        mode="w",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    config_path: Path = Path(__file__).parent / "config.json"
    config: dict[str, Any] = load_config(config_path)
    setup_environment(config)

    ocr_config_map: dict[str, OcrOptions] = get_ocr_config_map(config)
    ocr_options: OcrOptions = ocr_config_map[ocr]

    accelerator_options: AcceleratorOptions = ACCELERATOR_CONFIGS[accelerator]

    logger.info(f"Processing file: {input_path}")
    start_time: float = time.time()

    pipeline_options: PdfPipelineOptions = get_pdf_pipeline_options(
        ocr_options=ocr_options,
        accelerator_options=accelerator_options,
    )

    with print_memory_usage():
        markdown_content: str = convert_document_to_markdown(
            pipeline_options=pipeline_options, source=input_path
        )

    save_markdown_to_file(
        output_path=output_dir_path / f"{input_path.stem}.md",
        markdown_content=markdown_content,
    )

    elapsed_time: float = time.time() - start_time
    logger.info("Processing completed. Time taken: %.2f seconds", elapsed_time)


if __name__ == "__main__":
    typer.run(main)
