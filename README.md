
<h3 align="center">Named Entity Recognition with Docker</h3>
<p align="center">A Docker-powered service for named entity extraction from text or PDF files.</p>

---
This project provides a powerful named entity recognition service. The service enables extraction of
various entities with the help of [pdf-document-layout-analysis](https://github.com/huridocs/pdf-document-layout-analysis),  a service that segments documents with high accuracy.

## Quick Start
Run the service:

- With GPU support:
  
      make start


- Without GPU support:

      make start_no_gpu

Get the entities from a text:

    curl -X POST -d "text=Some example text" http://localhost:5070

Get the entities from a PDF:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5070/pdf

Save the extracted PDF named entities to a local folder:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5070/pdf -F "save_locally=true"

To stop the server:

    make stop


