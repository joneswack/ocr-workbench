"""This script is adapted from:
https://huggingface.co/spaces/lightonai/LightOnOCR-2-1B-Demo
"""

#!/usr/bin/env python3
import re
import sys
import time
from collections import OrderedDict
from pathlib import Path
from typing import Annotated, Literal, Optional

import pypdfium2 as pdfium
import torch
import typer
from transformers import (
    LightOnOcrForConditionalGeneration,
    LightOnOcrProcessor,
)

MODEL_REGISTRY = {
    "LightOnOCR-2-1B": {
        "model_id": "lightonai/LightOnOCR-2-1B",
        "has_bbox": False,
        "description": "Best overall OCR performance",
    },
    "LightOnOCR-2-1B-bbox": {
        "model_id": "lightonai/LightOnOCR-2-1B-bbox",
        "has_bbox": True,
        "description": "Best bounding box detection",
    },
    "LightOnOCR-2-1B-base": {
        "model_id": "lightonai/LightOnOCR-2-1B-base",
        "has_bbox": False,
        "description": "Base OCR model",
    },
    "LightOnOCR-2-1B-bbox-base": {
        "model_id": "lightonai/LightOnOCR-2-1B-bbox-base",
        "has_bbox": True,
        "description": "Base bounding box model",
    },
}

DEFAULT_MODEL = "LightOnOCR-2-1B"

device: str = "cpu"
attn_implementation: str = "eager"
dtype: torch.dtype = torch.float32


class ModelManager:
    """Manages model loading with LRU caching and GPU memory management."""

    def __init__(self, max_cached=2):
        self._cache = OrderedDict()
        self._max_cached = max_cached

    def get_model(self, model_name):
        config = MODEL_REGISTRY.get(model_name)
        if config is None:
            raise ValueError(
                f"Unknown model: {model_name}. Choose from: {list(MODEL_REGISTRY)}"
            )

        model_id = config["model_id"]

        if model_id in self._cache:
            self._cache.move_to_end(model_id)
            print(f"Using cached model: {model_name}", file=sys.stderr)
            return self._cache[model_id]

        while len(self._cache) >= self._max_cached:
            evicted_id, (evicted_model, _) = self._cache.popitem(last=False)
            print(f"Evicting model from cache: {evicted_id}", file=sys.stderr)
            del evicted_model
            if device == "cuda":
                torch.cuda.empty_cache()

        print(f"Loading model: {model_name} ({model_id})...", file=sys.stderr)
        model = (
            LightOnOcrForConditionalGeneration.from_pretrained(
                model_id,
                attn_implementation=attn_implementation,
                torch_dtype=dtype,
                trust_remote_code=True,
            )
            .to(device)
            .eval()
        )

        processor = LightOnOcrProcessor.from_pretrained(
            model_id, trust_remote_code=True
        )

        self._cache[model_id] = (model, processor)
        print(f"Model loaded: {model_name}", file=sys.stderr)
        return model, processor


model_manager = ModelManager(max_cached=2)


def render_pdf_page(page, max_resolution=1540, scale=2.77):
    """Render a PDF page to PIL Image."""
    width, height = page.get_size()
    pixel_width = width * scale
    pixel_height = height * scale
    resize_factor = min(1, max_resolution / pixel_width, max_resolution / pixel_height)
    target_scale = scale * resize_factor
    return page.render(scale=target_scale, rev_byteorder=True).to_pil()


def load_pdf_page(pdf_path, page_idx):
    """Return a PIL image for the given 0-based page index."""
    pdf = pdfium.PdfDocument(pdf_path)
    total_pages = len(pdf)
    page_idx = min(max(page_idx, 0), total_pages - 1)
    img = render_pdf_page(pdf[page_idx])
    pdf.close()
    return img, total_pages


def clean_output_text(text):
    """Remove chat template artifacts from output."""
    markers = {"system", "user", "assistant"}
    lines = [line for line in text.split("\n") if line.strip().lower() not in markers]
    cleaned = "\n".join(lines).strip()
    if "assistant" in text.lower():
        parts = text.split("assistant", 1)
        if len(parts) > 1:
            cleaned = parts[1].strip()
    return cleaned


BBOX_PATTERN = r"!\[image\]\((image_\d+\.png)\)\s*(\d+),(\d+),(\d+),(\d+)"


def parse_bbox_output(text):
    """Parse bbox output and return cleaned text with list of detections."""
    detections = []
    for match in re.finditer(BBOX_PATTERN, text):
        image_ref, x1, y1, x2, y2 = match.groups()
        detections.append(
            {"ref": image_ref, "coords": (int(x1), int(y1), int(x2), int(y2))}
        )
    cleaned = re.sub(BBOX_PATTERN, r"![image](\1)", text)
    return cleaned, detections


def extract_text_from_image(image, model_name, temperature=0.2, max_tokens=2048):
    """Extract text from a PIL image using a LightOnOCR model."""
    model, processor = model_manager.get_model(model_name)

    chat = [{"role": "user", "content": [{"type": "image", "url": image}]}]

    inputs = processor.apply_chat_template(
        chat,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    inputs = {
        k: v.to(device=device, dtype=dtype)
        if isinstance(v, torch.Tensor)
        and v.dtype in (torch.float32, torch.float16, torch.bfloat16)
        else v.to(device)
        if isinstance(v, torch.Tensor)
        else v
        for k, v in inputs.items()
    }

    generation_kwargs = dict(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=temperature if temperature > 0 else 0.0,
        top_p=0.9,
        top_k=0,
        use_cache=True,
        do_sample=temperature > 0,
    )

    with torch.no_grad():
        outputs = model.generate(**generation_kwargs)

    output_text = processor.decode(outputs[0], skip_special_tokens=True)
    return clean_output_text(output_text)


def process_pdf(pdf_path, pages, model_name, temperature, max_tokens, output_dir=None):
    """Run OCR on selected pages of a PDF and write results."""
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / (Path(pdf_path).stem + ".md")
        out = open(output_path, "w", encoding="utf-8")
        print(f"Writing output to: {output_path}", file=sys.stderr)
    else:
        out = sys.stdout
        output_path = None

    try:
        pdf = pdfium.PdfDocument(pdf_path)
        total_pages = len(pdf)
        pdf.close()

        page_indices = resolve_pages(pages, total_pages)
        print(
            f"Processing {len(page_indices)} page(s) from '{pdf_path}' "
            f"(total: {total_pages}) with model '{model_name}'",
            file=sys.stderr,
        )

        has_bbox = MODEL_REGISTRY.get(model_name, {}).get("has_bbox", False)

        doc_start = time.perf_counter()
        for page_idx in page_indices:
            print(f"  Page {page_idx + 1}/{total_pages}...", file=sys.stderr)
            page_start = time.perf_counter()
            image, _ = load_pdf_page(pdf_path, page_idx)
            text = extract_text_from_image(image, model_name, temperature, max_tokens)
            page_elapsed = time.perf_counter() - page_start
            print(f"  Page {page_idx + 1} done in {page_elapsed:.2f}s", file=sys.stderr)

            if has_bbox:
                text, _ = parse_bbox_output(text)

            if len(page_indices) > 1:
                out.write(f"\n--- Page {page_idx + 1} ---\n\n")
            out.write(text)
            out.write("\n")

        doc_elapsed = time.perf_counter() - doc_start
        print(
            f"Finished {len(page_indices)} page(s) in {doc_elapsed:.2f}s "
            f"({doc_elapsed / len(page_indices):.2f}s/page)",
            file=sys.stderr,
        )

    finally:
        if output_path is not None:
            out.close()


def resolve_pages(pages_spec, total_pages):
    """Parse a page spec like '1', '1-3', '1,3,5' into a sorted list of 0-based indices."""
    if pages_spec is None:
        return list(range(total_pages))

    indices = set()
    for part in pages_spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            indices.update(range(int(start) - 1, int(end)))
        else:
            indices.add(int(part) - 1)

    return sorted(i for i in indices if 0 <= i < total_pages)


def main(
    pdf: Annotated[Path, typer.Option(help="Path to the input PDF file")],
    accelerator_device: Annotated[
        Literal["cpu", "mps", "cuda"], typer.Option(help="Accelerator device to use")
    ] = "cpu",
    model: Annotated[
        Literal["LightOnOCR-2-1B", "LightOnOCR-2-1B-bbox", "LightOnOCR-2-1B-base", "LightOnOCR-2-1B-bbox-base"],
        typer.Option(help="OCR model to use"),
    ] = DEFAULT_MODEL,
    pages: Annotated[
        Optional[str],
        typer.Option(help="Pages to process: '1', '2-5', or '1,3,7'. Omit to process all pages."),
    ] = None,
    temperature: Annotated[
        float, typer.Option(help="Sampling temperature (0 = deterministic)")
    ] = 0.2,
    max_tokens: Annotated[
        int, typer.Option(help="Maximum output tokens per page")
    ] = 2048,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(help="Directory to write output into. File is named <pdf_name>.md. Defaults to stdout."),
    ] = None,
) -> None:
    """Run LightOnOCR on a PDF file."""
    global device, attn_implementation, dtype
    if accelerator_device == "cuda":
        device = "cuda"
        attn_implementation = "sdpa"
        dtype = torch.bfloat16
    else:
        device = accelerator_device
        attn_implementation = "eager"
        dtype = torch.float32
    print(f"Device: {device.upper()}, attention: {attn_implementation}", file=sys.stderr)

    if not pdf.exists():
        typer.echo(f"Error: file not found: {pdf}", err=True)
        raise typer.Exit(code=1)
    if pdf.suffix.lower() != ".pdf":
        typer.echo(f"Error: expected a PDF file, got: {pdf.suffix}", err=True)
        raise typer.Exit(code=1)

    process_pdf(
        str(pdf),
        pages,
        model,
        temperature,
        max_tokens,
        output_dir,
    )


if __name__ == "__main__":
    typer.run(main)
