# Proposal: Trade Document Automation for AGO Fruit

**Author:** Tiến Dũng  
**Date:** May 2026  
**Position:** IT Dept, AGO Fruit  

---

## 1. Architecture & Tech Stack

### The Problem

AGO Fruit receives 30–50 trade PDFs daily (Commercial Invoice, Packing List, Bill of Lading, Phytosanitary Certificate, Certificate of Origin) with inconsistent layouts across suppliers. Manual data entry into Excel takes 10–15 minutes per file — roughly **5–12 hours of staff time per day**.

### Proposed Solution

A **vision-LLM extraction pipeline** that sends PDF page images directly to a multimodal AI model, which returns structured JSON. No traditional OCR step is needed — the LLM reads the document visually, just like a human would.

```
┌─────────┐     ┌──────────┐     ┌───────────────────┐     ┌────────────┐
│  PDF    │────▶│ PyMuPDF  │────▶│ Gemini 2.5 Flash  │────▶│ Validation │
│ Upload  │     │ (300 DPI)│     │ (Vision + JSON)   │     │  Engine    │
└─────────┘     └──────────┘     └───────────────────┘     └─────┬──────┘
                                                                  │
                                                    ┌─────────────┴──────────────┐
                                                    │                            │
                                              confidence ≥ 0.7            confidence < 0.7
                                                    │                            │
                                              ┌─────▼─────┐           ┌─────────▼─────────┐
                                              │ Auto-export│           │ Human Review UI   │
                                              │ to Excel   │           │ (Streamlit)       │
                                              └────────────┘           │ Approve / Edit    │
                                                                       └────────┬──────────┘
                                                                                │
                                                                          ┌─────▼─────┐
                                                                          │ Export to  │
                                                                          │ Excel      │
                                                                          └────────────┘
```

### Why This Stack

| Component | Choice | Why |
|---|---|---|
| **LLM** | Gemini 2.5 Flash | Cheapest multimodal model with native JSON output, strong Vietnamese support. No separate OCR needed — images go in, structured data comes out. |
| **PDF→Image** | PyMuPDF (fitz) | Pure Python — no system dependency like Poppler. One `pip install` on any OS. |
| **Validation** | Pydantic | Type-safe schemas with built-in validation. Each field carries a confidence score (0.0–1.0). |
| **Review UI** | Streamlit | A junior developer can build and modify the UI in Python alone — no React/Vue required. |
| **Database** | SQLite | Zero-config, file-based. Sufficient for 30–50 docs/day. Full audit trail. |
| **Excel** | openpyxl | Standard Python Excel library. Supports formatting, conditional highlighting, multiple sheets. |

**Key design principle:** Every component is maintainable by a junior developer with no ML background. There are no model training steps, no GPU requirements, no custom ML pipelines. The entire system is prompt engineering + API calls.

---

## 2. Cost Breakdown

### Pricing Source

- **Model:** Gemini 2.5 Flash via Google AI API  
- **Source:** [https://ai.google.dev/pricing](https://ai.google.dev/pricing) (checked May 11, 2026)  
- **Input:** $0.30 per 1M tokens  
- **Output:** $2.50 per 1M tokens  

### Per-Document Cost

| Item | Tokens | Cost (USD) |
|---|---|---|
| Input: 3 page images × ~1,000 tokens each | 3,000 | $0.0009 |
| Input: system prompt + JSON schema | 500 | $0.00015 |
| Output: structured JSON result | 800 | $0.002 |
| **Total per document** | **4,300** | **≈ $0.003 (75 VND)** |

### Monthly Projection

| Scenario | Docs/day | Docs/month (22 working days) | Monthly Cost |
|---|---|---|---|
| Normal low | 30 | 660 | $2.00 ≈ **50,000 VND** |
| Normal high | 50 | 1,100 | $3.30 ≈ **83,000 VND** |
| Peak (2× buffer) | 100 | 2,200 | $6.60 ≈ **165,000 VND** |

**Verdict:** At peak load, the system uses **3.3% of the 5,000,000 VND/month budget**. This leaves ample room for:
- Retries on failed extractions (2–3× per failed doc)
- Switching to a more expensive model (e.g., Gemini 2.5 Pro) for difficult documents
- Scaling to higher volumes as the business grows

---

## 3. Edge Cases & Mitigation

### 3.1 Low-Quality Scans

**Problem:** Blurry photos, skewed scans, low-resolution faxes.  
**Solution:**
- Image preprocessing: auto-contrast enhancement, deskewing via PyMuPDF
- If overall confidence < 0.5 after extraction, flag as **"needs manual entry"** — don't attempt to auto-extract garbage
- The LLM still performs surprisingly well on degraded images (better than traditional OCR), because it uses contextual understanding, not just character recognition

### 3.2 Hallucinated Data

**Problem:** LLM invents plausible-looking data (e.g., a container number that looks real but isn't on the document).  
**Solution:**
- **Cross-field validation:** Do line item totals sum to the invoice total? Does the date make sense?
- **Confidence gating:** Fields below 0.7 confidence are always sent to human review
- **Format validation:** Container numbers must match ISO 6346 format; dates must be valid; currencies must be in the known set
- **Never auto-approve first-time supplier layouts** — require human validation for the first 5 documents from a new supplier

### 3.3 API Rate Limits & Downtime

**Problem:** Google API has rate limits; outages happen.  
**Solution:**
- Tenacity library for exponential backoff with jitter (max 3 retries)
- Queue-based processing: failed docs go to a retry queue
- Batch API option for non-urgent processing (50% cost discount)
- Graceful degradation: if the API is down, documents queue up and process when it's back

### 3.4 Inconsistent Layouts

**Problem:** Every supplier formats their invoices differently.  
**Solution:** This is precisely why we use an LLM instead of template-based OCR. The prompt defines **what fields to extract** (semantically), not **where they are** on the page. The model understands document structure visually.

### 3.5 Mixed Vietnamese / English Content

**Problem:** Trade documents often mix Vietnamese and English text.  
**Solution:** Gemini 2.5 Flash handles multilingual input natively. The extraction prompt explicitly instructs: *"Documents may contain Vietnamese, English, or both. Extract all fields regardless of language."*

---

## 4. Management Controls

### 4.1 Approval Gates

| Gate | Trigger | Action |
|---|---|---|
| **Auto-approve** | All fields confidence ≥ 0.7 | Direct export to Excel |
| **Review required** | Any field confidence < 0.7 | Route to human reviewer in Streamlit UI |
| **Manual entry** | Overall confidence < 0.5 | Flag as "low quality" — suggest manual entry |
| **New supplier** | First 5 docs from unknown supplier | Always require human review |

### 4.2 Audit Log

Every action is recorded in SQLite with full traceability:

```
documents
├── id, filename, upload_time, uploaded_by
├── document_type (auto-detected)
├── overall_confidence
└── status: pending → extracted → reviewed → approved → exported

audit_log
├── document_id
├── action: upload | extract | review | edit_field | approve | reject | export
├── user
├── timestamp
├── details (JSON: what changed, old value → new value)
```

### 4.3 Cost Monitoring Dashboard

The Streamlit UI includes a cost monitoring tab showing:
- Token usage per document and per day
- Running monthly cost vs. budget (5M VND)
- Alert if projected monthly cost exceeds 80% of budget

### 4.4 Data Governance

- All extracted data stays on-premise in SQLite (no third-party storage)
- Only document images are sent to the Gemini API for processing
- API key rotation is supported via `.env` configuration
- Export history is maintained for compliance audits
