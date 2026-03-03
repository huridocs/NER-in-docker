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
    create_reference,
    get_references,
    delete_reference,
)
from gradio_ui.formatters import create_legend
from gradio_ui.constants import NER_SERVICE_URL


# Create Gradio interface
with gr.Blocks(
    title="Named Entity Recognition",
    theme=gr.themes.Soft(),
    css="""
    #segments-scrollable {
        max-height: 600px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    #segments-scrollable > div {
        max-height: 600px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
""",
) as app:
    gr.Markdown("# 🔍 Named Entity Recognition Service")
    gr.Markdown("Extract named entities from text or PDF documents using state-of-the-art NER models.")

    # Display legend
    gr.HTML(create_legend())

    with gr.Tabs():
        # Tab 0: References
        with gr.Tab("📚 Create references"):
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
                    gr.Markdown("#### Segments")
                    segments_container = gr.HTML(elem_id="segments-scrollable", elem_classes="scrollable-container")
                with gr.Column(scale=2):
                    gr.Markdown("#### Segment Details")
                    selected_segment = gr.HTML(elem_id="segment-details")

                    gr.Markdown("#### Create Reference")
                    reference_text_input = gr.Textbox(
                        label="Reference Text",
                        placeholder="Enter reference text...",
                    )
                    to_input = gr.Textbox(
                        label="To",
                        placeholder="Enter target...",
                    )
                    create_reference_btn = gr.Button("Create Reference", variant="primary")
                    create_reference_output = gr.HTML()

            def update_dropdown(ns):
                choices = get_identifiers(ns)
                return gr.Dropdown(choices=choices, value=choices[0] if choices else None)

            refresh_btn.click(fn=update_dropdown, inputs=[namespace_ref_input], outputs=[identifier_dropdown])

            create_reference_btn.click(
                fn=create_reference,
                inputs=[namespace_ref_input, reference_text_input, to_input],
                outputs=[create_reference_output],
            )

            def display_segments(identifier, namespace):
                if not identifier:
                    return "", ""

                try:
                    response = requests.get(
                        f"{NER_SERVICE_URL}/segments", params={"identifier": identifier, "namespace": namespace}, timeout=30
                    )

                    if response.status_code == 200:
                        segments = response.json()
                        segments.sort(key=lambda x: x.get("segment_number", 0))

                        cards_html = '<div style="display: flex; flex-direction: column; gap: 10px;">'
                        for segment in segments:
                            full_text = segment.get("text", "N/A")
                            seg_num = segment.get("segment_number", "N/A")
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

                            details = f"## Segment {seg_num}\n\n**Text:** {full_text}"

                            cards_html += f"""<div style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                                <div style="font-weight: bold; margin-bottom: 5px;">Segment {seg_num} (Page {page}, Type: {seg_type})</div>
                                <div style="margin-bottom: 10px; white-space: pre-wrap; word-wrap: break-word;">{full_text}</div>
                                <button class="gradio-button secondary sm" onclick="document.getElementById('segment-details').innerHTML = `{details.replace(chr(10), '<br>').replace('`', '&#96;')}`">View Details</button>
                            </div>"""
                        cards_html += "</div>"

                        return cards_html, "<p>Click a segment to view details</p>"
                    else:
                        return f"<p>Error: {response.status_code}</p>", ""

                except Exception as e:
                    return f"<p>Error: {str(e)}</p>", ""

            identifier_dropdown.change(
                fn=display_segments,
                inputs=[identifier_dropdown, namespace_ref_input],
                outputs=[segments_container, selected_segment],
            )

        # Tab: Manage References
        with gr.Tab("📋 Manage References"):
            gr.Markdown("### View and Manage References")

            with gr.Row():
                with gr.Column(scale=1):
                    namespace_manage_ref = gr.Textbox(
                        label="Namespace",
                        value="default_namespace",
                    )
                    refresh_refs_btn = gr.Button("Refresh References")
                    gr.Markdown("#### References")
                    refs_container = gr.HTML(elem_id="refs-scrollable")
                with gr.Column(scale=2):
                    gr.Markdown("#### Reference Details")
                    selected_ref_details = gr.HTML(elem_id="ref-details")

            def display_references(namespace):
                if not namespace:
                    return "<p>Please enter a namespace</p>"

                try:
                    refs = get_references(namespace)
                    if not refs:
                        return "<p>No references found</p>"

                    cards_html = '<div style="display: flex; flex-direction: column; gap: 10px;">'
                    for ref in refs:
                        ref_id = ref.get("id")
                        ref_text = ref.get("reference_text", "N/A")
                        to_text = ref.get("to_text", "N/A")
                        created_at = ref.get("created_at", "N/A")

                        details = f"## Reference Details\n\n**ID:** {ref_id}\n\n**Reference Text:** {ref_text}\n\n**To:** {to_text}\n\n**Created At:** {created_at}"

                        cards_html += f"""<div style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                            <div style="font-weight: bold; margin-bottom: 5px;">Reference #{ref_id}</div>
                            <div style="margin-bottom: 10px; white-space: pre-wrap; word-wrap: break-word;"><strong>Reference:</strong> {ref_text}</div>
                            <div style="margin-bottom: 10px; white-space: pre-wrap; word-wrap: break-word;"><strong>To:</strong> {to_text}</div>
                            <button class="gradio-button secondary sm" onclick="document.getElementById('ref-details').innerHTML = `{details.replace(chr(10), '<br>').replace('`', '&#96;')}`">Show</button>
                            <button class="gradio-button danger sm" onclick="deleteRef({ref_id}, '{namespace}')">Delete</button>
                        </div>"""
                    cards_html += "</div>"

                    return cards_html
                except Exception as e:
                    return f"<p>Error: {str(e)}</p>"

            def delete_ref_handler(ref_id, namespace):
                result = delete_reference(namespace, ref_id)
                if result == "success":
                    return display_references(namespace)
                return f"<p>Error deleting reference: {result}</p>"

            refresh_refs_btn.click(fn=display_references, inputs=[namespace_manage_ref], outputs=[refs_container])

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
    # if not wait_for_backend():
    #     print("❌ Failed to connect to backend service. Exiting...", flush=True)
    #     exit(1)

    print("=" * 80, flush=True)
    print("✅  NER UI IS READY!".center(80), flush=True)
    print("=" * 80, flush=True)
    print("", flush=True)
    print("🌐 Access the UI at:", flush=True)
    print("   → http://localhost:7860", flush=True)
    print("", flush=True)
    print("=" * 80, flush=True)
    print("=" * 80 + "\n", flush=True)

    app.launch(server_name="0.0.0.0", server_port=7860, share=False, quiet=True)
