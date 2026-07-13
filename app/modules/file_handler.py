from pathlib import Path

FILES_PATH = 'files'

async def save_file(file: bytes, filepath: str = None, filename: str = None) -> Path:
    # solves the absolute path of the file
    abs_path = None
    if filepath:
        abs_path = Path(filepath)
    else:
        if filename:
            abs_path = Path(FILES_PATH) / filename
        else:
            abs_path = Path(FILES_PATH) / file.filename

    # reads and copies the bytes of the file, chunk by chunk
    with open(abs_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # 1MB
            f.write(chunk)

    await file.close()

    return abs_path