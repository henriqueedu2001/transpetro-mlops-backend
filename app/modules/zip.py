import shutil
from pathlib import Path

def zip(source: Path, destination: Path):
    archive_base = destination.with_suffix('')
    created = shutil.make_archive(str(archive_base), 'zip', root_dir=source)
    return Path(created)
