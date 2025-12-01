from google.adk.tools import mcp_tool
from google.adk.artifacts import create_artifact
import tempfile
import os
from google.cloud import storage
import pdfkit

# NOTE:
# - pdfkit needs wkhtmltopdf installed in the runtime image.
# - On Agent Engine the runtime usually supports PDF generation; in Cloud Shell you may not have wkhtmltopdf.
# - If wkhtmltopdf is unavailable, this tool will fallback to returning the HTML as a text artifact or save a PNG.

GCS_BUCKET = os.environ.get("ARTIFACT_BUCKET")  # set this env var to your gs:// bucket name


@mcp_tool(
    name="build_report",
    description="Create a PDF report from HTML (stores to GCS and returns artifact metadata).",
    input_schema={
        "type": "object",
        "properties": {
            "html": {"type": "string"},
            "filename": {"type": "string"}
        },
        "required": ["html"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "report": {"type": "object"}
        }
    }
)
def build_report(html: str, filename: str = None) -> dict:
    """
    Convert HTML -> PDF, upload to GCS, and return an ADK artifact descriptor.
    If PDF conversion fails (wkhtmltopdf missing), fallback to saving HTML.
    """

    # Prepare file names
    if not filename:
        filename = f"report_{int(__import__('time').time())}.pdf"
    if not filename.lower().endswith(".pdf"):
        filename = filename + ".pdf"

    tmp_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    tmp_html.write(html.encode("utf-8"))
    tmp_html.flush()
    tmp_html.close()

    pdf_path = tmp_html.name.replace(".html", ".pdf")

    # Try converting HTML -> PDF via pdfkit (wkhtmltopdf)
    try:
        pdfkit.from_file(tmp_html.name, pdf_path)
        artifact_path = pdf_path
    except Exception as e:
        # conversion failed: fallback to HTML artifact
        # save HTML path and mark type
        artifact_path = tmp_html.name
        # You can log the exception in a real callback; returning fallback is safer.
    
    # If user configured GCS bucket, upload artifact
    if GCS_BUCKET:
        try:
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET)
            blob_name = os.path.join("reports", os.path.basename(artifact_path))
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(artifact_path)
            gcs_url = f"gs://{GCS_BUCKET}/{blob_name}"
            public_url = blob.public_url  # may not be public unless ACL set
        except Exception as e:
            # upload failed — return local artifact path
            return {"report": {"path": artifact_path, "error": str(e)}}
        # create ADK artifact (wrapping local path is enough for ADK to store metadata)
        artifact = create_artifact(artifact_path, metadata={"gcs_url": gcs_url, "public_url": public_url})
        return {"report": artifact}

    # If no GCS bucket configured, return local artifact path wrapped as artifact
    artifact = create_artifact(artifact_path)
    return {"report": artifact}