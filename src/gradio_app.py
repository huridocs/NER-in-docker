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
                    segments_df = gr.Dataframe(
                        headers=["#", "Page", "Type", "Text"],
                        datatype=["number", "number", "str", "str"],
                        interactive=False,
                        wrap=True,
                    )
                with gr.Column(scale=2):
                    gr.Markdown("#### Segment Details")
                    selected_segment = gr.HTML("<p>Click a row in the segments table to view details.</p>")
                    selected_segment_id = gr.State(None)

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

            segments_state = gr.State([])

            def load_segments(identifier, namespace):
                if not identifier:
                    return [], []
                try:
                    response = requests.get(
                        f"{NER_SERVICE_URL}/segments",
                        params={"identifier": identifier, "namespace": namespace},
                        timeout=30,
                    )
                    if response.status_code == 200:
                        segments = response.json()
                        segments.sort(key=lambda x: x.get("segment_number", 0))
                        rows = [
                            [
                                seg.get("segment_number", ""),
                                seg.get("page_number", ""),
                                seg.get("type", ""),
                                seg.get("text", ""),
                            ]
                            for seg in segments
                        ]
                        return segments, rows
                    return [], []
                except Exception:
                    return [], []

            def on_segment_select(segments, evt: gr.SelectData):
                row = evt.index[0]
                if row >= len(segments):
                    return "<p>No segment selected.</p>", None
                seg = segments[row]
                seg_id = seg.get("id")
                seg_num = seg.get("segment_number", "N/A")
                page = seg.get("page_number", "N/A")
                seg_type = seg.get("type", "N/A")
                text = seg.get("text", "")
                html = (
                    f"<div style='padding:10px;border:1px solid #ddd;border-radius:5px;background:#f9f9f9;'>"
                    f"<p><strong>Segment:</strong> {seg_num} &nbsp; <strong>Page:</strong> {page} &nbsp; "
                    f"<strong>Type:</strong> {seg_type} &nbsp; <strong>ID:</strong> {seg_id}</p>"
                    f"<p style='white-space:pre-wrap;word-wrap:break-word;'><strong>Text:</strong> {text}</p>"
                    f"</div>"
                )
                return html, seg_id

            def update_dropdown(ns):
                choices = get_identifiers(ns)
                if choices:
                    segs, rows = load_segments(choices[0], ns)
                    return gr.update(choices=choices, value=choices[0]), segs, rows
                return gr.update(choices=[], value=None), [], []

            refresh_btn.click(
                fn=update_dropdown,
                inputs=[namespace_ref_input],
                outputs=[identifier_dropdown, segments_state, segments_df],
            )

            identifier_dropdown.change(
                fn=load_segments,
                inputs=[identifier_dropdown, namespace_ref_input],
                outputs=[segments_state, segments_df],
            )

            segments_df.select(
                fn=on_segment_select,
                inputs=[segments_state],
                outputs=[selected_segment, selected_segment_id],
            )

            create_reference_btn.click(
                fn=create_reference,
                inputs=[namespace_ref_input, selected_segment_id, reference_text_input, to_input],
                outputs=[create_reference_output],
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
                    gr.Markdown("#### Destinations")
                    destinations_df = gr.Dataframe(
                        headers=["Destination", "Count"],
                        datatype=["str", "number"],
                        interactive=False,
                        wrap=True,
                        label="Click a row and press Compute to view references",
                    )
                    compute_btn = gr.Button("Compute", variant="primary")
                with gr.Column(scale=2):
                    gr.Markdown("#### References")
                    refs_df = gr.Dataframe(
                        headers=["ID", "Reference Text", "Segment"],
                        datatype=["number", "str", "str"],
                        interactive=False,
                        wrap=True,
                    )
                    selected_ref_id = gr.State(None)
                    delete_ref_btn = gr.Button("Delete Selected Reference", variant="stop")
                    delete_ref_output = gr.HTML()
                    gr.Markdown("#### Reference Details")
                    selected_ref_details = gr.HTML(elem_id="ref-details")

            refs_by_destination_state = gr.State({})
            selected_destination_state = gr.State(None)

            def display_references(namespace):
                if not namespace:
                    return {}, [], None, [], None, "<p>Please enter a namespace</p>"

                try:
                    refs = get_references(namespace)
                    if not refs:
                        return {}, [], None, [], None, "<p>No references found</p>"

                    # Group references by destination
                    refs_by_destination = {}
                    for group in refs:
                        group_name = group.get("name", "N/A")
                        entities = group.get("named_entities", [])
                        refs_by_destination[group_name] = []
                        for entity in entities:
                            ref_id = entity.get("id")
                            ref_text = entity.get("text", "N/A")
                            segment = entity.get("segment")
                            segment_text = (
                                segment.get("text", "N/A")[:100] + "..." if segment and segment.get("text") else "N/A"
                            )

                            ref_data = {
                                "id": ref_id,
                                "destination": group_name,
                                "reference_text": ref_text,
                                "segment_text": segment_text,
                                "segment": segment,
                            }
                            refs_by_destination[group_name].append(ref_data)

                    # Build destinations table
                    dest_rows = []
                    for dest_name, dest_refs in refs_by_destination.items():
                        dest_rows.append([dest_name, len(dest_refs)])

                    return refs_by_destination, dest_rows, None, [], None, ""
                except Exception as e:
                    return {}, [], None, [], None, f"<p>Error: {str(e)}</p>"

            def on_destination_select(destinations, refs_by_dest, evt: gr.SelectData):
                row = evt.index[0]
                if row >= len(destinations):
                    return None, [], None
                # Handle DataFrame properly - destinations is a pandas DataFrame
                dest_name = destinations.iloc[row, 0]
                refs = refs_by_dest.get(dest_name, [])

                # Build references table rows
                rows = []
                for ref in refs:
                    rows.append([ref.get("id"), ref.get("reference_text", ""), ref.get("segment_text", "")])

                return dest_name, rows, None

            def on_ref_select(refs, evt: gr.SelectData):
                row = evt.index[0]
                if row >= len(refs):
                    return None, "<p>No reference selected.</p>"

                # Handle DataFrame properly - refs is a pandas DataFrame
                ref_id = refs.iloc[row, 0]
                # Find the full reference data
                return ref_id, f"<p>Selected reference ID: {ref_id}. Click 'Delete Selected Reference' to remove.</p>"

            def compute_destination(refs_by_dest, selected_dest):
                if not selected_dest:
                    return [], None, "<p style='color: orange;'>Please select a destination first.</p>"

                refs = refs_by_dest.get(selected_dest, [])
                rows = []
                for ref in refs:
                    rows.append([ref.get("id"), ref.get("reference_text", ""), ref.get("segment_text", "")])

                return rows, None, f"<p style='color: green;'>Loaded {len(rows)} references for '{selected_dest}'</p>"

            def delete_ref_handler(ref_id, namespace, refs_by_dest):
                if not ref_id:
                    return "<p style='color: orange;'>Please select a reference to delete.</p>", refs_by_dest, [], None

                result = delete_reference(namespace, ref_id)
                if result == "success":
                    # Refresh the data
                    new_refs_by_dest, dest_rows, _, _, _, _ = display_references(namespace)
                    return "<p style='color: green;'>Reference deleted successfully!</p>", new_refs_by_dest, [], None
                return f"<p style='color: red;'>Error deleting reference: {result}</p>", refs_by_dest, [], None

            refresh_refs_btn.click(
                fn=display_references,
                inputs=[namespace_manage_ref],
                outputs=[
                    refs_by_destination_state,
                    destinations_df,
                    selected_destination_state,
                    refs_df,
                    selected_ref_id,
                    delete_ref_output,
                ],
            )

            destinations_df.select(
                fn=on_destination_select,
                inputs=[destinations_df, refs_by_destination_state],
                outputs=[selected_destination_state, refs_df, selected_ref_id],
            )

            compute_btn.click(
                fn=compute_destination,
                inputs=[refs_by_destination_state, selected_destination_state],
                outputs=[refs_df, selected_ref_id, delete_ref_output],
            )

            refs_df.select(
                fn=on_ref_select,
                inputs=[refs_df],
                outputs=[selected_ref_id, selected_ref_details],
            )

            delete_ref_btn.click(
                fn=delete_ref_handler,
                inputs=[selected_ref_id, namespace_manage_ref, refs_by_destination_state],
                outputs=[delete_ref_output, refs_by_destination_state, refs_df, selected_ref_id],
            ).then(
                fn=lambda refs_by_dest: [[dest, len(refs)] for dest, refs in refs_by_dest.items()] if refs_by_dest else [],
                inputs=[refs_by_destination_state],
                outputs=[destinations_df],
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
