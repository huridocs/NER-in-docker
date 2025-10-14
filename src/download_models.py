import math
from os import makedirs
from os.path import join, exists
from huggingface_hub import snapshot_download

from configuration.configuration import MODELS_PATH


def download_progress(count, block_size, total_size):
    total_counts = total_size // block_size
    show_counts_percentages = total_counts // 5
    percent = count * block_size * 100 / total_size
    if count % show_counts_percentages == 0:
        print(f"Downloaded {math.ceil(percent)}%")


def download_flair_model():
    model_path = join(MODELS_PATH, "flair")
    if exists(model_path):
        return
    makedirs(model_path, exist_ok=True)
    snapshot_download(repo_id="flair/ner-english-ontonotes-large", local_dir=model_path, local_dir_use_symlinks=False)


def download_gliner_model():
    model_path = join(MODELS_PATH, "gliner")
    if exists(model_path):
        return
    makedirs(model_path, exist_ok=True)
    snapshot_download(repo_id="urchade/gliner_multi-v2.1", local_dir=model_path, local_dir_use_symlinks=False)


def download_models():
    makedirs(MODELS_PATH, exist_ok=True)
    download_flair_model()
    download_gliner_model()


if __name__ == "__main__":
    download_models()
