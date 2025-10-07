# Multi-Hops Agentic RAG System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)

After researching advanced RAG architectures, this repository implements a multi-hop agentic RAG system using LangGraph, drawing from adaptive and agentic RAG patterns (e.g., as described in resources like "Building Agentic Adaptive RAG with LangGraph" and "Agentic Retrieval-Augmented Generation: A Survey"). These systems enhance traditional RAG by incorporating intelligent agents for dynamic multi-step reasoning, hop selection based on query complexity, and iterative retrieval loops to handle complex queries through decision-making, context assessment, and parallel strategies, ensuring more accurate and comprehensive responses without relying on fixed retrieval pipelines.
The system ingests PDFs, embeds them using Azure OpenAI, stores them in PGVector (PostgreSQL-based vector database), and provides a Streamlit web interface for querying.

## Demo

![System Flow Diagram](langgraph_nodes.png)
*(The diagram above is the original flowchart. Below is a visual representation in Mermaid for interactive viewing in GitHub or compatible viewers.)*

### System Architecture Flowchart (Mermaid Canvas)

GitHub renders Mermaid diagrams as interactive canvases. Copy the code below into a Markdown file or use tools like Mermaid Live (https://mermaid.live) to view/edit it as a canvas.

```mermaid
flowchart TD
    START([START]) --> analyze_question[analyze_question\n- Question complexity\n- Question type\n- Estimated hops]
    analyze_question --> enhanced_plan[enhanced_plan\n- Generate sub-questions\n- Priority tasks\n- Strategy selection]
    enhanced_plan --> parallel_retrieve[parallel_retrieve\n- Semantic search\n- Similarity search\n- Hybrid fusion]
    parallel_retrieve --> advanced_assess[advanced_assess\n- Quality scoring\n- Coverage analysis\n- Gap detection]
    advanced_assess --> intelligent_decide[intelligent_decide\n- Multi-factor analysis\n- Stop: False]
    intelligent_decide -->|stop: False| enhanced_plan
    intelligent_decide -->|stop: True| enhanced_synthesis[enhanced_synthesis\n- Evidence integration\n- Answer generation\n- Confidence scoring]
    enhanced_synthesis --> advanced_verify[advanced_verify\n- Grounding check\n- Factual validation\n- Quality assurance]
    advanced_verify --> END([END])
```

## Architecture Overview

The core of the system is an **intelligent agent loop** implemented using [LangGraph](https://langchain-ai.github.io/langgraph/), a graph-based workflow engine for building multi-agent systems. The architecture follows a structured flow (as shown in the Mermaid diagram above) to handle queries efficiently, ensuring high-quality, grounded responses. It starts with question analysis and iteratively retrieves, assesses, and synthesizes information until sufficient context is gathered.

### High-Level Flow

1. **START**: User inputs a question (e.g., via Streamlit app).
2. **analyze_question**: Analyzes question complexity, type, and required evidence.
3. **enhanced_plan**: Generates sub-questions and retrieval strategies based on gaps.
4. **parallel_retrieve**: Performs multi-strategy retrieval (semantic, similarity) from the vector store.
5. **advanced_assess**: Evaluates retrieved context for quality, coverage, and gaps.
6. **intelligent_decide**: Decides to loop back (for more retrieval) or proceed based on multi-factor assessment.
7. **enhanced_synthesis**: Synthesizes a final answer with confidence scoring.
8. **advanced_verify**: Verifies the answer for grounding, consistency, and completeness.
9. **END**: Outputs the verified answer with sources and metrics.

If the decision node determines more hops are needed (e.g., due to information gaps), it loops back to planning/retrieval (up to a configurable max hops).

### Detailed Component Breakdown

- **State Management**: Uses a typed dictionary (`EnhancedAgentState`) to track state across nodes, including question details, evidence docs, scores (e.g., quality, coverage), and control flags (e.g., `stop`, `iteration`).
- **Nodes (LangGraph Steps)**:
  - **analyze_question**: Uses AzureChatOpenAI with a prompt (`QUESTION_ANALYSIS_PROMPT`) to score complexity (1-10), classify type (e.g., factual, analytical), estimate hops, and identify key aspects/evidence types.
  - **enhanced_plan**: Generates 3-5 prioritized sub-questions using `MULTI_QUERY_PLANNING_PROMPT`, targeting gaps from previous assessments.
  - **parallel_retrieve**: Executes parallel searches using multiple retrievers (semantic MMR, similarity) from PGVector. Fuses results, deduplicates, and merges with existing evidence.
  - **advanced_assess**: Scores context using `CONTEXT_ASSESSMENT_PROMPT` (quality, coverage, evidence strength) and detects gaps/contradictions.
  - **intelligent_decide**: Uses `DECISION_MAKING_PROMPT` to compute a continue probability based on scores, iterations, and recent improvements. Stops if quality thresholds are met or max iterations reached.
  - **enhanced_synthesis**: Generates the answer using `ENHANCED_SYNTHESIS_PROMPT`, incorporating quality scores and formatted evidence. Specialized for trade finance (e.g., outputs discrepancy tables in markdown/CSV).
  - **advanced_verify**: Verifies using `ADVANCED_VERIFICATION_PROMPT`, scoring factual grounding, consistency, etc., and flags issues.
- **Retrieval & Storage**:
  - Embeddings: Azure OpenAI Embeddings.
  - Vector Store: PGVector (PostgreSQL with vector extension) for storing chunked PDF documents.
  - Strategies: Hybrid (semantic + similarity) with deduplication by source/page.
- **Prompts & Specialization**:
  - Prompts from `multi_hops_prompts.py` and `prompts.py` ensure trade finance focus (e.g., discrepancy checklists, UCP 600 rules).
  - Outputs include tabular structures (e.g., defect checklists) and CSV exports for compliance reports.
- **Frontend**: Streamlit app (`app.py`) with real-time node logging, answer display, source citations, and metrics (confidence, sources count).
- **Utilities**: JSON parsing, document formatting, thread pooling for parallelism.

This architecture ensures **transparency** (step-by-step prints), **efficiency** (early stopping via decision node), and **accuracy** (multi-hop retrieval + verification). It's stateful (via MemorySaver) for threaded executions.

## Prerequisites

- Python 3.12+
- Azure OpenAI API keys (endpoint, API key, deployments for chat/embeddings).
- PostgreSQL database with PGVector extension (via Docker).
- PDFs for ingestion (place in a `docs/` folder or configure `DOCS_DIR`).
- `.env` file with variables (see `.env.example` in repo).

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/enhanced-rag-trade-finance.git
cd enhanced-rag-trade-finance
```

### 2. Set Up Virtual Environment with UV

Use [uv](https://github.com/astral-sh/uv) for fast virtual environment management and dependency installation.

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual env
uv venv

# Activate (Unix/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

*(Create a `requirements.txt` in your repo with dependencies like: langchain, langchain-openai, langchain-postgres, langgraph, streamlit, python-dotenv, tqdm, pikepdf, pypdf, pdfminer.six, etc.)*

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in:

```
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your_embeddings_deployment
PGVECTOR_DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/your_db
COLLECTION_NAME=trade_finance_docs
DOCS_DIR=path/to/your/pdfs
PDF_PASSWORD=optional_pdf_password
```

### 5. Set Up PostgreSQL with PGVector (Using Docker)

The system uses PGVector for vector storage. Run a PostgreSQL container with the PGVector extension.

```bash
# Pull and run PostgreSQL with PGVector
%docker run --name pgvector-container -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16
# Verify it's running
docker ps
```

Update `PGVECTOR_DATABASE_URL` in `.env` if needed.

### 6. Ingest PDFs (Data Ingestion)

Ingest trade finance PDFs into the vector store.

```bash
# Run ingestion script
python ingest_pdfs.py
```

- This loads PDFs from `DOCS_DIR`, sanitizes them (using pikepdf if needed), splits into chunks, embeds with Azure OpenAI, and upserts to PGVector.
- Skipped files are logged; ensure PDFs are readable.

## Running the Application

### 1. Start the Streamlit App

```bash
streamlit run app.py
```

- Open in browser (usually http://localhost:8501).
- Enter a question (e.g., "What are the key discrepancies in a Letter of Credit under UCP 600?").
- Configure max/min hops and recursion limit.
- Click "Run RAG" to process. View real-time node logs, final answer, sources, and metrics.

### 2. Example Usage

- Question: "Analyze discrepancies in MT700 for import LC."
- Output: Synthesized answer with discrepancy tables, CSV export confirmation, sources cited.

## Contributing

Contributions welcome! Fork the repo, create a branch, and submit a PR. Follow PEP8 style.

## License

MIT License. See [LICENSE](LICENSE) for details.
