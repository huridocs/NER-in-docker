import requests
import json
import tempfile
import time
from typing import Tuple, Optional

from .constants import NER_SERVICE_URL
from .formatters import format_entities_html


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


def save_texts_from_pdfs(pdf_files, namespace: str, identifier: str, language: str = "en", fast: bool = False) -> str:
    """Save text from multiple PDFs using the save_text endpoint."""
    if not pdf_files or len(pdf_files) == 0:
        return "<p style='color: red;'>Please upload at least one PDF file.</p>"

    if not namespace:
        namespace = "default_namespace"

    try:
        results = []
        for i, pdf_file in enumerate(pdf_files):
            with open(pdf_file, "rb") as f:
                pdf_content = f.read()

            file_name = pdf_file.split("/")[-1] if "/" in pdf_file else pdf_file
            files = {"file": (file_name, pdf_content, "application/pdf")}

            current_identifier = f"{identifier}_{i+1}" if identifier else file_name
            data = {"namespace": namespace, "identifier": current_identifier, "language": language, "fast": fast}

            response = requests.post(f"{NER_SERVICE_URL}/save_text", files=files, data=data, timeout=300)

            if response.status_code == 200:
                results.append(f"✓ {file_name}: {response.text}")
            else:
                results.append(f"✗ {file_name}: Error - {response.status_code}")

        return "<p>Processing Results:</p><ul>" + "".join([f"<li>{r}</li>" for r in results]) + "</ul>"

    except requests.exceptions.ConnectionError:
        return "<p style='color: red;'>Error: Cannot connect to NER service. Make sure it's running.</p>"
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"


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


def wait_for_backend(max_retries: int = 60, retry_interval: int = 2) -> bool:
    """Wait for the backend service to be ready by polling the info endpoint."""
    print("\n" + "=" * 80, flush=True)
    print("⏳ Waiting for NER backend service to be ready...".center(80), flush=True)
    print("=" * 80 + "\n", flush=True)

    for _ in range(1, max_retries + 1):
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


def get_identifiers(namespace: str = "default_namespace") -> list:
    """Get all identifiers for a given namespace."""
    try:
        response = requests.get(f"{NER_SERVICE_URL}/identifiers", params={"namespace": namespace}, timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def get_segments(identifier: str, namespace: str = "default_namespace") -> str:
    """Get segments for a given identifier."""
    if not identifier:
        return ""
    try:
        response = requests.get(
            f"{NER_SERVICE_URL}/segments", params={"identifier": identifier, "namespace": namespace}, timeout=30
        )
        if response.status_code == 200:
            segments = response.json()
            return json.dumps(segments, indent=2)
        return f"Error: {response.status_code}"
    except Exception as e:
        return str(e)


def create_reference(namespace: str, reference_text: str, to_text: str) -> str:
    """Create a reference in the backend."""
    if not namespace:
        namespace = "default_namespace"
    if not reference_text or not to_text:
        return "<p style='color: red;'>Please provide reference text and target text.</p>"

    try:
        data = {"namespace": namespace, "segment_text": "", "reference_text": reference_text, "to_text": to_text}
        response = requests.post(f"{NER_SERVICE_URL}/create_reference", data=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return "<p style='color: green;'>Reference created successfully!</p>"
            else:
                return f"<p style='color: red;'>Error: {result.get('message')}</p>"
        else:
            return f"<p style='color: red;'>Error: Service returned status code {response.status_code}</p>"
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"


def get_references(namespace: str = "default_namespace") -> list:
    """Get all references for a given namespace."""
    try:
        response = requests.get(f"{NER_SERVICE_URL}/references", params={"namespace": namespace}, timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def delete_reference(namespace: str, reference_id: int) -> str:
    """Delete a reference by ID."""
    try:
        data = {"namespace": namespace, "reference_id": reference_id}
        response = requests.post(f"{NER_SERVICE_URL}/delete_reference", data=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return "success"
            else:
                return f"Error: {result.get('message')}"
        else:
            return f"Error: Service returned status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
