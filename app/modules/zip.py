import shutil
from pathlib import Path
import os

def zip(source: Path, destination: Path):
    print(f'{source} | {destination} | {source}.zip')
    shutil.make_archive(source, 'zip', source)
    shutil.move(f'{source}.zip', destination)
    return