import os
import subprocess
from typing import Annotated

from common import ensure_path_exists, get_files_in_directory, get_logger

logger = get_logger(__name__)


def pptx_to_pdf(
    input_pptx: Annotated[str, "입력: PPTX 파일 경로"],
    output_pdf_dir: Annotated[str, "출력: PDF 저장 경로"],
) -> tuple[bool, str | None]:
    """
    LibreOffice를 사용해 PPTX를 PDF로 변환
    :param input_pptx: 입력 PPTX 파일 경로
    :param output_pdf: 출력 PDF 파일 경로
    """
    # LibreOffice 실행 (headless 모드)

    ensure_path_exists(os.path.dirname(output_pdf_dir))
    generated_pdf_path = os.path.join(
        output_pdf_dir, os.path.basename(input_pptx).replace(".pptx", ".pdf")
    )
    try:
        subprocess.run(
            [
                "soffice",  # brewed
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                os.path.dirname(generated_pdf_path),
                input_pptx,
            ],
            check=True,
        )
        logger.info("PPTX -> PDF로 변환 완료: %s -> %s", input_pptx, generated_pdf_path)
        return True, generated_pdf_path
    except Exception as e:
        logger.error("PPTX -> PDF 변환 실패: %s", e)
        raise e


if __name__ == "__main__":
    """
    -i <입력 PPTX 파일 경로>
    -o <출력 PDF 파일 경로>
    사용 예시:
    python pptx2pdf.py -i input.pptx -o output.pdf
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PPTX to PDF using LibreOffice."
    )
    parser.add_argument("-i", "--input", required=True, help="Input PPTX file path")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file path")
    args = parser.parse_args()
    input_pptx = args.input
    output_pdf_dir = args.output

    input_pptx_files = get_files_in_directory(input_pptx, ["pptx"])
    input_pptx_files.sort()
    logger.info("입력 PPTX 파일: %s", input_pptx_files)
    if not input_pptx_files:
        logger.warning("입력 파일이 없습니다: %s", input_pptx)
        exit(1)
    ensure_path_exists(os.path.dirname(output_pdf_dir))

    for input_pptx_file in input_pptx_files:
        try:
            okay, output_dir_ = pptx_to_pdf(input_pptx_file, output_pdf_dir)
            logger.info("변환 완료: %s", output_dir_)
        except subprocess.CalledProcessError as e:
            logger.error("변환 실패: %s", e)
        except Exception as e:
            logger.exception("오류 발생: %s", e)

    logger.info("모든 변환 작업이 완료되었습니다.")
    exit(0)
