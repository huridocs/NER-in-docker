import json
from ollama import Client
from pathlib import Path
from pydantic import BaseModel, Field

JSONS_PATH = Path("data/jsons")
PDFS_PATH = Path("data/pdfs")
PREDICTIONS_PATH = Path("data/predictions")


class VGTSegment(BaseModel):
    left: int
    top: int
    width: int
    height: int
    page_number: int
    page_width: int
    page_height: int
    text: str
    type: str
    id: str = ""

    def __hash__(self):
        return hash(
            (
                self.left,
                self.top,
                self.width,
                self.height,
                self.page_number,
                self.page_width,
                self.page_height,
                self.text,
                self.type,
                self.id,
            )
        )

    @staticmethod
    def get_dummy_segment() -> "VGTSegment":
        return VGTSegment(
            left=0, top=0, width=0, height=0, page_number=0, page_width=0, page_height=0, text="", type="Text", id=""
        )


class Article(BaseModel):
    article: str
    mention: str
    article_source: str
    source_text: str
    segment: VGTSegment = Field(default=None)


def get_vgt_segments(pdf_path: Path):
    json_path = JSONS_PATH / f"{pdf_path.stem}.json"
    vgt_segments = [VGTSegment(**item) for item in json.loads(json_path.read_text())]
    for vgt_segment in vgt_segments:
        vgt_segment.text = " ".join(vgt_segment.text.split())
    return vgt_segments


def get_content(text: str):
    return f"""
You are an information extraction assistant. Your task is to extract references to legal "articles" (or similar legal provisions) from a given text, along with the source they belong to, the exact phrase as it appears in the text, and the specific mention for each article or sub-article.

**Instructions:**

1. **For each article or sub-article reference found in the text, extract:**
    - "article": The full article or sub-article reference (e.g., "13 (1)", "13 (2)", "14 (1)").
    - "mention": The exact string in the text that refers to this article or sub-article (e.g., "42 (1)", "(2)", "44 (1)"). This should match the text exactly as it appears for this specific mention.
    - "article_source": The name of the code, law, regulation, or document the article belongs to, exactly as it appears in the text.
    - "source_text": The full phrase or sentence from the text where the article(s) and their source are mentioned together, exactly as it appears in the text.

2. **If multiple articles or sub-articles are mentioned together (e.g., "Articles 17 (1), (2) and 18 (1) of the Council's Rules"), extract a separate entry for each, using the same `article_source` and `source_text` for each.**

3. **If no article references are found, return an empty list (`[]`).**

4. **Return the results as a JSON array, with one object per article or sub-article. Do not include any explanations or extra text.**

**Examples:**

**Example Input:**
The Applicant cited Articles 17 (1), (2) and 18 (1) of the Council's Rules.

**Example Output:**
[
  {{
    "article": "17 (1)",
    "mention": "17 (1)",
    "article_source": "Council's Rules",
    "source_text": "Articles 17 (1), (2) and 18 (1) of the Council's Rules."
  }},
  {{
    "article": "17 (2)",
    "mention": "(2)",
    "article_source": "Council's Rules",
    "source_text": "Articles 17 (1), (2) and 18 (1) of the Council's Rules."
  }},
  {{
    "article": "18 (1)",
    "mention": "18 (1)",
    "article_source": "Council's Rules",
    "source_text": "Articles 17 (1), (2) and 18 (1) of the Council's Rules."
  }}
]

**Example Input:**
Whereas, according to article 131-4 of the Legal Code, ...

**Example Output:**
[
  {{
    "article": "131-4",
    "mention": "131-4",
    "article_source": "Legal Code",
    "source_text": "article 131-4 of the Legal Code"
  }}
]

**Example Input:**
This document does not mention any specific articles.

**Example Output:**
[]


---

**Now, extract the articles as described above from the following text:**

{text}
"""


def get_articles_for_segment(segment: VGTSegment, model: str = "gpt-oss"):
    content = get_content(segment.text)
    response = Client().chat(model=model, messages=[{"role": "user", "content": content}])
    response_json = json.loads(response["message"]["content"])
    articles = [Article(segment=segment, **item) for item in response_json]
    return articles


def get_articles_for_pdf(pdf_path: Path, model: str = "gpt-oss"):
    vgt_segments = get_vgt_segments(pdf_path)
    articles = []
    for segment in vgt_segments:
        articles.extend(get_articles_for_segment(segment, model))
    return articles


def extract_articles(model: str = "gpt-oss"):
    for pdf_path in PDFS_PATH.iterdir():
        if pdf_path.suffix != ".pdf":
            continue
        json_path = PREDICTIONS_PATH / f"{pdf_path.stem}.json"
        if json_path.exists():
            continue
        print(f"Extracting articles for {pdf_path.stem}...")
        articles = get_articles_for_pdf(pdf_path, model)
        json_path.write_text(json.dumps([article.model_dump() for article in articles], indent=4))


if __name__ == "__main__":
    Client().chat(model="gpt-oss", messages=[{"role": "user", "content": "hello"}])
    extract_articles()
