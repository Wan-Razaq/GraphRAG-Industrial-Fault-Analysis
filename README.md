# GraphRAG: Industrial Fault Diagnosis using Knowledge Graph and LLM

This project leverages Large Language Models (LLMs) combined with Knowledge Graphs (KG) to enhance the process of fault diagnosis in industrial machinery, specifically for IBM3 and IBM4 systems. The main approach used is Graph Retrieval-Augmented Generation (GraphRAG).

The pipeline consists of:
- Data Preprocessing: Combining and cleaning historical maintenance logs and manual book data.
- Knowledge Extraction: Using few-shot prompting (GPT-4) + BAML to extract structured entities.
- Evaluation: Assessing entity extraction quality using manually annotated data.
- Knowledge Graph Construction: Integrating extracted data into Neo4j.
- Downstream Application: Streamlit chatbot leveraging Neo4j GraphRAG for interactive troubleshooting. The chatbot support multilingual (EN/NL) built using Streamlit


##  Project Structure

graphRAG-industrial-fault-diagnosis/
├── data/
│   ├── raw/
│   │   └── Original maintenance logs and manual book images
│   └── processed/
│       └── Cleaned and structured JSON and JSONL datasets
├── notebooks/
│   ├── data_preprocessing/
│   ├── knowledge_extraction/
│   └── chatbot_experimentation/
├── src/
│   ├── models/
│   ├── utils/
│   └── App and chatbot logic
├── experiments/
│   ├── evaluation_results/
│   └── logs/
├── trained_models/
├── requirements.txt
└── README.md

##  Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Wan-Razaq/GraphRAG-Industrial-Fault-Analysis.git
cd graphRAG-industrial-fault-diagnosis

### 2. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

### 3. Set up virtual environment

Create a .env file in the root directory:

```bash
OPENAI_API_KEY=your-openai-api-key
NEO4J_URI=your-neo4j-uri
NEO4J_USER=your-neo4j-user
NEO4J_PASS=your-neo4j-password

### 4. Run the Streamlit Chatbot

```bash
streamlit run src/streamlit_app2.py


##  Key Technologies

Neo4j – Graph database for structured fault representation

OpenAI GPT-4 – Used for knowledge extraction and chatbot generation

Streamlit – Interactive chatbot frontend

D3.js – Graph visualizations embedded in the chatbot interface

