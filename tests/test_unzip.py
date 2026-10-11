import tempfile
import unittest
import zipfile
from pathlib import Path

from app.modules.unzip import unzip


class UnzipTest(unittest.TestCase):
    def test_extracts_regular_zip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "dataset.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("train/images/example.txt", "ok")
            unzip(archive, root / "dataset")
            self.assertEqual((root / "dataset/train/images/example.txt").read_text(), "ok")

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "dataset.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("../outside.txt", "unsafe")
            with self.assertRaisesRegex(ValueError, "caminho inseguro"):
                unzip(archive, root / "dataset")


if __name__ == "__main__":
    unittest.main()
