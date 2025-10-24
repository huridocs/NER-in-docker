from ollama import Client


def try_model(text: str):
    prompt = f"""System role:
    You are a professional Legal NER system. Extract entities from the provided text and return a single valid JSON object that strictly matches the schema below. Do not include any extra commentary.

    Task:
    Given the input text, identify and cluster all mentions of the following entity types:
    - LAW: Named acts/codes/regulations (e.g., “Communications Decency Act”, “Civil Code”).
    - STATUTE: A codified source or named statute family without a specific provision (e.g., “47 U.S.C.”, “Penal Code”).
    - PROVISION: A specific article/section/clause within a LAW or STATUTE (e.g., “47 U.S.C. § 230(c)(1)”, “Article 5(3)”).
    - COURT: Court names (e.g., “United States District Court for the Southern District of New York”).
    - JUDGE: Judicial officers (e.g., “Hon. Jane M. Doe”, “Justice Smith”).
    - LAWYER: Legal counsel/attorneys (e.g., “John R. Smith, Esq.”, “Counsel Mary Lee”).
    - CASE_NUMBER: Docket/case identifiers (e.g., “1:23-cv-12345”, “No. 21-101”).


    Return policy:
    - Return ONLY the JSON object (no markdown, no prose, no trailing commas).
    - If no entities are found, return {"entities": [], "meta": {...}}.

    Output format:
        {{
            canonical_name: str,
            entity_type: str,
            source_text: str,
        }}

    In the `source_text` field, you should return the exact substring of the input text that in order to find the reference in the original text.

    Here is the text you are going to work on:

    {text}
    """

    client = Client(host="http://localhost:11434")

    response = client.chat(model="qwen3:8b", messages=[{"role": "user", "content": prompt}])
    print(response["message"]["content"])
