import os
from pathlib import Path

FILES_PATH = Path('files')

def get_dataset_zip_path(file, train_id, project_name: str) -> Path:
    directory_name = f'train_{train_id}_{project_name}'
    dataset_path = FILES_PATH / directory_name / file.filename
    return dataset_path


def get_dataset_dir(train_id, project_name: str) -> Path:
    directory_name = f'train_{train_id}_{project_name}'
    dataset_path = FILES_PATH / directory_name
    return dataset_path


async def save_dataset(file: bytes, train_id: str, project_name: str) -> Path:
    dataset_path = get_dataset_zip_path(file, train_id, project_name)
    directory_path = get_dataset_dir(train_id, project_name)

    # create the train folder
    os.mkdir(path=directory_path)

    # saves the dataset 
    await save_file(file=file, filepath=dataset_path)

    return dataset_path


async def save_file(file: bytes, filepath: str = None, filename: str = None) -> Path:
    # solves the absolute path of the file
    abs_path = None
    if filepath:
        abs_path = Path(filepath)
    else:
        if filename:
            abs_path = FILES_PATH / filename
        else:
            abs_path = FILES_PATH / file.filename

    # reads and copies the bytes of the file, chunk by chunk
    with open(abs_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # 1MB
            f.write(chunk)

    await file.close()

    return abs_path