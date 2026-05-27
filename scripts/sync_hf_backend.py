"""Sync CodeBase/backend -> thim1n/wc2026-backend HF Space."""
import os
from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
api.upload_folder(
    folder_path="CodeBase/backend",
    repo_id="thim1n/wc2026-backend",
    repo_type="space",
    ignore_patterns=["*.pyc", "__pycache__", ".venv", "node_modules"],
)
print("✓ Backend synced → thim1n/wc2026-backend")
