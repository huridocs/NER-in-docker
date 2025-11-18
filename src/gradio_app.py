import gradio as gr
import requests
import json
from typing import Dict, Any, Tuple, Optional
import tempfile
import time

NER_SERVICE_URL = "http://ner:5070"

ENTITY_COLORS = {
    "PERSON": "#4A90E2",  # Blue
    "ORGANIZATION": "#E74C3C",  # Red
    "LOCATION": "#2ECC71",  # Green
    "DATE": "#F39C12",  # Orange
    "LAW": "#9B59B6",  # Purple
    "DOCUMENT_CODE": "#1ABC9C",  # Teal
    "REFERENCE": "#D35400",  # Dark Orange
}


def format_entity_display(entity: Dict[str, Any]) -> str:
    """Format a single entity for display."""
    entity_type = entity.get("type", "UNKNOWN")
    text = entity.get("text", "")
    color = ENTITY_COLORS.get(entity_type, "#95A5A6")

    return f'<span style="background-color: {color}; padding: 2px 6px; border-radius: 3px; color: white; margin: 2px; display: inline-block;">{text} ({entity_type})</span>'


def format_entities_html(entities: list) -> str:
    """Format entities list as HTML."""
    if not entities:
        return "<p>No entities found.</p>"

    html = "<div style='line-height: 2.5;'>"

    # Group by entity type
    entities_by_type = {}
    for entity in entities:
        entity_type = entity.get("type", "UNKNOWN")
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)

    # Display grouped entities
    for entity_type, type_entities in entities_by_type.items():
        color = ENTITY_COLORS.get(entity_type, "#95A5A6")
        html += f'<h4 style="color: {color}; margin-top: 15px;">{entity_type} ({len(type_entities)})</h4>'
        html += '<div style="margin-bottom: 10px;">'
        for entity in type_entities:
            html += format_entity_display(entity)
        html += "</div>"

    html += "</div>"
    return html


def extract_entities_from_text(text: str, language: str = "en") -> Tuple[str, str]:
    """Extract entities from text using the NER service."""
    if not text.strip():
        return "<p style='color: red;'>Please enter some text.</p>", ""

    try:
        response = requests.post(f"{NER_SERVICE_URL}/", data={"text": text, "language": language}, timeout=300)

        if response.status_code != 200:
            return f"<p style='color: red;'>Error: Service returned status code {response.status_code}</p>", ""

        result = response.json()
        entities = result.get("entities", [])

        # Format entities for display
        entities_html = format_entities_html(entities)

        # Format JSON response
        json_response = json.dumps(result, indent=2)

        return entities_html, json_response

    except requests.exceptions.ConnectionError:
        return "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>", ""
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>", ""


def extract_entities_from_pdf(pdf_file, language: str = "en", fast: bool = False) -> Tuple[str, str]:
    """Extract entities from PDF and return JSON response."""
    if pdf_file is None:
        return "<p style='color: red;'>Please upload a PDF file.</p>", ""

    try:
        with open(pdf_file, "rb") as f:
            pdf_content = f.read()

        files = {"file": ("document.pdf", pdf_content, "application/pdf")}
        data = {"language": language, "fast": fast}

        entities_response = requests.post(f"{NER_SERVICE_URL}/", files=files, data=data, timeout=300)

        if entities_response.status_code == 200:
            result = entities_response.json()
            entities = result.get("entities", [])
            entities_html = format_entities_html(entities)
            json_response = json.dumps(result, indent=2)
            return entities_html, json_response
        else:
            return f"<p style='color: red;'>Error: Service returned status code {entities_response.status_code}</p>", ""

    except requests.exceptions.ConnectionError:
        return "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>", ""
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>", ""


def extract_entities_from_text_llm(text: str, language: str = "en") -> Tuple[str, str]:
    """Extract entities from text using LLM-based NER service."""
    if not text.strip():
        return "<p style='color: red;'>Please enter some text.</p>", ""

    try:
        response = requests.post(f"{NER_SERVICE_URL}/llm", data={"text": text, "language": language}, timeout=300)

        if response.status_code != 200:
            return f"<p style='color: red;'>Error: Service returned status code {response.status_code}</p>", ""

        result = response.json()
        entities = result.get("entities", [])

        # Format entities for display
        entities_html = format_entities_html(entities)

        # Format JSON response
        json_response = json.dumps(result, indent=2)

        return entities_html, json_response

    except requests.exceptions.ConnectionError:
        return "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>", ""
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>", ""


def extract_entities_from_pdf_llm(pdf_file, language: str = "en", fast: bool = False) -> Tuple[str, str]:
    """Extract entities from PDF using LLM-based NER service."""
    if pdf_file is None:
        return "<p style='color: red;'>Please upload a PDF file.</p>", ""

    try:
        with open(pdf_file, "rb") as f:
            pdf_content = f.read()

        files = {"file": ("document.pdf", pdf_content, "application/pdf")}
        data = {"language": language, "fast": fast}

        entities_response = requests.post(f"{NER_SERVICE_URL}/llm", files=files, data=data, timeout=300)

        if entities_response.status_code == 200:
            result = entities_response.json()
            entities = result.get("entities", [])
            entities_html = format_entities_html(entities)
            json_response = json.dumps(result, indent=2)
            return entities_html, json_response
        else:
            return f"<p style='color: red;'>Error: Service returned status code {entities_response.status_code}</p>", ""

    except requests.exceptions.ConnectionError:
        return "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>", ""
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>", ""


def visualize_pdf(pdf_file, language: str = "en", fast: bool = False) -> Tuple[Optional[str], str]:
    """Generate annotated PDF with entity highlights."""
    if pdf_file is None:
        return None, "<p style='color: red;'>Please upload a PDF file.</p>"

    try:
        with open(pdf_file, "rb") as f:
            pdf_content = f.read()

        files = {"file": ("document.pdf", pdf_content, "application/pdf")}
        data = {"language": language, "fast": fast}

        visualize_response = requests.post(f"{NER_SERVICE_URL}/visualize", files=files, data=data, timeout=300)

        if visualize_response.status_code == 200:
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_pdf.write(visualize_response.content)
            temp_pdf.close()

            import base64

            pdf_base64 = base64.b64encode(visualize_response.content).decode("utf-8")
            pdf_preview_html = f"""
            <div style="width: 100%; height: 800px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden;">
                <iframe 
                    src="data:application/pdf;base64,{pdf_base64}" 
                    width="100%" 
                    height="100%" 
                    style="border: none;"
                    type="application/pdf">
                    <p>Your browser does not support embedded PDFs. Please download the file to view it.</p>
                </iframe>
            </div>
            """
            return temp_pdf.name, pdf_preview_html
        else:
            return None, f"<p style='color: red;'>Error: Service returned status code {visualize_response.status_code}</p>"

    except requests.exceptions.ConnectionError:
        return None, "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>"
    except Exception as e:
        return None, f"<p style='color: red;'>Error: {str(e)}</p>"


def create_legend() -> str:
    """Create a legend showing entity types and their colors."""
    legend_html = "<div style='padding: 10px; background-color: #f5f5f5; border-radius: 5px; margin-bottom: 10px;'>"
    legend_html += "<h4 style='margin-top: 0;'>Entity Types Legend:</h4>"
    legend_html += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"

    entity_labels = {
        "PERSON": "Person (PER)",
        "ORGANIZATION": "Organization (ORG)",
        "LOCATION": "Location (LOC)",
        "DATE": "Date (DAT)",
        "LAW": "Law (LAW)",
        "DOCUMENT_CODE": "Document Code (DOC)",
        "REFERENCE": "Reference (REF)",
    }

    for entity_type, label in entity_labels.items():
        color = ENTITY_COLORS.get(entity_type, "#95A5A6")
        legend_html += f'<span style="background-color: {color}; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold;">{label}</span>'

    legend_html += "</div></div>"
    return legend_html


def wait_for_backend(max_retries: int = 60, retry_interval: int = 2) -> bool:
    """Wait for the backend service to be ready by polling the info endpoint."""
    print("\n" + "=" * 80, flush=True)
    print("⏳ Waiting for NER backend service to be ready...".center(80), flush=True)
    print("=" * 80 + "\n", flush=True)

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(f"{NER_SERVICE_URL}/", timeout=5)
            if response.status_code == 200:
                print("=" * 80, flush=True)
                print("✅  NER UI IS READY!".center(80), flush=True)
                print("=" * 80, flush=True)
                print("", flush=True)
                print("🌐 Access the UI at:", flush=True)
                print("   → http://localhost:7860", flush=True)
                print("", flush=True)
                print("=" * 80, flush=True)
                print("=" * 80 + "\n", flush=True)
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(retry_interval)
        except Exception as e:
            print(f"   Unexpected error while checking backend: {str(e)}", flush=True)
            time.sleep(retry_interval)

    print("\n" + "=" * 80, flush=True)
    print("❌ Backend service did not become ready in time!".center(80), flush=True)
    print("=" * 80 + "\n", flush=True)
    return False


# Create Gradio interface
with gr.Blocks(title="Named Entity Recognition", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🔍 Named Entity Recognition Service")
    gr.Markdown("Extract named entities from text or PDF documents using state-of-the-art NER models.")

    # Display legend
    gr.HTML(create_legend())

    with gr.Tabs():
        # Tab 1: Text Input
        with gr.Tab("📝 Text Extraction"):
            gr.Markdown("### Extract entities from text")
            gr.Markdown("Enter your text below and click 'Extract Entities' to identify named entities.")

            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        label="Input Text",
                        placeholder="Enter text here... (e.g., 'John Smith works at Microsoft in Seattle since January 2020.')",
                        lines=10,
                    )
                    with gr.Row():
                        language_text = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                            info="Select the language of your text",
                        )
                        extract_text_btn = gr.Button("Extract Entities", variant="primary")

                with gr.Column(scale=2):
                    entities_output = gr.HTML(label="Extracted Entities")

            with gr.Accordion("📋 View JSON Response", open=False):
                json_output_text = gr.Code(label="JSON Response", language="json", lines=15)

            # Example texts
            gr.Examples(
                examples=[
                    [
                        "John Smith works at Microsoft in Seattle since January 2020. He reports to the CEO under Article 15 of the company bylaws."
                    ],
                    ["The United Nations held a meeting in Geneva on March 15, 2024, discussing international law reforms."],
                    ["Dr. Sarah Johnson from Harvard University published research in Nature magazine last week."],
                ],
                inputs=text_input,
                label="Example Texts",
            )

            extract_text_btn.click(
                fn=extract_entities_from_text,
                inputs=[text_input, language_text],
                outputs=[entities_output, json_output_text],
            )

        # Tab 2: PDF Entity Extraction
        with gr.Tab("📄 PDF Entity Extraction"):
            gr.Markdown("### Extract entities from PDF")
            gr.Markdown("Upload a PDF document to extract named entities and get the JSON response.")

            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_entities = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
                    with gr.Row():
                        language_pdf_entities = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                            info="Select the language of your PDF",
                        )
                        fast_mode_entities = gr.Checkbox(
                            label="Fast Mode", value=False, info="Enable for faster processing (less accurate segmentation)"
                        )

                    extract_entities_btn = gr.Button("Extract Entities", variant="primary")

                with gr.Column(scale=2):
                    with gr.Accordion("📋 Extracted Entities", open=True):
                        entities_output_pdf = gr.HTML(label="Entities")

            with gr.Accordion("📋 View JSON Response", open=False):
                json_output_pdf = gr.Code(label="JSON Response", language="json", lines=15)

            extract_entities_btn.click(
                fn=extract_entities_from_pdf,
                inputs=[pdf_input_entities, language_pdf_entities, fast_mode_entities],
                outputs=[entities_output_pdf, json_output_pdf],
            )

        # Tab 3: PDF Visualization
        with gr.Tab("🎨 PDF Visualization"):
            gr.Markdown("### Visualize entities in PDF")
            gr.Markdown("Upload a PDF document to generate an annotated version with highlighted entities.")

            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_viz = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
                    with gr.Row():
                        language_pdf_viz = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                            info="Select the language of your PDF",
                        )
                        fast_mode_viz = gr.Checkbox(
                            label="Fast Mode", value=False, info="Enable for faster processing (less accurate segmentation)"
                        )

                    visualize_btn = gr.Button("Generate Visualization", variant="primary")

                with gr.Column(scale=2):
                    gr.Markdown("#### PDF Preview:")
                    pdf_preview = gr.HTML(label="PDF Viewer")
                    annotated_pdf_output = gr.File(label="Download Annotated PDF", interactive=False)

            visualize_btn.click(
                fn=visualize_pdf,
                inputs=[pdf_input_viz, language_pdf_viz, fast_mode_viz],
                outputs=[annotated_pdf_output, pdf_preview],
            )

        # Tab 4: LLM Text Extraction
        with gr.Tab("🤖 LLM Text Extraction"):
            gr.Markdown("### Extract entities from text using LLM")
            gr.Markdown(
                "Use Large Language Models (Ollama) for entity extraction. "
                "This method can provide different results compared to traditional NER models."
            )

            with gr.Row():
                with gr.Column(scale=2):
                    text_input_llm = gr.Textbox(
                        label="Input Text",
                        placeholder="Enter text here... (e.g., 'John Smith works at Microsoft in Seattle since January 2020.')",
                        lines=10,
                    )
                    with gr.Row():
                        language_text_llm = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                            info="Select the language of your text",
                        )
                        extract_text_llm_btn = gr.Button("Extract Entities (LLM)", variant="primary")

                with gr.Column(scale=2):
                    entities_output_llm = gr.HTML(label="Extracted Entities")

            with gr.Accordion("📋 View JSON Response", open=False):
                json_output_text_llm = gr.Code(label="JSON Response", language="json", lines=15)

            # Example texts
            gr.Examples(
                examples=[
                    [
                        "John Smith works at Microsoft in Seattle since January 2020. He reports to the CEO under Article 15 of the company bylaws."
                    ],
                    ["The United Nations held a meeting in Geneva on March 15, 2024, discussing international law reforms."],
                    ["Dr. Sarah Johnson from Harvard University published research in Nature magazine last week."],
                ],
                inputs=text_input_llm,
                label="Example Texts",
            )

            extract_text_llm_btn.click(
                fn=extract_entities_from_text_llm,
                inputs=[text_input_llm, language_text_llm],
                outputs=[entities_output_llm, json_output_text_llm],
            )

        # Tab 5: LLM PDF Extraction
        with gr.Tab("🤖 LLM PDF Entity Extraction"):
            gr.Markdown("### Extract entities from PDF using LLM")
            gr.Markdown(
                "Upload a PDF document and use Large Language Models (Ollama) for entity extraction. "
                "This method can provide different results compared to traditional NER models."
            )

            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_entities_llm = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
                    with gr.Row():
                        language_pdf_entities_llm = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                            info="Select the language of your PDF",
                        )
                        fast_mode_entities_llm = gr.Checkbox(
                            label="Fast Mode", value=False, info="Enable for faster processing (less accurate segmentation)"
                        )

                    extract_entities_llm_btn = gr.Button("Extract Entities (LLM)", variant="primary")

                with gr.Column(scale=2):
                    with gr.Accordion("📋 Extracted Entities", open=True):
                        entities_output_pdf_llm = gr.HTML(label="Entities")

            with gr.Accordion("📋 View JSON Response", open=False):
                json_output_pdf_llm = gr.Code(label="JSON Response", language="json", lines=15)

            extract_entities_llm_btn.click(
                fn=extract_entities_from_pdf_llm,
                inputs=[pdf_input_entities_llm, language_pdf_entities_llm, fast_mode_entities_llm],
                outputs=[entities_output_pdf_llm, json_output_pdf_llm],
            )

    # Footer
    gr.Markdown("---")
    gr.Markdown(
        "Built with [Gradio](https://gradio.app) | " "Powered by [NER-in-docker](https://github.com/huridocs/NER-in-docker)"
    )


if __name__ == "__main__":
    if not wait_for_backend():
        print("❌ Failed to connect to backend service. Exiting...", flush=True)
        exit(1)

    app.launch(server_name="0.0.0.0", server_port=7860, share=False, quiet=True)
