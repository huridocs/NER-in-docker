import gradio as gr
import requests
import json

from gradio_ui.api import (
    extract_entities_from_text,
    extract_entities_from_pdf,
    extract_entities_from_text_llm,
    extract_entities_from_pdf_llm,
    save_texts_from_pdfs,
    visualize_pdf,
    wait_for_backend,
    get_identifiers,
    get_segments,
)
from gradio_ui.formatters import create_legend
from gradio_ui.constants import NER_SERVICE_URL


# Create Gradio interface
with gr.Blocks(title="Named Entity Recognition", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🔍 Named Entity Recognition Service")
    gr.Markdown("Extract named entities from text or PDF documents using state-of-the-art NER models.")

    # Display legend
    gr.HTML(create_legend())

    with gr.Tabs():
        # Tab 0: References
        with gr.Tab("📚 References"):
            gr.Markdown("### View References")

            with gr.Row():
                with gr.Column(scale=1):
                    namespace_ref_input = gr.Textbox(
                        label="Namespace",
                        value="default_namespace",
                    )
                    refresh_btn = gr.Button("Refresh Identifiers")
                    identifier_dropdown = gr.Dropdown(
                        label="Identifiers",
                        choices=[],
                        value=None,
                        interactive=True,
                    )
                with gr.Column(scale=2):
                    gr.Markdown("#### Segment Details")
                    selected_segment = gr.HTML(elem_id="segment-details")

            gr.Markdown("#### Segments")
            segments_container = gr.HTML()

            def update_dropdown(ns):
                choices = get_identifiers(ns)
                return gr.Dropdown(choices=choices, value=choices[0] if choices else None)

            refresh_btn.click(fn=update_dropdown, inputs=[namespace_ref_input], outputs=[identifier_dropdown])

            def display_segments(identifier, namespace):
                if not identifier:
                    segments_container.value = ""
                    selected_segment.value = ""
                    return

                try:
                    response = requests.get(
                        f"{NER_SERVICE_URL}/segments", params={"identifier": identifier, "namespace": namespace}, timeout=30
                    )

                    if response.status_code == 200:
                        segments = response.json()
                        segments.sort(key=lambda x: x.get("segment_number", 0))

                        cards_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
                        for segment in segments:
                            text = segment.get("text", "")[:100] + ("..." if len(segment.get("text", "")) > 100 else "")
                            seg_num = segment.get("segment_number", "N/A")
                            full_text = segment.get("text", "N/A")
                            page = segment.get("page_number", "N/A")
                            seg_type = segment.get("type", "N/A")
                            source_id = segment.get("source_id", "N/A")
                            bbox = segment.get("bounding_box", {})
                            bbox_str = (
                                f"x={bbox.get('x', 'N/A')}, y={bbox.get('y', 'N/A')}, width={bbox.get('width', 'N/A')}, height={bbox.get('height', 'N/A')}"
                                if bbox
                                else "N/A"
                            )
                            page_dims = f"{segment.get('page_width', 'N/A')}x{segment.get('page_height', 'N/A')}"

                            details = f"## Segment {seg_num}\n\n**Text:** {full_text}\n\n**Page:** {page}\n\n**Type:** {seg_type}\n\n**Source ID:** {source_id}\n\n**Bounding Box:** {bbox_str}\n\n**Page Dimensions:** {page_dims}"

                            cards_html += f"""<div style="flex: 1 1 200px;">
                                <button class="gradio-button secondary sm" onclick="document.getElementById('segment-details').innerHTML = `{details.replace(chr(10), '<br>').replace('`', '&#96;')}`">{text}</button>
                            </div>"""
                        cards_html += "</div>"

                        segments_container.value = cards_html
                        selected_segment.value = "<p>Click a segment to view details</p>"
                    else:
                        segments_container.value = f"<p>Error: {response.status_code}</p>"
                        selected_segment.value = ""

                except Exception as e:
                    segments_container.value = f"<p>Error: {str(e)}</p>"
                    selected_segment.value = ""

            identifier_dropdown.change(
                fn=display_segments,
                inputs=[identifier_dropdown, namespace_ref_input],
                outputs=[segments_container, selected_segment],
            )

        # Tab 1: Save Texts from PDFs
        with gr.Tab("💾 Save Texts"):
            gr.Markdown("### Save text from multiple PDFs")
            gr.Markdown("Upload multiple PDF documents to extract and save their text content.")

            with gr.Row():
                with gr.Column(scale=1):
                    pdf_files_input = gr.File(
                        label="Upload PDFs", file_types=[".pdf"], type="filepath", file_count="multiple"
                    )
                    namespace_input = gr.Textbox(
                        label="Namespace",
                        placeholder="Enter namespace (e.g., 'my_docs')",
                    )
                    identifier_input = gr.Textbox(
                        label="Identifier Prefix",
                        placeholder="Enter identifier prefix (optional)",
                    )
                    with gr.Row():
                        language_save = gr.Dropdown(
                            choices=["en", "es", "de", "fr"],
                            value="en",
                            label="Language",
                        )
                        fast_mode_save = gr.Checkbox(label="Fast Mode", value=False, info="Enable for faster processing")
                    save_btn = gr.Button("Save Texts", variant="primary")

                with gr.Column(scale=2):
                    save_output = gr.HTML(label="Results")

            save_btn.click(
                fn=save_texts_from_pdfs,
                inputs=[pdf_files_input, namespace_input, identifier_input, language_save, fast_mode_save],
                outputs=[save_output],
            )

        # Tab 2: Text Input
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

        # Tab 2: PDF Entity Extraction & Visualization
        with gr.Tab("📄 PDF Entity Extraction & Visualization"):
            gr.Markdown("### Extract and Visualize entities from PDF")
            gr.Markdown(
                "Upload a PDF document to extract named entities, get the JSON response, or generate an annotated version."
            )

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

                    with gr.Row():
                        extract_entities_btn = gr.Button("Extract Entities", variant="primary")
                        visualize_btn = gr.Button("Generate Visualization", variant="secondary")

                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.Tab("📋 Extracted Entities"):
                            entities_output_pdf = gr.HTML(label="Entities")
                        with gr.Tab("🎨 Visualization"):
                            gr.Markdown("#### PDF Preview:")
                            pdf_preview = gr.HTML(label="PDF Viewer")
                            annotated_pdf_output = gr.File(label="Download Annotated PDF", interactive=False)

            with gr.Accordion("📋 View JSON Response", open=False):
                json_output_pdf = gr.Code(label="JSON Response", language="json", lines=15)

            extract_entities_btn.click(
                fn=extract_entities_from_pdf,
                inputs=[pdf_input_entities, language_pdf_entities, fast_mode_entities],
                outputs=[entities_output_pdf, json_output_pdf],
            )

            visualize_btn.click(
                fn=visualize_pdf,
                inputs=[pdf_input_entities, language_pdf_entities, fast_mode_entities],
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
