import re
from pathlib import Path

FILES_PATH = Path("files")


def sanitize_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    return cleaned[:80] or "project"


def get_train_dir(train_id: int, project_name: str) -> Path:
    return FILES_PATH / f"train_{train_id}_{sanitize_name(project_name)}"


def get_dataset_zip_path(train_id: int, project_name: str) -> Path:
    return get_train_dir(train_id, project_name) / "dataset.zip"


def get_dataset_dir(train_id: int, project_name: str) -> Path:
    return get_train_dir(train_id, project_name) / "dataset"


async def save_dataset(file, train_id: int, project_name: str) -> Path:
    dataset_path = get_dataset_zip_path(train_id, project_name)
    dataset_path.parent.mkdir(parents=True, exist_ok=False)
    await save_file(file=file, filepath=dataset_path)
    return dataset_path


async def save_file(file, filepath: str | Path | None = None, filename: str | None = None) -> Path:
    if filepath:
        abs_path = Path(filepath)
    elif filename:
        abs_path = FILES_PATH / filename
    else:
        abs_path = FILES_PATH / sanitize_name(file.filename)

    abs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(abs_path, "wb") as output:
        while chunk := await file.read(1024 * 1024):
            output.write(chunk)
    await file.close()
    return abs_path
