import zipfile
from pathlib import Path
import os

def unzip(zip_path: Path, destination: Path):
    # verifies if the.zip file exists
    if not os.path.isfile(zip_path):
        raise FileExistsError(f'the file {zip_path} doesn\'t exist')

    # creates the directory if it doesn't exist
    os.makedirs(destination, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination)
    except zipfile.BadZipFile:
        raise zipfile.BadZipFile(f'the file {zip_path} is not a valid zip')
    except PermissionError:
        raise PermissionError(f'permission denied to read {zip_path} or write in {destination}')
    except Exception as error:
        raise Exception(f'unexpected error: {error}')
        return