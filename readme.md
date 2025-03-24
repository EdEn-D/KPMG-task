# KPMG Home Assignment

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/kpmg-task.git
cd kpmg-task
```

### 2. Create and Activate a Virtual Environment

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For MacOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Configure the following environment variables:

**Azure Document Intelligence:**
- `AZURE_DOCUMENT_KEY`
- `AZURE_DOCUMENT_ENDPOINT`

**Azure OpenAI:**
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

**Azure OpenAI Embeddings (for RAG):**
- `AZURE_EMBEDDING_DEPLOYMENT`
- `AZURE_EMBEDDING_ENDPOINT`
- `AZURE_EMBEDDING_API_VERSION`

## Running the Project

### Phase 1: Field Extraction using Document Intelligence & Azure OpenAI

```bash
python phase1/main.py
```

- Upload a document and wait for the JSON output.

### Phase 2: Microservice-based ChatBot Q&A on Medical Services

**Requirements:**
- Create a `data` folder in the root directory
- Populate the folder with HTML files from the 'phase2_data' folder

```bash
python phase2/main.py
```

**Services:**
- Backend API: http://localhost:5051
- Streamlit UI: http://localhost:8501

**Usage:**
1. Start by sending a message to the chatbot
2. The bot will provide a list of questions to fill out the form
3. After completing the form, you can ask questions about medical services