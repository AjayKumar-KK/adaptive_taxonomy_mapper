# Adaptive Taxonomy Mapper

## Quickstart

### 1) Run batch mapping on the Golden Set
```bash
python main.py
```
Outputs: `outputs/results.json`

### 2) Run the demo interface (Streamlit)
```bash
pip install -r requirements.txt
streamlit run demo/app.py
```

## Files
- `main.py` — runnable main entrypoint (batch runner)
- `src/mapper.py` — core mapping engine
- `data/taxonomy.json` — internal taxonomy
- `data/test_cases.json` — golden test cases
- `docs/SYSTEM_DESIGN.md` — system design notes
- `demo/app.py` — Streamlit demo UI
