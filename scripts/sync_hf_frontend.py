"""Sync CodeBase/frontend -> thim1n/wc2026-frontend HF Space."""
import os
from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
api.upload_folder(
    folder_path="CodeBase/frontend",
    repo_id="thim1n/wc2026-frontend",
    repo_type="space",
    ignore_patterns=["node_modules", "dist", "*.pyc"],
)
print("✓ Frontend synced → thim1n/wc2026-frontend")
