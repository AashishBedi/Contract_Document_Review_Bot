import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv

from models import AnalyzeTextRequest, AnalyzeResponse, ContractAnalysis
from pdf_parser import extract_text_from_pdf
from analyzer import analyze_contract

MAX_PDF_SIZE_MB = 20
MAX_PDF_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024

load_dotenv()

app = FastAPI(
    title="ContractBot API",
    description="AI-powered contract analysis using Claude and PyMuPDF",
    version="1.0.0"
)

# Allow Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Cannot combine credentials=True with wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ContractBot API is running. POST to /analyze to analyze a contract."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze/text", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeTextRequest):
    """
    Analyze a contract provided as plain text.
    """
    if not request.contract_text or len(request.contract_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Contract text is too short or empty. Please provide the full contract text."
        )

    try:
        raw_analysis = analyze_contract(request.contract_text)
        analysis = ContractAnalysis(**raw_analysis)
        return AnalyzeResponse(success=True, analysis=analysis)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/pdf", response_model=AnalyzeResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Analyze a contract provided as a PDF upload.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a .pdf file."
        )

    # Guard against oversized uploads before reading into memory
    if file.size and file.size > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF file is too large. Maximum allowed size is {MAX_PDF_SIZE_MB}MB."
        )

    try:
        file_bytes = await file.read()
        contract_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {str(e)}")

    if len(contract_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract meaningful text from the PDF. It may be scanned or image-based."
        )

    try:
        raw_analysis = analyze_contract(contract_text)
        analysis = ContractAnalysis(**raw_analysis)
        return AnalyzeResponse(success=True, analysis=analysis)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
