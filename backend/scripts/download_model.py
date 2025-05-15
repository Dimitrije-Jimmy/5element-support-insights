"""
Script to download the trained DistilBERT model files from cloud storage.
Run this after cloning the repository to get the model files.
"""

import os
import sys
from pathlib import Path
import requests
from tqdm import tqdm

# Replace these with your actual cloud storage URLs
MODEL_FILES = {
    "model.safetensors": "YOUR_CLOUD_URL/model.safetensors",
    "tokenizer.json": "YOUR_CLOUD_URL/tokenizer.json",
    "config.json": "YOUR_CLOUD_URL/config.json"
}

MODEL_DIR = Path(__file__).parent.parent / "models" / "distilbert_classifier"

def download_file(url: str, dest_path: Path, desc: str):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dest_path, 'wb') as file, tqdm(
        desc=desc,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

def main():
    """Download all model files."""
    print(f"Downloading model files to {MODEL_DIR}")
    
    for filename, url in MODEL_FILES.items():
        dest_path = MODEL_DIR / filename
        if dest_path.exists():
            print(f"Skipping {filename} - already exists")
            continue
            
        try:
            download_file(url, dest_path, f"Downloading {filename}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}", file=sys.stderr)
            return 1
    
    print("Download complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 