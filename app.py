import asyncio
import os
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from common import FilePath, ensure_path_exists, gen_task_id, get_logger, is_path_exists
from converter import Converter

logger = get_logger(__name__)

TASK_ID_LENGTH = 8  # Length of the task ID
CONCURRENT_LIMIT = 1  # Adjust this limit as needed


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Application startup.")
    ensure_path_exists(FilePath.PPT.value)
    ensure_path_exists(FilePath.PDF.value)
    ensure_path_exists(FilePath.PNG.value)
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="Background task example",
    description="...",
    version="1.0.0",
    lifespan=lifespan,
)


async def save_ppt_into_lfs(file: UploadFile, file_path: str):
    """
    Save the uploaded PPT file into the specified path.
    """
    ensure_path_exists(FilePath.PPT.value)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    logger.info("File saved to: %s", file_path)


class ConverterManager:
    def __init__(self, concurrent_limit: int):
        self.concurrent_limit = concurrent_limit
        self.semaphore = threading.BoundedSemaphore(concurrent_limit)
        self.lock = threading.Lock()
        self.current_count = 0

    def borrow(
        self,
    ) -> tuple[bool, Converter | None]:
        if not self.semaphore.acquire(blocking=False):
            return False, None
        try:
            with self.lock:
                self.current_count += 1
                logger.info(
                    "Current count after borrow: %d -> %d",
                    self.current_count - 1,
                    self.current_count,
                )
                return True, Converter()
        except Exception as e:
            self.semaphore.release()
            with self.lock:
                self.current_count -= 1
            logger.error("Error while borrowing semaphore: %s", e)
            return False, None

    def return_(self, preprocessor: Converter):
        del preprocessor
        self.semaphore.release()
        with self.lock:
            self.current_count -= 1
            logger.info(
                "Current count after return: %d -> %d",
                self.current_count + 1,
                self.current_count,
            )
            if self.current_count < 0:
                logger.error("Current count is negative, resetting to 0.")
                self.current_count = 0

    def get_current_count(self) -> int:
        with self.lock:
            return self.current_count

    def get_available_count(self) -> int:
        return self.concurrent_limit - self.current_count


conv_manager = ConverterManager(concurrent_limit=CONCURRENT_LIMIT)


async def process_ppt_coro(
    file_path: str,
    task_id: str,
    output_pdf_dir: str = "pdf",
    output_png_dir: str = "png",
    output_png_dpi: int = 200,
):
    busy_count = 0
    ensure_path_exists(Path(output_png_dir, task_id).as_posix())
    while True:
        success, preprocessor = conv_manager.borrow()
        if success and preprocessor:
            break
        if busy_count % 100 == 0:
            logger.debug("ALL CONVERTERS ARE BUSY. ")
        await asyncio.sleep(1)
        busy_count += 1

    try:
        logger.info("Processing PPT file: %s", file_path)
        preprocessor.initialize(
            input_ppt=file_path,
            output_pdf_dir=output_pdf_dir,
            output_png_dir=output_png_dir,
            output_png_dpi=output_png_dpi,
        )
        await asyncio.to_thread(preprocessor.convert, task_id=task_id)
    except Exception as e:
        logger.error("Error processing PPT file: %s", e)
    finally:
        conv_manager.return_(preprocessor)
        logger.info("Finished processing PPT file: %s", file_path)


@app.post("/preprocess/ppt")
async def handle_preprocess(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ppt file to preprocess"),
):
    logger.info("Received file: %s", file.filename)
    ensure_path_exists(FilePath.PPT.value)

    # NOTE: 보통 발생할 일 없음
    if not file.filename:
        logger.error("No file name provided in the upload.")
        return JSONResponse(
            status_code=400,
            content={"message": "파일 이름이 제공되지 않았습니다."},
        )
    # NOTE: 파일 확장자 확인
    if not file.filename.endswith((".ppt", ".pptx")):
        logger.error("Invalid file type: %s", file.filename)
        return JSONResponse(
            status_code=400,
            content={
                "message": "지원하지 않는 파일 형식입니다. ppt 또는 pptx 파일만 허용합니다."
            },
        )

    task_id = gen_task_id(length=8)
    file_path = os.path.basename(Path(file.filename))
    await save_ppt_into_lfs(file, file_path)
    # start background task
    background_tasks.add_task(
        process_ppt_coro,
        file_path=file_path,
        output_pdf_dir=FilePath.PDF.value,
        output_png_dir=FilePath.PNG.value,
        output_png_dpi=200,
        task_id=task_id,
    )
    return JSONResponse(
        status_code=202,
        content={
            "message": "이미지 전처리 작업이 백그라운드에서 시작되었습니다.",
            "task_id": task_id,
        },
    )


@app.get("/preprocess/ppt/status")
async def get_preprocess_status(task_id: str):
    """
    Get the current status of the preprocess task.
    """

    dir_exists = is_path_exists(Path(FilePath.PNG.value, task_id))
    metadata_exists = is_path_exists(Path(FilePath.PNG.value, task_id, "metadata.json"))
    if metadata_exists:
        return JSONResponse(
            status_code=200,
            content={
                "message": "이미지 전처리 작업이 완료되었습니다.",
                "task_id": task_id,
            },
        )
    if dir_exists:
        return JSONResponse(
            status_code=202,
            content={
                "message": "이미지 전처리 작업이 진행 중입니다.",
                "task_id": task_id,
            },
        )
    return JSONResponse(
        status_code=404,
        content={
            "message": "이미지 전처리 작업을 찾을 수 없습니다.",
            "task_id": task_id,
        },
    )


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "healthy"}
