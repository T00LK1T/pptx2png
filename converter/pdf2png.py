import os

from pdf2image import convert_from_path

from common import ensure_path_exists, get_files_in_directory, get_logger

logger = get_logger(__name__)


def pdf_to_png(input_pdf, output_folder, dpi=200):
    """
    PDF를 PNG 이미지로 변환
    :param input_pdf: 입력 PDF 파일 경로
    :param output_folder: 출력 폴더 경로
    :param dpi: 이미지 해상도 (기본값 200)
    """
    # PDF를 이미지 리스트로 변환
    images = convert_from_path(input_pdf, dpi=dpi)

    # 출력 폴더 생성
    ensure_path_exists(output_folder)

    # 각 페이지를 PNG로 저장
    for i, image in enumerate(images):
        image.save(os.path.join(output_folder, f"slide_{i+1:03d}.png"), "PNG")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert PDF to PNG images.")
    parser.add_argument("-i", "--input", required=True, help="Input PDF file path")
    parser.add_argument("-o", "--output", required=True, help="Output folder path")
    parser.add_argument(
        "--dpi", type=int, default=200, help="Image resolution in DPI (default: 200)"
    )

    args = parser.parse_args()

    input_pdf_dir = args.input
    output_dir = args.output
    dpi = args.dpi

    input_pdf_files = get_files_in_directory(input_pdf_dir, ["pdf"])
    input_pdf_files.sort()

    for input_pdf_file in input_pdf_files:
        logger.info("Processing PDF file: %s", input_pdf_file)
        output_folder = os.path.join(
            output_dir, os.path.splitext(os.path.basename(input_pdf_file))[0]
        )
        ensure_path_exists(output_folder)
        try:
            pdf_to_png(input_pdf_file, output_folder, dpi=dpi)
        except Exception as e:
            logger.error("Failed to convert PDF '%s': %s", input_pdf_file, e)
            continue
        logger.info(
            "Converted '%s' to PNG images in '%s'", input_pdf_file, output_folder
        )
    logger.info("All PDF files processed.")
    exit(0)
