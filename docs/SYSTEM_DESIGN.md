# System Design Notes — Adaptive Taxonomy Mapper

## 1) Scaling taxonomy from ~12 to 5,000 categories
- **Index leaves**: flatten the taxonomy to leaf nodes with stable IDs, parent path, and metadata (synonyms, examples, related tags).
- **Two-stage retrieval**:
  1. **Candidate generation** (fast): BM25 keyword search + vector search over leaf descriptions/examples to get top-K candidates.
  2. **Reranking / classification** (accurate): a small supervised classifier or cross-encoder reranker selects best leaf among K.
- **Taxonomy updates**: version taxonomy, keep backward compatibility by mapping old IDs to new IDs.

## 2) Cost control for 1 million stories/month (if using LLMs)
- **Do not call an LLM for every story**. Use rules + lightweight classifiers first.
- **Escalate only hard cases**: ambiguous inputs, low confidence, or conflicts between tags and snippet.
- **Caching**: store results for near-duplicate snippets; reuse for repeated creators/series.
- **Batch & token control**: batch requests, summarize/trim inputs, enforce strict output formats.

## 3) Prevent hallucinating categories not in JSON
- **Allow-list**: output must be one of the leaf labels present in `taxonomy.json` (or `[UNMAPPED]`).
- **Validation layer**: hard-check output membership; if invalid, retry with constraints or force `[UNMAPPED]`.
- **Structured outputs**: use schemas (JSON mode) if using an LLM; reject unknown keys/values.

---

This prototype intentionally uses a transparent, deterministic scorer so the submission shows personal problem-solving rather than fully LLM-generated outputs.
