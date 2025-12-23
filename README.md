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
adaptive_taxonomy_mapper/
│
├── main.py               # Batch execution script
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── .gitignore
│
├── src/
│   ├── init.py
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
