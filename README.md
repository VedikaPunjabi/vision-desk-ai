# 🛡️ Vision Desk AI — Enterprise Workplace Safety & Intelligence Suite

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow.svg)](https://github.com/ultralytics/ultralytics)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-red.svg)](https://www.langchain.com/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Vision Desk AI** is an enterprise-grade, multimodal workplace safety monitoring, compliance analysis, and agentic incident investigation platform. 

It combines **Real-time Computer Vision (YOLOv8)**, **Multimodal Document RAG (ChromaDB + Gemini)**, **Autonomous Multi-Agent Investigation (LangGraph)**, and an **Interactive Executive Analytics Dashboard** to detect workplace hazards, verify regulatory policies, and generate audit-ready compliance reports.

---

## 🌟 Key Capabilities & Modules

- **🎯 Real-Time PPE & Hazard Vision Detection:** Detects workers, hardhats, high-visibility vests, gloves, boots, and unsafe equipment in both images and high-fps video feeds.
- **📄 OCR & Document Intelligence Pipeline:** Extracts, chunks, and indexes unstructured safety SOPs and compliance PDFs (with automated OCR fallback for scanned documents).
- **🔗 Multimodal Incident Correlation Engine:** Automatically cross-references visual detections against retrieved policy clauses to flag non-compliance with severity ratings.
- **💬 Grounded Policy Safety QA Assistant:** Vector-search-backed question-answering assistant that cites exact policy sections and visual evidence.
- **🤖 Autonomous Multi-Agent Root Cause Investigation:** Multi-agent LangGraph workflow (Query Analysis ➔ Document Retrieval ➔ Visual Analysis ➔ Evidence Validation ➔ Reasoning ➔ Report Generation) with human sign-off.
- **📊 Executive Safety Dashboard & Audit Reporting:** Live workplace compliance percentage, department safety scoreboard, filterable incident log, and 1-click CSV report exports.

---

## 🏗️ Project Architecture & Structure

```text
vision-desk-ai/
├── .env.example                  # Template for API keys & secrets
├── .gitignore                    # Git ignore file for models & databases
├── LICENSE                       # MIT License
├── README.md                     # Project documentation
├── requirements.txt              # Production dependencies
├── app.py                        # Central Flask server & analytics REST API
│
├── frontend/                     # Modern UI & Dashboard
│   ├── index.html                # Unified single-page interface
│   ├── style.css                 # Enterprise dark-theme stylesheet
│   └── script.js                 # Chart.js bindings, filters & state management
│
└── modules/                      # Core AI & Intelligence Engines
    ├── __init__.py               # Package marker
    ├── vision_detector.py        # YOLOv8 PPE & Safety Detector
    ├── document_processor.py     # PDF/DOCX text & OCR extraction
    ├── chunker.py                # Sentence-aware chunker
    ├── embeddings.py             # SentenceTransformers embedding generation
    ├── vector_store.py           # ChromaDB persistent store
    ├── document_pipeline.py      # End-to-end document ingestion pipeline
    ├── incident_correlation.py   # Multimodal correlation engine
    ├── safety_qa.py              # Policy RAG & QA system
    │
    └── investigation/            # Multi-Agent Investigation System
        ├── __init__.py           # Sub-package marker
        ├── state.py              # Investigation StateGraph schema
        ├── agents.py             # Autonomous agent nodes
        ├── workflow.py           # LangGraph orchestration graph
        └── run.py                # Standalone CLI investigation test tool

```
---

## 🛠️ Tech Stack

- **Backend / APIs:** Python, Flask, Flask-SQLAlchemy, Flask-Bcrypt
- **Computer Vision:** Ultralytics YOLOv8, OpenCV, PyTorch, HuggingFace Hub
- **Document Processing & Vector DB:** PyMuPDF, Pytesseract, Sentence-Transformers, ChromaDB
- **LLM & Agent Frameworks:** Google Gemini 2.5 Flash, LangGraph, LangChain Google GenAI
- **Frontend / Visualization:** HTML5, Modern CSS Grid/Flexbox, Vanilla JS, Chart.js

---

## ⚙️ Installation & Quickstart

**1. Clone the Repository**
```bash
git clone https://github.com/your-username/vision-desk-ai.git
cd vision-desk-ai
```

**2. Set Up Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
- Create a `.env` file in the root folder (or duplicate `.env.example`):
```bash
SECRET_KEY=your-custom-secret-key-2025
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

> *Note: If no Gemini API key is provided, the system seamlessly operates in local offline demonstration mode.* 

---

## 🚀 Running the Platform

Launch the Flask application:
```bash
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 📡 REST API Summary
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/login` | `POST` | Authenticates user session |
| `/api/signup` | `POST` | Creates a new user account |
| `/api/analyze` | `POST` | Uploads media and executes YOLOv8 object & PPE detection |
| `/api/process-document` | `POST` | Parses and indexes uploaded safety documents into ChromaDB |
| `/api/correlate` | `POST` | Correlates visual observations against safety policies |
| `/api/safety-qa` | `POST` | Queries the RAG safety policy knowledge base |
| `/api/investigate` | `POST` | Triggers the LangGraph multi-agent root-cause investigation |
| `/api/dashboard/metrics` | `GET` | Fetches live KPIs, compliance %, and department scores |
| `/api/dashboard/violations` | `GET` | Retrieves filterable violation records |
| `/api/dashboard/update-status` | `POST` | Updates status of a violation (`Open` ➔ `Resolved`) |
| `/api/dashboard/export/csv` | `GET` | Generates and downloads a CSV compliance report |

---
## 📄 License
This project is licensed under the MIT License - see the `LICENSE` file for details.
