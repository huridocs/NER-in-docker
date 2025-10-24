import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import requests
import zipfile
from ner_in_docker.configuration import DATA_PATH
from pathlib import Path


def get_data():
    data_path = Path(DATA_PATH) / "conll-2012"
    if data_path.exists():
        print("Data already exists. Skipping download.")
        return

    data_url = "https://data.mendeley.com/public-files/datasets/zmycy7t9h9/files/b078e1c4-f7a4-4427-be7f-9389967831ef/file_downloaded"
    response = requests.get(data_url)

    with open(Path(DATA_PATH, "conll-2012.zip"), "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(Path(DATA_PATH, "conll-2012.zip"), "r") as zip_ref:
        zip_ref.extractall(DATA_PATH)


if __name__ == "__main__":
    get_data()
