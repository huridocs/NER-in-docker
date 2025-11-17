import gradio as gr
import requests
import json
from typing import Dict, Any, Tuple, Optional
import tempfile
from pathlib import Path

# Configuration
NER_SERVICE_URL = "http://ner:5070"

# Entity type colors matching the service
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


def extract_entities_from_pdf(
    pdf_file, language: str = "en", fast: bool = False, get_entities: bool = True, get_visualization: bool = False
) -> Tuple[Optional[str], str, str, str]:
    """Extract entities from PDF and return annotated PDF with JSON response based on user selection."""
    if pdf_file is None:
        return None, "<p style='color: red;'>Please upload a PDF file.</p>", "", ""

    if not get_entities and not get_visualization:
        return (
            None,
            "<p style='color: orange;'>Please select at least one option: 'Get entities' or 'Get visualization'.</p>",
            "",
            "",
        )

    try:
        # Read the PDF file
        with open(pdf_file, "rb") as f:
            pdf_content = f.read()

        annotated_pdf_path = None
        entities_html = ""
        json_response = ""
        pdf_preview_html = ""

        # Get visualization if requested
        if get_visualization:
            files = {"file": ("document.pdf", pdf_content, "application/pdf")}
            data = {"language": language, "fast": fast}

            visualize_response = requests.post(f"{NER_SERVICE_URL}/visualize", files=files, data=data, timeout=300)

            if visualize_response.status_code == 200:
                # Save annotated PDF to temporary file
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_pdf.write(visualize_response.content)
                temp_pdf.close()
                annotated_pdf_path = temp_pdf.name

                # Create PDF preview HTML with embedded viewer
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
            else:
                entities_html += f"<p style='color: red;'>Error getting visualization: Service returned status code {visualize_response.status_code}</p>"

        # Get entities if requested
        if get_entities:
            files = {"file": ("document.pdf", pdf_content, "application/pdf")}
            data = {"language": language, "fast": fast}

            entities_response = requests.post(f"{NER_SERVICE_URL}/", files=files, data=data, timeout=300)

            if entities_response.status_code == 200:
                result = entities_response.json()
                entities = result.get("entities", [])
                entities_html = format_entities_html(entities) + entities_html
                json_response = json.dumps(result, indent=2)
            else:
                entities_html += f"<p style='color: red;'>Error getting entities: Service returned status code {entities_response.status_code}</p>"

        if not entities_html:
            entities_html = "<p>Processing completed.</p>"

        return annotated_pdf_path, entities_html, json_response, pdf_preview_html

    except requests.exceptions.ConnectionError:
        return None, "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>", "", ""
    except Exception as e:
        return None, f"<p style='color: red;'>Error: {str(e)}</p>", "", ""


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

        # Tab 2: PDF Upload
        with gr.Tab("📄 PDF Extraction"):
            gr.Markdown("### Extract entities from PDF")
            gr.Markdown("Upload a PDF document to extract and visualize named entities.")

            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
                    with gr.Row():
                        language_pdf = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                            info="Select the language of your PDF",
                        )
                        fast_mode = gr.Checkbox(
                            label="Fast Mode", value=False, info="Enable for faster processing (less accurate segmentation)"
                        )

                    gr.Markdown("#### Options:")
                    with gr.Row():
                        get_entities_checkbox = gr.Checkbox(
                            label="Get entities", value=True, info="Extract entities and JSON response"
                        )
                        get_visualization_checkbox = gr.Checkbox(
                            label="Get visualization", value=False, info="Generate annotated PDF with highlights"
                        )

                    extract_pdf_btn = gr.Button("Extract", variant="primary")

                    # Entities display below the upload section
                    with gr.Accordion("📋 Extracted Entities", open=True):
                        entities_output_pdf = gr.HTML(label="Entities")

                with gr.Column(scale=2):
                    annotated_pdf_output = gr.File(label="Annotated PDF", interactive=False)
                    gr.Markdown("#### PDF Preview:")
                    pdf_preview = gr.HTML(label="PDF Viewer")

            with gr.Accordion("📋 View JSON Response", open=False):
                json_output_pdf = gr.Code(label="JSON Response", language="json", lines=15)

            extract_pdf_btn.click(
                fn=extract_entities_from_pdf,
                inputs=[pdf_input, language_pdf, fast_mode, get_entities_checkbox, get_visualization_checkbox],
                outputs=[annotated_pdf_output, entities_output_pdf, json_output_pdf, pdf_preview],
            )

    # Footer
    gr.Markdown("---")
    gr.Markdown(
        "Built with [Gradio](https://gradio.app) | " "Powered by [NER-in-docker](https://github.com/huridocs/NER-in-docker)"
    )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
