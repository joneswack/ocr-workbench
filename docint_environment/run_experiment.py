import json
from pathlib import Path
from typing import Annotated

import typer
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    DocumentContentFormat,
)
from azure.core.credentials import AzureKeyCredential


def save_text_to_file(text: str, output_path: Path) -> None:
    """Save text content to a file in the specified output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)


def main(
    input_file: Annotated[Path, typer.Option()],
    output_dir: Annotated[Path, typer.Option()],
):
    config = json.load(open("config.json"))
    endpoint = config["document_intelligence_endpoint"]
    credential = AzureKeyCredential(config["document_intelligence_key"])
    document_intelligence_client = DocumentIntelligenceClient(endpoint, credential)

    with open(input_file, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout",
            body=f,
            output_content_format=DocumentContentFormat.MARKDOWN,
        )
        result = poller.result()

    markdown_content = result["content"]

    save_text_to_file(
        text=markdown_content,
        output_path=output_dir / f"{input_file.stem}.md",
    )


if __name__ == "__main__":
    typer.run(main)
