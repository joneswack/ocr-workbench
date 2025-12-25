import os
from logging import Logger, getLogger
from pathlib import Path
from typing import Annotated, Any, Literal

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
from utils import load_json_config, monitor_resources, save_text_to_file, setup_logger

logger: Logger = getLogger(__name__)


def _get_rapidocr_config(config: dict[str, Any]) -> RapidOcrOptions:
    """Create RapidOCR configuration with model paths."""
    base_path = Path(config["modelscope_model_cache_dir"])
    return RapidOcrOptions(
        force_full_page_ocr=config["force_full_page_ocr"],
        lang=config["rapidocr_langs"],
        det_model_path=str(base_path / config["rapidocr_det_model_rel_path"]),
        rec_model_path=str(base_path / config["rapidocr_rec_model_rel_path"]),
        cls_model_path=str(base_path / config["rapidocr_cls_model_rel_path"]),
    )


def get_ocr_options_map(config: dict[str, Any]) -> dict[str, OcrOptions]:
    """Create map of OCR options based on provided configuration."""
    return {
        "tesseract": TesseractOcrOptions(
            force_full_page_ocr=config["force_full_page_ocr"],
            lang=config["tesseract_langs"],
        ),
        "easyocr": EasyOcrOptions(
            force_full_page_ocr=config["force_full_page_ocr"],
            lang=config["easyocr_langs"],
        ),
        "suryaocr": SuryaOcrOptions(
            force_full_page_ocr=config["force_full_page_ocr"],
            lang=config["suryaocr_langs"],
        ),
        "rapidocr": _get_rapidocr_config(config),
    }


def _get_pdf_pipeline_options(
    config: dict[str, Any],
    ocr_method: str,
    accelerator_device: AcceleratorDevice,
) -> PdfPipelineOptions:
    """Create PDF pipeline options with OCR and accelerator configurations."""
    ocr_options: OcrOptions = get_ocr_options_map(config)[ocr_method]
    accelerator_options = AcceleratorOptions(
        num_threads=config["num_threads"], device=accelerator_device
    )

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
    input_file: str | Path,
    config: dict[str, Any],
    ocr_method: str,
    accelerator_device: str,
) -> str:
    """Convert a document to markdown using the provided pipeline options."""

    # Set TESSDATA_PREFIX environment variable for Tesseract OCR
    os.environ.setdefault("TESSDATA_PREFIX", config["tesseract_data_path"])

    pipeline_options: PdfPipelineOptions = _get_pdf_pipeline_options(
        config=config,
        ocr_method=ocr_method,
        accelerator_device=AcceleratorDevice(accelerator_device),
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    logger.info(f"Processing file: {input_file}")

    try:
        conversion_result: ConversionResult = doc_converter.convert(source=input_file)
        return conversion_result.document.export_to_markdown()
    except Exception:
        logger.exception("Failed to convert source %s", input_file)
        return ""


def main(
    input_file: Annotated[Path, typer.Option()],
    output_dir: Annotated[Path, typer.Option()],
    ocr_method: Annotated[
        Literal["tesseract", "easyocr", "suryaocr", "rapidocr"], typer.Option()
    ],
    accelerator_device: Annotated[Literal["cpu", "mps", "cuda"], typer.Option()],
) -> None:
    """Main function to run the OCR experiment.

    Args:
        input_file: Path to input PDF file.
        output_dir: Directory to save output markdown to.
        ocr_method: OCR engine to use.
        accelerator_device: Accelerator device.
    """
    setup_logger(
        logger=logger,
        output_path=output_dir / f"{input_file.stem}_{accelerator_device}.log",
    )
    config: dict[str, Any] = load_json_config(
        config_path=Path(__file__).parent / "config.json"
    )

    with monitor_resources(logger=logger):
        markdown_content: str = convert_document_to_markdown(
            input_file=input_file,
            config=config,
            ocr_method=ocr_method,
            accelerator_device=accelerator_device,
        )

    save_text_to_file(
        text=markdown_content,
        output_path=output_dir / f"{input_file.stem}.md",
    )


if __name__ == "__main__":
    typer.run(main)
