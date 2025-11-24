import json
import os
from time import time
from typing import List, Dict
from ollama import Client


class ArticleReferenceExtractor:

    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma3:12b")
        self.client = Client(host=self.host)

    def build_prompt(self, text: str) -> str:
        return f"""Extract all references to Articles from the African (Banjul) Charter on Human and Peoples' Rights from the text below.

The Charter contains Articles numbered 1 to 68. Find all references to these articles in the text.

Requirements:
1. Identify references like "Article 5", "Article 12", "Articles 3 and 4", "Article 7(1)", etc.
2. For each reference found, extract:
   - The article number(s) referenced
   - The exact text where the reference appears (surrounding context). Like "Article 5" or "8(b)".
3. Return ONLY a valid JSON array with no additional text, markdown, or explanations.

Output format:
[
  {{"article_number": "5", "referenced_text": "Article 5"}},
  {{"article_number": "12", "referenced_text": "12(b))"}},
  {{"article_number": "7", "referenced_text": "Article 7(1)"}}
]

Text to analyze:
{text}

JSON array:"""

    def extract_references(self, text: str) -> List[Dict[str, str]]:
        prompt = self.build_prompt(text)
        response_text = ""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal document analyzer. Extract article references and return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                },
            )

            response_text = response["message"]["content"].strip()

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            references = json.loads(response_text)

            if not isinstance(references, list):
                print(f"Warning: Expected list, got {type(references)}")
                return []

            valid_references = []
            for ref in references:
                if isinstance(ref, dict) and "article_number" in ref and "referenced_text" in ref:
                    valid_references.append(ref)
                else:
                    print(f"Warning: Invalid reference format: {ref}")

            return valid_references

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response_text[:500]}")
            return []
        except Exception as e:
            print(f"Error during extraction: {e}")
            return []


def main():
    sample_texts = [
        """The Commission considers that range and type of ultimate remedies depends on the
nature of the violations established and the prejudice suffered by the Complainant.
The Commission is not bound by the strict rules of pleadings that may be applicable
at domestic level, such as that specific remedies must be pleaded. The Commission
mandate to protect rights entils that the Commission can adopt any remedy it
considers effective in the sense that it adequately redresses the prejudice suffered by
the victim.
183. In the present case, where as the amendment to the law redressed the
difficulties of obtaining official identification documents, it only did so as from the
date of the amendment. The prejudice suffered by the victims as a result of difficulties
prior to the amendment are not addressed by this subsequent change in law. In
absence of any other remedy that can redress this prior prejudice, the Commission
considers that monetary compensation is due. Such compensation is at large: it cannot
be ascertained by a mathematical calculation. It is a matter of impression on the part
of the Commission. In the circumstances of the present case, the Commission considers
that a lump sum award of US$15,000.00 (United States Dollars Ten Thousand) for all
the victims cited in the present case to be adequate compensation.
184. Regarding the refusal to document Bahá’í marriages which also constitute
violation of Articles 2 and 3 of the Charter, the appropriate remedy should yield the
official recognition and documentation of Bahá’í marriages using a legal regime that
is neutral of religion since the Respondent State does not recognise Bahá’í as a religion
and source of personal law. In this regard, the Respondent State should take necessary
measures that yield this state of affairs. In particular, the Respondent State has to adopt
a law which is neutral of religion for purposes of recognising and documenting
marriages of persons under its jurisdiction such as the Baha’i in particular) who do not
identify with the personal laws that are based on the three recognised religions.
Decision of the Commission’s on the merits
185. In light of the foregoing, the African Commission on Human and Peoples’
Rights:
(a) Finds that the Respondent State is in violation of Article 2 as read together
with Article 3 both of the Charter;
(b) Finds that the Respondent State is in violation of Artile 8 of the Charter in
respect of the freedom of religion reserved to the forum internum.""",
    ]

    extractor = ArticleReferenceExtractor()

    print(f"Using model: {extractor.model}")
    print(f"Connecting to: {extractor.host}\n")

    all_results = []

    for i, text in enumerate(sample_texts, 1):
        print(f"\n{'='*80}")
        print(f"Processing sample {i}:")
        print(f"Text: {text[:100]}...")
        print(f"{'='*80}\n")

        references = extractor.extract_references(text)

        result = {"sample_id": i, "input_text": text, "references": references}

        all_results.append(result)

        print(f"\nFound {len(references)} article reference(s):")
        for ref in references:
            print(f"  - Article {ref['article_number']}: {ref['referenced_text'][:80]}...")

    output_file = "article_references_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"Total samples processed: {len(all_results)}")
    print(f"{'='*80}")


if __name__ == "__main__":
    start = time()
    print("start")
    main()
    print("time", round(time() - start, 2), "s")
