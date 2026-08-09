from pathlib import Path
import yaml


class ConfigError(Exception):
    """配置文件错误"""


class AppConfig:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path).resolve()
        if not self.config_path.is_file():
            raise ConfigError(f"配置文件不存在：{self.config_path}")

        self.base_dir = self.config_path.parent
        self.raw = self._load_yaml()
        self.project = self.raw.get("project", {})
        self.paths = self.raw.get("paths", {})
        self.ocr = self.raw.get("ocr", {})
        self._validate()
        self._normalize_paths()

    def _load_yaml(self):
        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as exc:
            raise ConfigError(f"读取配置文件失败：{exc}") from exc
        if not isinstance(data, dict):
            raise ConfigError("配置文件格式错误：yaml 顶层必须是字典结构")
        return data

    def _validate(self):
        for key in ("name", "batch_name"):
            if not self.project.get(key):
                raise ConfigError(f"project 缺少配置：{key}")
        required_paths = (
            "input_dir", "output_dir", "tif_dir", "json_extract_dir",
            "charnum_file", "task_split_file", "pic_check_file",
            "error_file", "state_db", "log_dir",
        )
        for key in required_paths:
            if not self.paths.get(key):
                raise ConfigError(f"paths 缺少配置：{key}")
        if not self.ocr.get("url"):
            raise ConfigError("ocr.url 不能为空")

    def _normalize_paths(self):
        for key, value in tuple(self.paths.items()):
            path = Path(value)
            if not path.is_absolute():
                path = self.base_dir / path
            self.paths[key] = str(path.resolve())
        Path(self.paths["state_db"]).parent.mkdir(parents=True, exist_ok=True)
        Path(self.paths["log_dir"]).mkdir(parents=True, exist_ok=True)

    @property
    def project_name(self) -> str:
        return str(self.project["name"])

    @property
    def batch_name(self) -> str:
        return str(self.project["batch_name"])
