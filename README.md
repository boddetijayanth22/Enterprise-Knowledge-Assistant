<div align="center">

# 🚀 Enterprise Knowledge Assistant

### Production-inspired Retrieval-Augmented Generation (RAG) Application

Build intelligent document assistants powered by **Semantic Search**, **Vector Embeddings**, and **Large Language Models**.

---

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?style=for-the-badge)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</div>

---

<p align="center">

<img src="C:\Users\bodde\OneDrive\Desktop\gitbanner.png" width="100%">

</p>

---

## 📖 Overview

**Enterprise Knowledge Assistant** is a production-inspired **Retrieval-Augmented Generation (RAG)** application that enables users to upload, organize, and query PDF documents using natural language.

Instead of relying solely on the knowledge stored inside a Large Language Model, the application retrieves relevant information from uploaded documents before generating a response. This approach produces grounded, context-aware answers based on the user's own knowledge base.

The project demonstrates the practical implementation of a complete RAG pipeline using modern AI technologies, including semantic chunking, dense vector embeddings, vector search, and Large Language Models.

The application is built with a modular architecture consisting of:

- ⚡ FastAPI Backend
- 🎨 Streamlit Frontend
- 🗄️ Qdrant Vector Database
- 🧠 Sentence Transformers Embedding Model
- 🤖 Google Gemini LLM

The primary objective of this project is to understand how enterprise document intelligence systems are designed while following clean architecture and modular software engineering principles.

---

# 🎯 Project Goals

This project was developed to gain hands-on experience with the core components of Retrieval-Augmented Generation (RAG) by building an end-to-end document intelligence application from scratch.

The primary goals include:

- Build a complete Retrieval-Augmented Generation pipeline
- Understand semantic retrieval using dense embeddings
- Learn vector databases through Qdrant
- Integrate Google Gemini for grounded response generation
- Design a modular FastAPI backend
- Develop an interactive Streamlit frontend
- Implement metadata-based document retrieval
- Prevent duplicate indexing using SHA-256 hashing
- Establish a strong foundation for future versions involving Hybrid Search, Re-ranking, LangChain, LangGraph, MCP, and Agentic AI

---

# 📑 Table of Contents

- [Overview](#-overview)
- [Project Goals](#-project-goals)
- [Application Preview](#-application-preview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [RAG Workflow](#-rag-workflow)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [REST API](#-rest-api)
- [Version 1 Progress](#-version-1-progress)
- [Project Roadmap](#-project-roadmap)
- [Challenges Solved](#-challenges-solved)
- [Learning Outcomes](#-learning-outcomes)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

# 📸 Application Preview

The following screenshots demonstrate the current capabilities of the application.

> **Replace the placeholders below with actual screenshots after capturing your application.**

---

## 🏠 Home Dashboard

<p align="center">
<img src=".github/assets/dashboard.png" width="90%">
</p>

The dashboard provides an overview of the knowledge base, including indexed documents, vector storage statistics, and quick access to the application's core features.

---

## 📚 Knowledge Base

<p align="center">
<img src=".github/assets/knowledge-base.png" width="90%">
</p>

The Knowledge Base allows users to:

- Upload PDF documents
- Search indexed documents
- Select documents for retrieval
- Delete documents
- Refresh the document list

---

## 💬 Chat Interface

<p align="center">
<img src=".github/assets/chat.png" width="90%">
</p>

The chat interface enables users to ask questions in natural language. The application retrieves relevant document chunks from the selected documents and generates grounded responses using Google Gemini.

---

# ✨ Features

The current implementation (Version 1) includes the following capabilities.

---

## 📄 Document Management

- Upload one or multiple PDF documents
- Automatic PDF parsing
- Semantic chunk generation
- SHA-256 based duplicate document detection
- Delete indexed documents
- Search documents by filename
- Refresh the Knowledge Base
- Metadata storage for each indexed document

---

## 🧠 Intelligent Retrieval

- Semantic search using dense vector embeddings
- Metadata-based document filtering
- Multi-document retrieval
- Configurable Top-K retrieval
- Context construction for LLM prompting
- Source-aware retrieval pipeline

---

## 🤖 AI-Powered Question Answering

- Natural language querying
- Context-aware answer generation
- Google Gemini integration
- Source citations included with responses
- Retrieval-Augmented Generation (RAG) pipeline

---

## 📊 Knowledge Base Management

- View uploaded documents
- Track indexed content
- Organize document collection
- Select specific documents for querying
- Remove obsolete documents

---

## ⚙️ Backend

Built using **FastAPI**, providing:

- RESTful API architecture
- Modular service layer
- Schema validation using Pydantic
- Centralized configuration
- Error handling
- Logging support
- Scalable project organization

---

## 🎨 Frontend

Built using **Streamlit**, featuring:

- Clean and interactive interface
- Modular UI components
- Sidebar-based navigation
- PDF upload workflow
- Knowledge Base management
- Real-time chat experience

---

## 🔒 Data Integrity

To improve reliability and maintain data consistency, the application includes:

- SHA-256 hashing to prevent duplicate uploads
- Metadata-based document tracking
- Vector persistence using Qdrant
- Consistent document indexing workflow

---

# 📌 Current Version

This repository currently represents **Version 1** of the Enterprise Knowledge Assistant.

### ✅ Implemented

- PDF Upload
- PDF Parsing
- Semantic Chunking
- Dense Vector Embeddings
- Qdrant Integration
- Semantic Retrieval
- Google Gemini Integration
- Source Citations
- Metadata Filtering
- Duplicate Detection
- Knowledge Base Management
- Document Search
- Document Deletion
- FastAPI REST API
- Streamlit Frontend
- Modular Project Architecture

> **Version 2 features such as enhanced chat management, UI improvements, and dashboard enhancements are currently under development and are intentionally not listed as completed features.**

---

# 🏗️ System Architecture

The Enterprise Knowledge Assistant follows a modular Retrieval-Augmented Generation (RAG) architecture, separating document ingestion, retrieval, and response generation into independent components.

```text
                           ┌───────────────────────┐
                           │        User           │
                           └───────────┬───────────┘
                                       │
                                       ▼
                           ┌───────────────────────┐
                           │   Streamlit Frontend  │
                           └───────────┬───────────┘
                                       │
                               REST API Calls
                                       │
                                       ▼
                           ┌───────────────────────┐
                           │    FastAPI Backend    │
                           └───────┬───────┬───────┘
                                   │       │
                  Document Upload   │       │ User Query
                                   │       │
                                   ▼       ▼
                      ┌───────────────────────┐
                      │    PDF Loader         │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │ Semantic Chunking     │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │ Embedding Generation  │
                      │ (Sentence Transformer)│
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │   Qdrant Vector DB    │
                      └───────────┬───────────┘
                                  │
                          Semantic Retrieval
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  Prompt Construction  │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │   Google Gemini LLM   │
                      └───────────┬───────────┘
                                  │
                                  ▼
                           Grounded Response
                                  │
                                  ▼
                                User
```

---

# 🔄 Retrieval-Augmented Generation (RAG) Workflow

The application follows two independent workflows: **Document Ingestion** and **Question Answering**.

## 📄 Document Ingestion Pipeline

Whenever a user uploads a PDF, the following operations are performed:

```text
Upload PDF
      │
      ▼
Load PDF
      │
      ▼
Extract Text
      │
      ▼
Semantic Chunking
      │
      ▼
Generate Dense Embeddings
      │
      ▼
Store Vectors in Qdrant
      │
      ▼
Store Metadata
```

During indexing, metadata such as the filename, page number, chunk text, and SHA-256 document hash are stored alongside each vector. This enables duplicate detection and metadata-based retrieval.

---

## 💬 Question Answering Pipeline

When a user submits a question, the application performs the following steps:

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Search Qdrant
      │
      ▼
Retrieve Top-K Chunks
      │
      ▼
Apply Metadata Filtering
      │
      ▼
Construct Prompt
      │
      ▼
Generate Response with Gemini
      │
      ▼
Return Answer + Source Citations
```

This Retrieval-Augmented Generation workflow ensures that responses are grounded in the uploaded documents rather than relying solely on the language model's pre-trained knowledge.

---

# 🛠️ Technology Stack

The project combines modern AI frameworks with scalable backend technologies.

| Category | Technology |
|-----------|------------|
| **Programming Language** | Python 3.13 |
| **Backend Framework** | FastAPI |
| **Frontend Framework** | Streamlit |
| **Large Language Model** | Google Gemini |
| **Embedding Model** | BAAI/bge-small-en-v1.5 |
| **Vector Database** | Qdrant |
| **Document Loader** | PyPDF |
| **Data Validation** | Pydantic |
| **HTTP Client** | Requests |
| **Environment Management** | python-dotenv |
| **Containerization** | Docker |
| **Development Environment** | VS Code |

---

# 🏛️ Design Decisions

Several architectural decisions were made to improve maintainability, scalability, and retrieval quality.

### Why FastAPI?

- High-performance asynchronous backend
- Automatic OpenAPI documentation
- Clean API routing
- Modular service architecture

---

### Why Streamlit?

- Rapid UI development
- Interactive interface
- Simple integration with FastAPI
- Ideal for AI application prototyping

---

### Why Qdrant?

- High-performance vector similarity search
- Metadata filtering support
- Efficient vector storage
- Scalable retrieval architecture

---

### Why Sentence Transformers?

The project uses **BAAI/bge-small-en-v1.5**, providing:

- High-quality semantic embeddings
- Fast inference
- Strong retrieval performance
- Compact model size

---

### Why Google Gemini?

Google Gemini was selected because it provides:

- Strong reasoning capabilities
- Natural language generation
- Long-context support
- Effective response generation for Retrieval-Augmented Generation pipelines

---
