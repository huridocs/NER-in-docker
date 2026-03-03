import streamlit as st
import requests
import json
import tempfile
import base64
from typing import Tuple, Optional, List

from gradio_ui.api import (
    extract_entities_from_text as _extract_entities_from_text,
    extract_entities_from_pdf as _extract_entities_from_pdf,
    extract_entities_from_text_llm as _extract_entities_from_text_llm,
    extract_entities_from_pdf_llm as _extract_entities_from_pdf_llm,
    save_texts_from_pdfs as _save_texts_from_pdfs,
    visualize_pdf as _visualize_pdf,
    get_identifiers,
    get_segments as _get_segments,
    create_reference as _create_reference,
    get_references,
    delete_reference,
)
from gradio_ui.formatters import create_legend, format_entities_html
from gradio_ui.constants import NER_SERVICE_URL, ENTITY_COLORS

st.set_page_config(
    page_title="Named Entity Recognition",
    page_icon="🔍",
    layout="wide",
)

st.markdown("# 🔍 Named Entity Recognition Service")
st.markdown("Extract named entities from text or PDF documents using state-of-the-art NER models.")

st.markdown(create_legend(), unsafe_allow_html=True)


def extract_entities_from_text(text: str, language: str = "en") -> Tuple[str, str]:
    return _extract_entities_from_text(text, language)


def extract_entities_from_pdf(pdf_file, language: str = "en", fast: bool = False) -> Tuple[str, str]:
    return _extract_entities_from_pdf(pdf_file, language, fast)


def extract_entities_from_text_llm(text: str, language: str = "en") -> Tuple[str, str]:
    return _extract_entities_from_text_llm(text, language)


def extract_entities_from_pdf_llm(pdf_file, language: str = "en", fast: bool = False) -> Tuple[str, str]:
    return _extract_entities_from_pdf_llm(pdf_file, language, fast)


def save_texts_from_pdfs(pdf_files, namespace: str, identifier: str, language: str = "en", fast: bool = False) -> str:
    return _save_texts_from_pdfs(pdf_files, namespace, identifier, language, fast)


def visualize_pdf(pdf_file, language: str = "en", fast: bool = False) -> Tuple[Optional[str], str]:
    return _visualize_pdf(pdf_file, language, fast)


def get_segments(identifier: str, namespace: str = "default_namespace") -> List[dict]:
    if not identifier:
        return []
    try:
        response = requests.get(
            f"{NER_SERVICE_URL}/segments", params={"identifier": identifier, "namespace": namespace}, timeout=30
        )
        if response.status_code == 200:
            segments = response.json()
            segments.sort(key=lambda x: x.get("segment_number", 0))
            return segments
        return []
    except Exception:
        return []


def create_reference(namespace: str, segment_id: Optional[str], reference_text: str, to_text: str) -> str:
    return _create_reference(namespace, segment_id, reference_text, to_text)


tab_create_ref, tab_manage_ref, tab_save_texts, tab_text_extraction, tab_pdf_extraction, tab_llm_extraction = st.tabs(
    [
        "📚 Create References",
        "📋 Manage References",
        "💾 Save Texts",
        "📝 Text Extraction",
        "📄 PDF Entity Extraction & Visualization",
        "🤖 LLM Text Extraction",
    ]
)

with tab_create_ref:
    st.markdown("### View References")

    col1, col2 = st.columns([1, 2])

    with col1:
        namespace_ref = st.text_input("Namespace", value="default_namespace", key="namespace_ref")
        if st.button("Refresh Identifiers", key="refresh_btn"):
            st.session_state.identifiers = get_identifiers(namespace_ref)

        if "identifiers" not in st.session_state:
            st.session_state.identifiers = get_identifiers(namespace_ref)

        identifier = st.selectbox(
            "Identifiers",
            options=st.session_state.identifiers if st.session_state.identifiers else [],
            index=0 if st.session_state.identifiers else None,
            key="identifier_dropdown",
        )

        st.markdown("#### Segments")

        segments = []
        if identifier:
            segments = get_segments(identifier, namespace_ref)

        if segments:
            segment_data = [
                {
                    "#": seg.get("segment_number", ""),
                    "Page": seg.get("page_number", ""),
                    "Type": seg.get("type", ""),
                    "Text": seg.get("text", ""),
                }
                for seg in segments
            ]
            st.dataframe(segment_data, use_container_width=True, height=400, key="segments_df")

            selected_segment_idx = st.selectbox(
                "Select a segment",
                options=range(len(segments)),
                format_func=lambda i: f"Segment {segments[i].get('segment_number', 'N/A')} - Page {segments[i].get('page_number', 'N/A')}",
                key="segment_select",
            )

            if selected_segment_idx is not None:
                seg = segments[selected_segment_idx]
                st.markdown("#### Segment Details")
                st.markdown(
                    f"**Segment:** {seg.get('segment_number', 'N/A')} | **Page:** {seg.get('page_number', 'N/A')} | **Type:** {seg.get('type', 'N/A')} | **ID:** {seg.get('id', 'N/A')}"
                )
                st.markdown(f"**Text:** {seg.get('text', '')}")

                selected_segment_id = str(seg.get("id", ""))
            else:
                selected_segment_id = None
        else:
            st.info("No segments found")
            selected_segment_id = None

    with col2:
        st.markdown("#### Create Reference")

        reference_text = st.text_input("Reference Text", placeholder="Enter reference text...", key="ref_text_input")
        to_input = st.text_input("To", placeholder="Enter target...", key="to_input")

        if st.button("Create Reference", type="primary", key="create_ref_btn"):
            result = create_reference(namespace_ref, selected_segment_id, reference_text, to_input)
            st.markdown(result, unsafe_allow_html=True)

with tab_manage_ref:
    st.markdown("### View and Manage References")

    col1, col2 = st.columns([1, 2])

    with col1:
        namespace_manage = st.text_input("Namespace", value="default_namespace", key="namespace_manage")
        if st.button("Refresh References", key="refresh_refs_btn"):
            st.session_state.references = get_references(namespace_manage)

        if "references" not in st.session_state:
            st.session_state.references = get_references(namespace_manage)

        st.markdown("#### References")

        refs = st.session_state.references

        if refs:
            for group in refs:
                group_name = group.get("name", "N/A")
                entities = group.get("named_entities", [])
                for entity in entities:
                    ref_text = entity.get("text", "N/A")
                    segment = entity.get("segment")
                    segment_text = segment.get("text", "N/A") if segment else "N/A"

                    with st.container():
                        st.markdown(f"**Destination:** {group_name}")
                        st.markdown(f"**Reference:** {ref_text}")
                        st.markdown(f"**Segment:** {segment_text}")
                        st.divider()
        else:
            st.info("No references found")

    with col2:
        st.markdown("#### Reference Details")
        st.info("Select a reference from the list to view details")

with tab_save_texts:
    st.markdown("### Save text from multiple PDFs")
    st.markdown("Upload multiple PDF documents to extract and save their text content.")

    col1, col2 = st.columns([1, 2])

    with col1:
        pdf_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True, key="pdf_save")
        namespace = st.text_input("Namespace", placeholder="Enter namespace (e.g., 'my_docs')", key="namespace_save")
        identifier_prefix = st.text_input(
            "Identifier Prefix", placeholder="Enter identifier prefix (optional)", key="id_prefix"
        )
        language_save = st.selectbox("Language", options=["en", "es", "de", "fr"], index=0, key="lang_save")
        fast_mode_save = st.checkbox("Fast Mode", value=False, help="Enable for faster processing", key="fast_save")

        save_btn = st.button("Save Texts", type="primary", key="save_btn")

    with col2:
        if save_btn:
            result = save_texts_from_pdfs(pdf_files, namespace, identifier_prefix, language_save, fast_mode_save)
            st.markdown(result, unsafe_allow_html=True)

with tab_text_extraction:
    st.markdown("### Extract entities from text")
    st.markdown("Enter your text below and click 'Extract Entities' to identify named entities.")

    col1, col2 = st.columns(2)

    with col1:
        text_input = st.text_area(
            "Input Text",
            placeholder="Enter text here... (e.g., 'John Smith works at Microsoft in Seattle since January 2020.')",
            height=200,
            key="text_input",
        )
        language_text = st.selectbox(
            "Language",
            options=["en", "es", "de", "fr"],
            index=0,
            key="lang_text",
        )
        extract_text_btn = st.button("Extract Entities", type="primary", key="extract_text_btn")

    with col2:
        if extract_text_btn:
            entities_html, json_response = extract_entities_from_text(text_input, language_text)
            st.markdown("### Extracted Entities")
            st.markdown(entities_html, unsafe_allow_html=True)

            with st.expander("📋 View JSON Response"):
                st.code(json_response, language="json")

    st.markdown("#### Example Texts")
    example_texts = [
        "John Smith works at Microsoft in Seattle since January 2020. He reports to the CEO under Article 15 of the company bylaws.",
        "The United Nations held a meeting in Geneva on March 15, 2024, discussing international law reforms.",
        "Dr. Sarah Johnson from Harvard University published research in Nature magazine last week.",
    ]
    for i, example in enumerate(example_texts):
        if st.button(f"Load Example {i+1}", key=f"example_{i}"):
            st.session_state.text_input = example

with tab_pdf_extraction:
    st.markdown("### Extract and Visualize entities from PDF")
    st.markdown("Upload a PDF document to extract named entities, get the JSON response, or generate an annotated version.")

    col1, col2 = st.columns([1, 2])

    with col1:
        pdf_file = st.file_uploader("Upload PDF", type="pdf", key="pdf_entity")
        language_pdf = st.selectbox(
            "Language",
            options=["en", "es", "de", "fr"],
            index=0,
            key="lang_pdf",
        )
        fast_mode_pdf = st.checkbox(
            "Fast Mode", value=False, help="Enable for faster processing (less accurate segmentation)", key="fast_pdf"
        )

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            extract_pdf_btn = st.button("Extract Entities", type="primary", key="extract_pdf_btn")
        with btn_col2:
            visualize_btn = st.button("Generate Visualization", key="visualize_btn")

    with col2:
        tab_entities, tab_visualization = st.tabs(["📋 Extracted Entities", "🎨 Visualization"])

        with tab_entities:
            if extract_pdf_btn:
                entities_html, json_response = extract_entities_from_pdf(pdf_file, language_pdf, fast_mode_pdf)
                st.markdown(entities_html, unsafe_allow_html=True)

                with st.expander("📋 View JSON Response"):
                    st.code(json_response, language="json")

        with tab_visualization:
            if visualize_btn:
                annotated_pdf, pdf_preview = visualize_pdf(pdf_file, language_pdf, fast_mode_pdf)
                if annotated_pdf:
                    with open(annotated_pdf, "rb") as f:
                        st.download_button(
                            label="Download Annotated PDF",
                            data=f,
                            file_name="annotated_document.pdf",
                            mime="application/pdf",
                            key="download_annotated",
                        )
                st.markdown("#### PDF Preview:")
                st.markdown(pdf_preview, unsafe_allow_html=True)

with tab_llm_extraction:
    st.markdown("### Extract entities from text using LLM")
    st.markdown(
        "Use Large Language Models (Ollama) for entity extraction. This method can provide different results compared to traditional NER models."
    )

    col1, col2 = st.columns(2)

    with col1:
        text_input_llm = st.text_area(
            "Input Text",
            placeholder="Enter text here... (e.g., 'John Smith works at Microsoft in Seattle since January 2020.')",
            height=200,
            key="text_input_llm",
        )
        language_llm = st.selectbox(
            "Language",
            options=["en", "es", "de", "fr"],
            index=0,
            key="lang_llm",
        )
        extract_llm_btn = st.button("Extract Entities (LLM)", type="primary", key="extract_llm_btn")

    with col2:
        if extract_llm_btn:
            entities_html, json_response = extract_entities_from_text_llm(text_input_llm, language_llm)
            st.markdown("### Extracted Entities")
            st.markdown(entities_html, unsafe_allow_html=True)

            with st.expander("📋 View JSON Response"):
                st.code(json_response, language="json")

    st.markdown("#### Example Texts")
    for i, example in enumerate(example_texts):
        if st.button(f"Load Example {i+1}", key=f"example_llm_{i}"):
            st.session_state.text_input_llm = example

st.markdown("---")
st.markdown(
    "Built with [Streamlit](https://streamlit.io) | Powered by [NER-in-docker](https://github.com/huridocs/NER-in-docker)"
)

if __name__ == "__main__":
    pass
