from flashrank import Ranker

flashrank_cache_dir = "./cache/flashrank"
ranker = Ranker(cache_dir=flashrank_cache_dir)

Ranker._download_model_files(ranker, "rank-T5-flan")
