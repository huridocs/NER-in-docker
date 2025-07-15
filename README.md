<h3 align="center">Named Entity Recognition with Docker</h3>
<p align="center">A Docker-powered service for named entity extraction from text or PDF files.</p>

---
This repository provides a Docker-powered service for Named Entity Recognition (NER), enabling the extraction of specific 
entities from text or PDF files. The service enables extraction of various entities with the help of [pdf-document-layout-analysis](https://github.com/huridocs/pdf-document-layout-analysis),
a service that segments documents with high accuracy.

#### Project Links:

- GitHub: [NER-in-docker](https://github.com/huridocs/NER-in-docker)
- HuggingFace: [NER-in-docker](https://huggingface.co/HURIDOCS/NER-in-docker)

## Quick Start
Clone the service:

    git clone https://github.com/huridocs/NER-in-docker
    cd NER-in-docker

Run the service:

- With GPU support:
  
      make start

- Without GPU support:

      make start_no_gpu

---

## API Usage

The service exposes a FastAPI REST API. By default, it runs on `http://localhost:8000`.

### Endpoints

#### 1. `/` (POST)
Extract named entities from text or PDF.

**Parameters:**
- `namespace` (str, optional): Namespace for storing/retrieving entities in SQLite.
- `identifier` (str, optional): Source identifier for the text.
- `text` (str, optional): Text to analyze (if no file is provided).
- `file` (PDF, optional): PDF file to analyze (multipart/form-data).
- `fast` (bool, optional): Use fast PDF segmentation (default: False).

**Example (Text):**
```bash
curl -X POST http://localhost:8000/ \
  -F "text=Your text here" \
  -F "namespace=my_namespace"
```

**Example (PDF):**
```bash
curl -X POST http://localhost:8000/ \
  -F "file=@/path/to/file.pdf" \
  -F "namespace=my_namespace" \
  -F "fast=true"
```

#### 2. `/delete_namespace` (POST)
Delete all entities for a given namespace.

**Parameters:**
- `namespace` (str, required): Namespace to delete.

**Example:**
```bash
curl -X POST http://localhost:8000/delete_namespace \
  -F "namespace=my_namespace"
```

#### 3. `/` (GET)
Returns Python version info (for health check).

---

## Response Structure

The main endpoint (`/`, POST) returns a JSON object:

```
{
  "entities": [
    {
      "text": "Entity text",
      "type": "EntityType",
      "source_id": "Source identifier",
      "character_start": 123,
      "character_end": 130,
      "relevance_percentage": 98.5,
      "group_name": "GroupName",
      "segment": {
        "page_number": 1,
        "segment_number": 0,
        ...
      }
    },
    ...
  ],
  "groups": [
    {
      "name": "GroupName",
      "entities": [
        {
          "text": "Entity text",
          "index": 0,
          ...
        },
        ...
      ]
    },
    ...
  ]
}
```
- `entities`: List of extracted named entities with metadata.
- `groups`: List of entity groups, each containing related entities.

---

## Notes
- If `namespace` is provided, entities are stored and reused for reference extraction.
- If both `text` and `file` are provided, only the file is processed.
- The service supports both text and PDF input.

For more details, see the source code and API models in `src/drivers/rest/response_entities/NamedEntitiesResponse.py`.
