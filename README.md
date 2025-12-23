# Adaptive Taxonomy Mapper

An explainable, rule-based system that maps **noisy user-generated tags and story descriptions** into a **clean internal fiction taxonomy**.  
This project demonstrates **problem-solving ability, system design, and deployment skills**, suitable for real-world content and recommendation platforms.

---

## About the Project

In many content platforms, users add tags like *Action*, *Love*, or *Scary*.  
These tags are often **inaccurate or too generic**, which leads to poor recommendations and analytics.

The **Adaptive Taxonomy Mapper** solves this problem by:
- Analyzing the **story context**
- Giving higher importance to content than user tags
- Mapping stories to a **controlled taxonomy**
- Avoiding forced or incorrect classifications
- Explaining **why** a category was chosen

---

## Live Demo

**Streamlit Deployment Link:**  
https://adaptive-taxonomy-mapper.streamlit.app 

## Project Structure

```text
adaptive_taxonomy_mapper/
│
├── main.py               # Batch execution script
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── .gitignore
│
├── src/
│   ├── __init__.py
│   └── mapper.py         # Core taxonomy mapping logic
│
├── demo/
│   └── app.py            # Streamlit demo application
│
├── data/
│   ├── taxonomy.json     # Predefined taxonomy
│   └── test_cases.json   # Sample test cases
│
├── docs/
│   └── SYSTEM_DESIGN.md  # Detailed system design
│
└── outputs/              # Generated results (created at runtime)
```
## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/AjayKumar-KK/adaptive_taxonomy_mapper.git
cd adaptive_taxonomy_mapper
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit demo
```bash
streamlit run demo/app.py
```

### 4. Run batch processing (optional)
```bash
python main.py
```

Batch results will be saved in:
```text
outputs/results.json
```
