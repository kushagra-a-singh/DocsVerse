# DocsVerse: Document Research & Theme Identification Chatbot

## Overview
This project is an interactive web-based application that allows users to upload documents, chat with an AI assistant to extract information from those documents, and identify common themes across the document set. It provides a user interface for managing uploaded documents and viewing chat interactions with relevant citations.

## Features

### 1. Document Management and Upload
- **Document Upload:** Users can upload multiple documents in PDF format.
- **Document Listing:** An intuitive interface to view all uploaded documents, including their status and upload date.
- **Document Deletion:** Users can delete individual documents.
- **Knowledge Base Creation:** Uploaded documents are processed and stored to create a knowledge base for the AI assistant.

### 2. AI Chat and Query Processing
- **Natural Language Queries:** Users can ask questions about the uploaded documents using natural language.
- **Contextual Responses:** The AI assistant processes queries against selected documents to provide relevant answers.
- **Citations:** Responses include citations indicating the source documents.

### 3. Theme Identification
- **Theme Analysis:** The application can analyze uploaded documents to identify common themes.
- **Theme Listing:** Identified themes are listed on a dedicated Themes page.

## Technical Stack

### Backend
- Python with FastAPI: Provides a fast, modern framework for the API.
- SQLAlchemy: ORM for interacting with the database (SQLite for local development).
- ChromaDB: Vector database used for storing document embeddings and performing semantic search.
- AI Language Models: Integrates with external LLM services (eg. Gemini) for processing queries and identifying themes.
- Document Processing Libraries: (eg. for text extraction, chunking).

### Frontend
- React.js: JavaScript library for building the user interface.
- Material UI: React component library for styling and UI elements.
- React Query: For data fetching, caching and state management.
- Vite: Fast frontend build tool.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 14+ (or higher)
- Access to a large language model API

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kushagra-a-singh/DocsVerse.git
cd DocsVerse/DocsVerse.git
cd DocsVerse
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate # On windows
# source venv/bin/activate # On macOS/Linux
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the `./backend/app/` directory.
```bash
#example .env content
APP_NAME=Document Research & Theme Identification Chatbot
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

HOST=0.0.0.0
PORT=8000

UPLOAD_DIR=./data/uploads
PROCESSED_DIR=./data/processed
MAX_UPLOAD_SIZE=10485760

VECTOR_DB_IMPL=duckdb+parquet
VECTOR_DB_PERSIST_DIR=./data/vectordb
VECTOR_DB_COLLECTION=documents
VECTOR_DB_EMBEDDING_FUNCTION=sentence_transformer
VECTOR_DB_MODEL_NAME=all-MiniLM-L6-v2
VECTOR_DB_CHUNK_SIZE=1000
VECTOR_DB_CHUNK_OVERLAP=200
VECTOR_DB_SEARCH_LIMIT=20

OCR_ENABLED=True
OCR_USE_ANGLE_CLS=True
OCR_LANGUAGE=en
OCR_USE_GPU=False

LLM_PROVIDER=google
HF_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MAX_TOKENS=512
LLM_TEMPERATURE=0.1
HF_HOME=./models/huggingface
TRANSFORMERS_CACHE=./models/huggingface

EMBEDDING_FUNCTION=sentence_transformer
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
MODEL_CACHE_DIR=./models
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
GOOGLE_MODEL=gemini-2.0-flash
```
Replace `"YOUR_GOOGLE_API_KEY"` with your actual API key.

4. Run the backend server:
```bash
cd backend
.\venv\Scripts\activate #on windows if not already active
# source venv/bin/activate #on macOS/Linux if not already active
uvicorn app.main:app --reload
```
The backend should start and run on `http://127.0.0.1:8000` by default.

5. Set up the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Usage

1.  Access the application at `http://localhost:5173/` (or the port shown by the Vite development server).
2.  Navigate to the Documents page to upload documents.
3.  Wait for documents to be processed (indicated by the status in the table).
4.  Go to the Chat page to select documents and interact with the AI assistant.
5.  Enter your natural language queries in the chat input field.
6.  View the AI's responses, which may include citations from the selected documents.
7.  Explore the Themes page to see the identified themes across your documents.

## Project Structure

```
DocsVerse/ 
├── backend/
│ ├── app/ 
│ │ ├── api/ #api endpoints for document, query and theme
│ │ ├── database/
│ │ ├── models/ #pydantic and SQLAlchemy models
│ │ ├── services/ #service integrations (LLM, vector store, document processing, theme identification)
│ │ ├── main.py 
│ │ └── config.py 
│ ├── data/ 
│ └── requirements.txt 
├── frontend/
│ ├── public/ 
│ ├── src/ 
│ │ ├── api/ 
│ │ ├── components/ 
│ │ ├── pages/ 
│ │ ├── assets/ 
│ │ └── main.jsx 
│ ├── index.html 
│ ├── package.json 
│ └── vite.config.js 
├── .gitignore 
├── README.md 
```

## Project Status and Future Improvements

The project currently implements the core functionalities of document upload, storage, retrieval, chat interaction with citations and basic theme identification and listing.

Potential future improvements include:
-   **Enhanced Theme Integration:** Fully integrating the theme selection functionality on the chat page to filter or guide conversations.
-   **More Granular Citations:** Implementing paragraph or sentence-level citations in the chat responses.
-   **OCR Implementation:** Adding support for processing scanned image documents.
-   **Improved Theme Analysis:** Further refining the theme identification process for more accurate and comprehensive results.
-   **Visualizations:** Adding visual representations for themes and their connections to documents.
-   **Deployment:** Setting up deployment on cloud platforms for broader access.
