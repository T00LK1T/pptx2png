import asyncio
import sys

from aiohttp import ClientSession, ClientTimeout, FormData

from common import get_files_in_directory, get_logger

PPT_DIR = "ppt"
DEFAULT_TARGET_URL = "http://localhost:38080/preprocess/ppt"

logger = get_logger(__name__)


async def main():

    import argparse

    parser = argparse.ArgumentParser(description="request bomber")
    parser.add_argument(
        "-u",
        "--url",
        required=False,
        default=DEFAULT_TARGET_URL,
        help="Target URL to send requests",
    )

    args = parser.parse_args()
    TARGET_URL = args.url or DEFAULT_TARGET_URL

    ppt_file_list = get_files_in_directory(PPT_DIR, postfix=[".ppt", ".pptx"])
    if not ppt_file_list:
        logger.info("No PPT files found in the directory.")
        return

    async with ClientSession(timeout=ClientTimeout(total=1)) as session:
        for file_path in ppt_file_list:
            data = FormData()
            data.add_field(
                "file",
                open(file_path, "rb"),
                filename=file_path.split("/")[-1],
                content_type="application/vnd.ms-powerpoint",
            )
            async with session.post(TARGET_URL, data=data) as response:
                if response.status == 202:
                    logger.info(f"File {file_path} is being processed.")
                else:
                    logger.error(
                        f"Failed to process file {file_path}. Status: {response.status}"
                    )


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("All files processed.")
