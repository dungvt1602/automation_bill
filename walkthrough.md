# Design Walkthrough

## Key Design Decisions

The most important decision was **skipping traditional OCR entirely**. Instead of chaining Tesseract → regex parsing → template matching (which breaks on every new supplier layout), I send page images directly to Gemini 2.5 Flash and let the vision model extract structured data in one pass. This makes the system layout-agnostic — it handles inconsistent formats by understanding documents visually, the same way a human operator would.

I chose **Gemini 2.5 Flash** over GPT-4o mini primarily for its native multimodal input and structured JSON output mode. At $0.003 per document (~75 VND), the monthly cost stays under 165,000 VND even at 2× peak volume — well within the 5M VND budget. The cost headroom means we can afford retries, model upgrades, or scaling without concern.

The **confidence scoring + human review loop** is the other critical choice. Rather than trusting the LLM blindly, every field carries a confidence score. Documents below threshold route to a Streamlit review UI where staff can verify and correct before export. This keeps humans in the loop without making them process every document.

## What I'd Do Differently With More Time

I'd add a **feedback learning loop**: when a reviewer corrects a field, store the correction as a few-shot example for that supplier's document type. Over time, the system's effective accuracy improves per-supplier without any model fine-tuning — just better prompts.

I'd also build **supplier-specific validation rules** (e.g., "Supplier X always ships in 20ft containers") to catch anomalies that cross-field validation alone would miss.

## One Assumption I'm Uncertain About

I'm assuming **3 pages per document on average** for cost projections. Real-world Packing Lists for mixed fruit shipments could be 8–10 pages with dense item tables. This wouldn't break the budget (even at 10 pages, cost would be ~$0.01/doc ≈ 250 VND), but it would increase processing latency. I'd want to validate this assumption against actual AGO Fruit document samples before production deployment.
