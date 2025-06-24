import logging
import random
import string
from enum import Enum
from pathlib import Path
from typing import Annotated

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)


__all__ = [
    "get_logger",
    "get_files_in_directory",
    "ensure_path_exists",
    "gen_task_id",
    "FilePath",
]


class FilePath(str, Enum):
    PPT = "ppt"
    PDF = "pdf"
    PNG = "png"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    로거를 생성하는 함수
    :param name: 로거 이름
    :param level: 로깅 레벨 (기본값: INFO)
    :return: logging.Logger 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def get_files_in_directory(
    directory: Annotated[str, "디렉토리 경로"],
    postfix: Annotated[
        list[str] | None, "파일 확장자 목록, 입력 안하면 모든파일"
    ] = None,
) -> list[str]:
    import os

    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
        and (postfix is None or any(f.endswith(ext) for ext in postfix))
    ]


def ensure_path_exists(path: str) -> None:
    """
    주어진 경로가 존재하지 않으면 생성하는 함수
    :param path: 생성할 경로
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def is_path_exists(path: Path) -> bool:
    """
    주어진 경로가 존재하는지 확인하는 함수
    :param path: 확인할 경로
    :return: 경로가 존재하면 True, 아니면 False
    """
    return path.exists()


gen_task_id = lambda length: "".join(
    random.choices(string.ascii_letters + string.digits, k=length)
)
