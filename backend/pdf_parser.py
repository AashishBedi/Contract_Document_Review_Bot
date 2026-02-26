import fitz  # PyMuPDF
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file given its raw bytes.
    Returns the extracted text as a single string.
    Raises ValueError if no text could be extracted.
    """
    text_parts = []

    try:
        pdf_stream = io.BytesIO(file_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(page_text.strip())

        doc.close()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")

    if not text_parts:
        raise ValueError(
            "No readable text found in the PDF. "
            "The file may be scanned or image-based."
        )

    return "\n\n".join(text_parts)
