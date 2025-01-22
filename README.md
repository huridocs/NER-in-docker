
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

Get the entities from a text:

    curl -X POST -d "text=Some example text" http://localhost:5070

Get the entities from a PDF:

    curl -X POST -F "file=@/PATH/TO/PDF/pdf_name.pdf" localhost:5070

To stop the server:

    make stop


## Contents
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [Requirements](#requirements)
- [Models](#models)
- [Usage](#usage)
- [Benchmarks](#benchmarks)

## Dependencies
* Docker Desktop 4.25.0 [install link](https://www.docker.com/products/docker-desktop/)
* For GPU support [install link](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Requirements
* 6 GB RAM memory
* 6 GB GPU memory (if not, it will run on CPU)


## Models
For entity extraction, the service use two different models.

One of them is [GLiNER Multi v2.1](https://huggingface.co/urchade/gliner_multi-v2.1). GLiNER is a named entity recognition model
capable of identifying any entity type using a bidirectional transformer encoder (BERT-like).  It provides a practical alternative to 
traditional NER models, which are limited to predefined entities, and Large Language Models (LLMs) that, despite their flexibility, 
are costly and large for resource-constrained scenarios. In this project, we use GLiNER specifically for extracting `DATE` entities.

The other model is [Flair NER English Ontonotes Large](https://huggingface.co/flair/ner-english-ontonotes-large). Flair is a
powerful NLP library and provides various kinds of models. This model we use in our project is one of the largest models Flair provides,
capable of detecting up to 18 entity classes. However, we use this model to extract only the following entities: `PERSON`, `ORGANIZATION`, `LOCATION` and `LAW`.

In addition to these NER models, you can check this link for details on the models that segment documents: [PDF Document Layout Analysis Models](https://github.com/huridocs/pdf-document-layout-analysis#models)

## Usage

As we mentioned int the [Quick Start](#quick-start), you can use the service like this:

    curl -X POST -d "text=Some example text" http://localhost:5070

or

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5070

When text is sent to the service, it is passed directly to the [NER models](#models).

When a PDF is sent, the PDF is first segmented using the [pdf-document-layout-analysis](https://github.com/huridocs/pdf-document-layout-analysis) service.
Then, for each segment, entities are extracted by the [NER models](#models).

When you send a PDF to the service, you should be prepared that the service may use lots of resources. The [pdf-document-layout-analysis](https://github.com/huridocs/pdf-document-layout-analysis)
service segments the PDFs using a visual model. So, please note that if you do not have GPU in your system, or enough free GPU memory,
this visual model will run on CPU, and it might cause longer response time.

After entity extraction, the service tries to merge entities with different or incorrect spellings into a single representative entity
(e.g., "Jane Doe" and "J. Doe" will be merged into "Jane Doe").


When the process is done, the output will be a `NamedEntitiesResponse` in the following format:

    {
      "entities": [
        {
          "group_name": Representative name for all the variations of the same entity (e.g: "Jane Doe")
          "type": Type of the entity (e.g: "PERSON")
          "text": Text of the entity (e.g: "J. Doe")
          "character_start": Starting index of the entity within the context
          "character_end":  Ending index of the entity within the context
        }
      ],
      "groups": [
        {
          "group_name": Representative name for all the variations of the same entity (e.g: "Jane Doe")
          "type": Type of the entity group (e.g: "PERSON")
          "entities_ids": [
            IDs of the entities in the group (e.g: [0, 5])
          ],
          "entities_text": [
            Texts of the entities in the group (e.g:  ["Jane Doe", "J. Doe"])
          ]
        }
      ]
    }

To make it more clear, let's explain.

The response will return two lists, one is "entities" and the other one is "groups". 

The "entities" list contains all the entities found in the given input, doesn't matter their variations. Every entity in "entities" list will have:

- "group_name", this attribute will include the representative name of the given entity. For example, if there are two entities like
"J. Doe" and "Jane Doe", these entities will be merged into the same group, and the group_name will be the most representative version 
of these entities, which is "Jane Doe".

- The other attributes like "type", "text", "character_start" and "character_end" are self-explanatory.

The "groups" list will contain the groups of entities. The "group_name" and "type" attributes here are the same with the "entities" list.
"entities_ids" and "entities_text" attributes will hold the IDs of each entity and the variations of all the entities in the same group.

After you are done with the service, you can stop it with this command:

```
make stop
```

## Benchmarks

For [GLiNER](https://github.com/urchade/GLiNER) benchmark details, you can refer to this [link](https://huggingface.co/urchade/gliner_multi-v2.1).  
Also you can refer to this [paper](https://arxiv.org/abs/2311.08526).

<img src=https://cdn-uploads.huggingface.co/production/uploads/6317233cc92fd6fee317e030/Y5f7tK8lonGqeeO6L6bVI.png width="600">

---

For [Flair](https://github.com/flairNLP/flair) benchmark details, you can refer to this [link](https://towardsdatascience.com/benchmark-ner-algorithm-d4ab01b2d4c3).  
Also you can refer to this [paper](https://arxiv.org/abs/2011.06993).

<img src=https://miro.medium.com/v2/resize:fit:720/format:webp/1*rqxVYJWsUPrZS7Co4u33_Q.png width="600">
