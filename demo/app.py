#!/usr/bin/env python3
"""
Demo UI (Streamlit): Adaptive Taxonomy Mapper

Run:
  pip install -r requirements.txt
  streamlit run demo/app.py
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

import streamlit as st

# Ensure project root is on path so we can import src.mapper
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.mapper import TaxonomyMapper  # noqa: E402


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource
def get_mapper() -> TaxonomyMapper:
    taxonomy: Dict[str, Any] = load_json(os.path.join(ROOT, "data", "taxonomy.json"))
    return TaxonomyMapper(taxonomy)


st.set_page_config(page_title="Adaptive Taxonomy Mapper Demo", layout="centered")

st.title("Adaptive Taxonomy Mapper Demo")
st.write(
    "Enter comma-separated user tags and a story snippet. "
    "The mapper returns a taxonomy leaf (or `[UNMAPPED]`) with an explanation.\n\n"
    "**Rules implemented:** Context Wins, Honesty, Hierarchy."
)

tags_csv = st.text_input("User Tags (comma-separated)", value="Love, Future", placeholder="e.g., Love, Future")
snippet = st.text_area(
    "Story Snippet",
    height=150,
    value="A story about a man who falls in love with his AI operating system in a neon-drenched Tokyo.",
    placeholder="Paste story snippet here..."
)

col1, col2 = st.columns([1, 2])
with col1:
    run = st.button("Map to Taxonomy", type="primary")
with col2:
    st.caption("Tip: Try tags like `Ghost` with a slasher snippet, or `Action` with a courtroom snippet.")

if run:
    tags: List[str] = [t.strip() for t in (tags_csv or "").split(",") if t.strip()]
    mapper = get_mapper()
    res = mapper.map(case_id=0, user_tags=tags, snippet=snippet or "")

    st.subheader("Result")
    st.metric("Mapped Leaf", res.mapped)
    if res.path:
        st.write("**Taxonomy Path:** " + " / ".join(res.path))
    else:
        st.write("**Taxonomy Path:** -")

    st.write("**Confidence:** " + f"{res.confidence:.2f}")

    st.subheader("Reasoning Log")
    st.write(res.reasoning)

    if res.scores:
        st.subheader("Top Scores")
        # Show scores sorted
        items = sorted(res.scores.items(), key=lambda kv: kv[1], reverse=True)
        st.table([{"Leaf": k, "Score": float(v)} for k, v in items])
