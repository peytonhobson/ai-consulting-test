import os
from flashrank import Ranker

model_name = "rank-T5-flan"
flashrank_cache_dir = "./cache/flashrank"
model_dir = os.path.join(flashrank_cache_dir, model_name)

# Check if model directory already exists
if not os.path.exists(model_dir):
    print(f"Downloading model files for {model_name}...")
    ranker = Ranker(cache_dir=flashrank_cache_dir)
    Ranker._download_model_files(ranker, model_name)
    print(f"Model files downloaded to {model_dir}")
else:
    print(
        f"Model files for {model_name} already exist at {model_dir}, skipping download"
    )
