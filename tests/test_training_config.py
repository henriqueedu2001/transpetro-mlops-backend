import unittest

from app.services.training_config import build_training_config, parse_args_yaml


BASE_CONFIG = {
    "model_version": "yolov8", "model_size": "n", "epochs": 10, "batch": 16,
    "workers": 8, "imgsz": 640, "patience": 100, "optimizer": "auto",
    "lr0": 0.01, "lrf": 0.01, "momentum": 0.937, "weight_decay": 0.0005,
    "warmup_epochs": 3, "cos_lr": False, "close_mosaic": 10, "seed": 0,
    "deterministic": True, "device": "0",
}


class TrainingConfigTest(unittest.TestCase):
    def test_builds_checkpoint_and_yaml_overrides_form(self):
        values = {**BASE_CONFIG, "model_version": "yolo11", "model_size": "s"}
        config, extras = build_training_config(values, b"lr0: 0.005\namp: true\n")
        self.assertEqual(config.checkpoint, "yolo11s.pt")
        self.assertEqual(config.lr0, 0.005)
        self.assertEqual(extras, {"amp": True})

    def test_rejects_platform_owned_keys(self):
        with self.assertRaisesRegex(ValueError, "não pode alterar: project"):
            parse_args_yaml(b"project: /tmp/redirect\n")

    def test_rejects_unknown_keys(self):
        with self.assertRaisesRegex(ValueError, "parâmetros desconhecidos"):
            parse_args_yaml(b"mystery: 42\n")

    def test_rejects_invalid_extra_type(self):
        with self.assertRaisesRegex(ValueError, "amp deve ser true ou false"):
            parse_args_yaml(b"amp: talvez\n")

    def test_rejects_invalid_device(self):
        with self.assertRaises(ValueError):
            build_training_config({**BASE_CONFIG, "device": "../../gpu"}, None)

    def test_normalizes_legacy_auto_optimizer(self):
        config, _ = build_training_config({**BASE_CONFIG, "optimizer": "Auto"}, None)
        self.assertEqual(config.optimizer, "auto")


if __name__ == "__main__":
    unittest.main()
