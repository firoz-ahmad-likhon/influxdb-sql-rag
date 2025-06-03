import json
from typing import Any, cast
from pathlib import Path
from src.utils.config import Config
import os

Config.load_env()


class DataProvider:
    """Common data catalog."""

    BASE_PATH = Path(os.getenv("DATA_DIR", "app/resources/data"))

    @staticmethod
    def catalog() -> dict[str, Any]:
        """Load catalog json."""
        catalog_path = DataProvider.BASE_PATH / "catalog.json"

        with catalog_path.open("r", encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))

    @staticmethod
    def glossary() -> dict[str, Any]:
        """Load glossary json."""
        glossary_path = DataProvider.BASE_PATH / "glossary.json"

        with glossary_path.open("r", encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))
