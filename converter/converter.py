from datetime import datetime
from typing import Annotated

import orjson

from common import get_logger

from .pdf2png import pdf_to_png
from .pptx2pdf import pptx_to_pdf

logger = get_logger(__name__)


class Converter:
    def __init__(self): ...

    def initialize(
        self,
        input_ppt: Annotated[str, "입력: PPTX 경로"],
        output_pdf_dir: Annotated[str, "출력: PDF 경로"] = "pdf",
        output_png_dir: Annotated[str, "출력: PNG 경로"] = "png",
        output_png_dpi: Annotated[int, "출력: PNG 해상도 (DPI)"] = 200,
    ):
        self.input_ppt = input_ppt
        self.output_pdf_dir = output_pdf_dir
        self.output_png_dir = output_png_dir
        self.output_png_dpi = output_png_dpi

    def convert(self, task_id: str) -> str:
        """
        ppt -> pdf -> png 변환
        """
        okay, generated_pdf_path = pptx_to_pdf(
            self.input_ppt,
            self.output_pdf_dir,
        )
        if not okay:
            raise RuntimeError(f"Failed to convert PPTX to PDF: {self.input_ppt}")

        origin_file_name = self.input_ppt.split("/")[-1]

        generated_png_path = f"{self.output_png_dir}" f"/{task_id}"

        metadata = {
            "origin_file_name": origin_file_name,
            "task_id": task_id,
            "output_png_dpi": self.output_png_dpi,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            "pdf_to_png: [generated_pdf_path=%s, generated_png_path=%s, output_png_dpi=%d]",
            generated_pdf_path,
            generated_png_path,
            self.output_png_dpi,
        )

        pdf_to_png(
            generated_pdf_path,
            generated_png_path,
            self.output_png_dpi,
        )
        with open(f"{generated_png_path}/metadata.json", "w") as f:
            f.write(orjson.dumps(metadata).decode("utf-8"))
        logger.info("Conversion completed successfully.")
        return self.output_png_dir


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(
            "Usage: python -m converter.converter <input_pptx_path> <output_pdf_dir> <output_png_dir> [output_png_dpi]"
        )
        sys.exit(1)

    input_ppt = sys.argv[1]
    output_pdf_dir = sys.argv[2]
    output_png_dir = sys.argv[3]
    output_png_dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 200

    converter = Converter()
    converter.initialize(
        input_ppt=input_ppt,
        output_pdf_dir=output_pdf_dir,
        output_png_dir=output_png_dir,
        output_png_dpi=output_png_dpi,
    )
    output_dir = converter.convert(task_id=datetime.now().strftime("%Y%m%d%H%M%S"))
    print(f"Converted files are saved in: {output_dir}")
